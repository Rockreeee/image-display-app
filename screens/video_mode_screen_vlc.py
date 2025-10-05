import tkinter as tk
import screens.video_mode_setting_screen as video_mode_setting_screen
import utils.settings_manager as settings_manager
import utils.fetch_weather_from_tenkijp as fetch_weather_from_tenkijp
import utils.music_player as music_player
import os
import random
from datetime import datetime
import threading
from tkinter import messagebox
from time import strftime, localtime, time
from PIL import Image, ImageEnhance, ImageTk
import utils.fetch_train_schedule as fetch_train_schedule
import json
import vlc

# start: カスタム設定
# 日付UIとディスプレイ距離
MARGIN_ABOVE_CLOCK = 50
# 文字の大きさ
DATE_FONT_SIZE = 28
TIME_FONT_SIZE = 70
WEATHER_FONT_SIZE = 20
# 画像の表示領域に対して何割表示するか 0~1.0
CONSTANT_MARGIN = 0.7
# 明るくなる時間
TIME_BRIGHTNESS_HOUR = 7
TIME_BRIGHTNESS_MINUTE = 0
# 暗くなる時間
TIME_DARKNESS_HOUR = 21
TIME_DARKNESS_MINUTE = 0
# 音楽が止まるまでの時間（分）
MUSIC_STOP_MINUTES = 10
# 列車時刻表ファイルパス
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
TRAIN_SCHEDULE_FILE_PATH_A = os.path.join(BASE_DIR, "data", "train_schedule_for_nagoya.json")
TRAIN_SCHEDULE_FILE_PATH_B = os.path.join(BASE_DIR, "data", "train_schedule_for_toyota.json")
DESTINATION_A = "For Nagoya"
DESTINATION_B = "For Toyota"
# end: カスタム設定

class VideoModeScreenVLC:
    def __init__(self):
        self.image_brightness = 1.0
        self.label_brightness = 1.0
        self.volume = 1.0
        self.current_video_index = 0
        self.is_playing = False
        self.last_video_change_time = time()
        
        # データ更新用のタイマー
        self.last_weather_update = 0
        self.last_train_update = 0
        self.weather_data = None
        self.train_data = None

        # 設定変数の初期化
        self.initialize_settings()
        
        # 初期データの取得
        self.update_weather_data()
        self.update_train_data()
        
        self.create_widgets()

    # 設定をロードし、各変数に設定
    def initialize_settings(self):
        settings = settings_manager.load_settings()
        self.video_path = settings.get('video_path')
        self.interval = int(settings.get('interval'))
        self.automatic_brightness = settings.get('automatic_brightness')
        self.show_time = settings.get('show_time')
        self.show_weather = settings.get('show_weather')
        self.show_train_schedule = settings.get('show_train_schedule')
        self.sound_path = settings.get('sound_path')
        self.sound_mode = settings.get('sound_mode')
        self.preserve_quality = settings.get('preserve_quality', True)
        self.play_video_audio = settings.get('play_video_audio', False)

        self.video_files = [f for f in os.listdir(self.video_path) if f.endswith(('.mp4', '.avi', '.mov', '.MOV', '.mkv'))]

    # UI作成
    def create_widgets(self):
        # メインウィンドウ作成
        self.root = tk.Tk()
        self.root.title("Video Display App (VLC)")
        
        # 全画面表示
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        
        # VLCインスタンス作成
        self.instance = vlc.Instance(['--no-xlib', '--quiet', '--no-video-title-show'])
        self.player = self.instance.media_player_new()
        
        # 動画再生開始
        self.play_random_video()
        
        # 自動明るさ調整
        if self.automatic_brightness:
            self.automatic_brightness_adjustment()

        # 音楽再生
        if self.sound_path != "":
            if self.sound_mode == "1":
                self.play_sound(self.sound_path)
            elif self.sound_mode == "2":
                self.automatic_sound_booking()
        
        # キーバインド設定
        self.setup_keybindings()
        
        # 定期的な更新処理
        self.update_display()
        
        # メインループ開始
        self.root.mainloop()

    def play_random_video(self):
        """ランダムな動画を再生"""
        if not self.video_files:
            print("動画ファイルが見つかりません")
            return
            
        random_file = random.choice(self.video_files)
        video_path = os.path.join(self.video_path, random_file)
        self.current_video_path = video_path
        
        # メディア作成（ループ再生オプション付き）
        media = self.instance.media_new(video_path, 'input-repeat=1')
        self.player.set_media(media)
        
        # 音声設定
        if not self.play_video_audio:
            self.player.audio_set_volume(0)
        
        # 再生開始
        self.player.play()
        
        # 動画ウィンドウをTkinterウィンドウに埋め込み
        if os.name == 'nt':  # Windows
            self.player.set_hwnd(self.root.winfo_id())
        else:  # Linux/Mac
            self.player.set_xwindow(self.root.winfo_id())
        
        print(f"動画再生開始: {random_file}")

    def setup_keybindings(self):
        """キーバインド設定"""
        self.root.bind('<Escape>', lambda e: self.close_window())
        self.root.bind('<q>', lambda e: self.close_window())
        self.root.bind('<f>', lambda e: self.toggle_fullscreen())
        self.root.bind('<h>', lambda e: self.toggle_cursor())
        self.root.bind('<v>', lambda e: self.set_volume())
        self.root.bind('<m>', lambda e: self.sound_mute())
        self.root.bind('<i>', lambda e: self.image_brightness_adjustment())
        self.root.bind('<space>', lambda e: self.next_video())

    def update_display(self):
        """定期的な更新処理"""
        current_time = time()
        
        # interval経過したかチェック
        if current_time - self.last_video_change_time >= self.interval:
            self.last_video_change_time = current_time
            self.next_video()
        
        # 音楽停止のタイミングチェック
        if hasattr(self, 'music_stop_time') and current_time >= self.music_stop_time:
            if hasattr(self, 'player_music'):
                self.player_music.stop_music()
            delattr(self, 'music_stop_time')
        
        # 音楽開始のタイミングチェック
        if hasattr(self, 'next_music_start_time') and current_time >= self.next_music_start_time:
            self.automatic_sound_booking()
            delattr(self, 'next_music_start_time')
        
        # データ更新のタイミング制御（1分ごと）
        if current_time - self.last_weather_update >= 60:
            self.update_weather_data()
            self.last_weather_update = current_time
        
        if current_time - self.last_train_update >= 300:  # 5分ごと
            self.update_train_data()
            self.last_train_update = current_time
        
        # 100ms後に再度実行
        self.root.after(100, self.update_display)

    # データ更新関数
    def update_weather_data(self):
        try:
            self.weather_data = fetch_weather_from_tenkijp.get_precipitation_forecast()
        except Exception as e:
            print(f"天気データの更新でエラー: {e}")
    
    def update_train_data(self):
        try:
            with open(TRAIN_SCHEDULE_FILE_PATH_A, 'r') as file:
                train_schedule_dataA = json.load(file)
            with open(TRAIN_SCHEDULE_FILE_PATH_B, 'r') as file:
                train_schedule_dataB = json.load(file)
            
            next_trainsA = fetch_train_schedule.get_next_trains(train_schedule_dataA)
            next_trainsB = fetch_train_schedule.get_next_trains(train_schedule_dataB)
            
            self.train_data = {
                'A': next_trainsA,
                'B': next_trainsB
            }
        except Exception as e:
            print(f"列車時刻表データの更新でエラー: {e}")

    # キーバインドのための関数一覧
    def close_window(self):
        print("停止します")
        # 音楽停止
        if hasattr(self, 'player_music'):
            self.player_music.stop_music()
        # 動画停止
        self.player.stop()
        self.root.destroy()
        video_mode_setting_screen.create_screen()

    def image_brightness_adjustment(self):
        self.image_brightness -= 0.2
        if self.image_brightness < 0:
            self.image_brightness = 1

    def toggle_fullscreen(self):
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))

    def toggle_cursor(self):
        self.root.config(cursor="" if self.root.cget("cursor") == "none" else "none")

    def set_volume(self):
        if not hasattr(self, 'player_music'):
            print("プレイヤーが定義されていません")
            return
        self.volume = max(0.1, self.volume - 0.2) if self.volume >= 0.1 else 1.0
        print(f"音量を {self.volume} に変更しました")
        self.player_music.set_volume(self.volume)

    def sound_mute(self):
        if not hasattr(self, 'player_music'):
            print("プレイヤーが定義されていません")
            return
        self.player_music.sound_mute()

    def next_video(self):
        self.play_random_video()

    def automatic_brightness_adjustment(self):
        now = datetime.now().time()
        
        if now >= datetime.strptime("09:00", "%H:%M").time() and now < datetime.strptime("17:00", "%H:%M").time():
            # 昼の時間帯は明るさを1.0に設定
            self.image_brightness = 1.0
            print("今は昼間（09:00〜17:00）です。")
        
        elif now >= datetime.strptime("21:00", "%H:%M").time() or now < datetime.strptime("05:00", "%H:%M").time():
            # 夜の時間帯は明るさを0.2に設定
            self.image_brightness = 0.2
            print("今は夜間（21:00〜05:00）です。")
        
        else:
            # 変化する時間帯（05:00 - 09:00、17:00 - 21:00）は徐々に変化させる
            if now >= datetime.strptime("05:00", "%H:%M").time() and now < datetime.strptime("09:00", "%H:%M").time():
                # 朝、夜から昼にかけて徐々に明るくする
                hours_since_6am = (datetime.combine(datetime.today(), now) - datetime.strptime("05:00", "%H:%M")).seconds / 3600
                self.image_brightness = 0.2 + (0.8 * (hours_since_6am / 4))
                print(f"今は朝（05:00〜09:00）です。徐々に明るくしています。")

            elif now >= datetime.strptime("17:00", "%H:%M").time() and now < datetime.strptime("21:00", "%H:%M").time():
                # 夕方、昼から夜にかけて徐々に暗くする
                hours_since_5pm = (datetime.combine(datetime.today(), now) - datetime.strptime("17:00", "%H:%M")).seconds / 3600
                self.image_brightness = 1.0 - (0.8 * (hours_since_5pm / 4))
                print(f"今は夕方（17:00〜21:00）です。徐々に暗くしています。")

    # 特定の時間までの残り時間を計算
    def calculate_time_next_trigger(self, target_hour, target_minute):
        # 現在の時刻を取得
        current_time = datetime.now()

        # 次に発動させたい時間を計算
        target_time = current_time.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

        # 現在の時刻から次の発動までの時間を計算
        delta_time = target_time - current_time
        total_seconds = delta_time.total_seconds()
        return int(total_seconds)

    # 音楽再生
    def play_sound(self, path):
        self.player_music = music_player.MusicPlayer(path)

        # play_music_loopを別スレッドで実行
        self.music_thread = threading.Thread(target=self.player_music.play_music)
        self.music_thread.start()

    # 自動音予約
    def automatic_sound_booking(self):
        # 初回起動時ではない時
        if hasattr(self, 'player_music'):
            # 音楽を再生
            self.player_music = music_player.MusicPlayer(self.sound_path)
            self.music_thread = threading.Thread(target=self.player_music.play_music)
            self.music_thread.start()

            # 停止予約（時間ベースで管理）
            self.music_stop_time = time() + (MUSIC_STOP_MINUTES * 60)

        # 朝までの時間計算
        time_to_morning = self.calculate_time_next_trigger(TIME_BRIGHTNESS_HOUR, TIME_BRIGHTNESS_MINUTE)
        if time_to_morning < 1:
            time_to_morning += 86400

        # 予約
        print("音が流れるまで：", int(time_to_morning), "秒")
        self.next_music_start_time = time() + time_to_morning


def create_screen():
    try:
        VideoModeScreenVLC()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        messagebox.showerror("Error", f"動画再生エラー: {e}")
        video_mode_setting_screen.create_screen() 