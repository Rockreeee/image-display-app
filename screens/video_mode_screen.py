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
import cv2
import numpy as np

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

class VideoModeScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Display App")
        self.root.configure(background='black')
        self.image_brightness = 1.0
        self.label_brightness = 1.0
        self.volume = 1.0
        self.current_video_index = 0
        self.video_cap = None
        self.is_playing = False

        # 設定変数の初期化
        self.initialize_settings()
        self.set_keybinding()
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
        self.preserve_quality = settings.get('preserve_quality', True)  # 画質保持の設定
        self.play_video_audio = settings.get('play_video_audio', False)  # 動画音声再生の設定

        self.video_files = [f for f in os.listdir(self.video_path) if f.endswith(('.mp4', '.avi', '.mov', '.MOV', '.mkv'))]

    # キーバインド一覧
    def set_keybinding(self):
        # 終了する時のキーバインド
        self.root.bind("<Escape>", self.close_window)
        self.root.bind("<q>", self.close_window)

        # 文字の明るさを調整するキーバインド
        self.root.bind("<b>", self.label_brightness_adjustment)

        # 動画の明るさを調整するキーバインド
        self.root.bind("<i>", self.video_brightness_adjustment)

        # キーイベントをバインドしてフルスクリーン表示の切り替えを有効にする
        self.root.bind("<f>", self.toggle_fullscreen)

        # キーイベントをバインドしてカーソルを表示きりかえ
        self.root.bind("<h>", self.toggle_cursor)

        # キーイベントをバインドして音量の調整を有効にする
        self.root.bind("<v>", self.set_volume)

        # キーイベントをバインドしてミュートの切り替えを有効にする
        self.root.bind("<m>", self.sound_mute)
            
        # キーイベントをバインドして動画変更を有効にする
        self.root.bind("<space>", self.next_video)

    # start: キーバインドのための関数一覧
    # 終了する時の関数
    def close_window(self, event):
        print("停止します")
        # 音楽停止
        if hasattr(self, 'player'):
            self.player.stop_music()
        # 動画停止
        if self.video_cap:
            self.video_cap.release()
        self.cancel_root_after()
        self.root.destroy()
        video_mode_setting_screen.create_screen()

    # 明るさを調整する関数
    def label_brightness_adjustment(self, event):
        if not hasattr(self, 'label_brightness'):
            print("文字が定義されていません")
            return
        else:
            self.label_brightness -= 0.2
            if self.label_brightness < 0:
                self.label_brightness = 1
            
            # RGB値を16進数に変換
            brightness = int(255 * self.label_brightness)
            color = f"#{brightness:02x}{brightness:02x}{brightness:02x}"
            
            # ラベルの色を更新
            if hasattr(self, 'date_label'):
                self.canvas.itemconfig(self.date_label, fill=color)
            if hasattr(self, 'time_label'):
                self.canvas.itemconfig(self.time_label, fill=color)
            if hasattr(self, 'weather_label'):
                self.canvas.itemconfig(self.weather_label, fill=color)
            if hasattr(self, 'train_schedule_label'):
                self.canvas.itemconfig(self.train_schedule_label, fill=color)

    # 明るさを調整する関数
    def video_brightness_adjustment(self, event):
        self.image_brightness -= 0.2
        if self.image_brightness < 0:
            self.image_brightness = 1

    # ウィンドウの大きさを調整
    def toggle_fullscreen(self, event):
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    # カーソルを隠す関数
    def toggle_cursor(self, event):
        cursor_state = self.root.cget("cursor")
        if cursor_state == "none":
            self.root.config(cursor="arrow") 
        else:
            self.root.config(cursor="none")

    # 音量を調整する関数
    def set_volume(self, event):
        if not hasattr(self, 'player'):
            print("プレイヤーが定義されていません")
            return
        self.volume = max(0.1, self.volume - 0.2) if self.volume >= 0.1 else 1.0
        print(f"音量を {self.volume} に変更しました")
        self.player.set_volume(self.volume)

    # ミュートにする関数
    def sound_mute(self, event):
        if not hasattr(self, 'player'):
            print("プレイヤーが定義されていません")
            return
        self.player.sound_mute()

    # 次の動画に変更
    def next_video(self, event):
        self.current_video_index = (self.current_video_index + 1) % len(self.video_files)
        self.load_video()
    # end: キーバインドのための関数一覧

    # UI作成
    def create_widgets(self):
        self.canvas = tk.Canvas(self.root, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.video_label = tk.Label(self.canvas, bg='black')
        self.canvas.create_window(0, 0, anchor="nw", window=self.video_label)

        # 時計を表示
        if self.show_time:
            self.show_clock_without_margin_widget()

        # 天気を表示
        if self.show_weather:
            self.show_weather_without_margin_widget()

        # 列車時刻表を表示
        if self.show_train_schedule:
            self.show_train_schedule_without_margin_widget()

        # 動画を表示
        self.load_video()

        # 自動明るさ調整
        if self.automatic_brightness:
            self.automatic_brightness_adjustment()

        # 音楽再生
        if self.sound_path != "":
            if self.sound_mode == "1":
                self.play_sound(self.sound_path)
            elif self.sound_mode == "2":
                self.automatic_sound_booking()

    # 動画を読み込む
    def load_video(self):
        if self.video_cap:
            self.video_cap.release()
        
        if not self.video_files:
            print("動画ファイルが見つかりません")
            return
        
        video_file = self.video_files[self.current_video_index]
        video_path = os.path.join(self.video_path, video_file)
        
        print(f"動画ファイルを読み込み中: {video_path}")
        
        self.video_cap = cv2.VideoCapture(video_path)
        if not self.video_cap.isOpened():
            print(f"動画ファイルを開けません: {video_path}")
            return
        
        # 元の動画のFPSを取得
        self.original_fps = self.video_cap.get(cv2.CAP_PROP_FPS)
        if self.original_fps <= 0:
            self.original_fps = 30.0  # デフォルト値
        
        print(f"動画FPS: {self.original_fps}")
        
        self.is_playing = True
        self.frame_count = 0
        self.start_time = time()
        self.update_video_frame()

    # 動画フレームを更新
    def update_video_frame(self):
        if not self.is_playing or not self.video_cap:
            return
        
        ret, frame = self.video_cap.read()
        if not ret:
            # 動画が終了したら最初から再生
            print("動画終了、最初から再生")
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.video_cap.read()
            if not ret:
                print("動画の読み込みに失敗")
                return
        
        # フレームをリサイズ
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 画質保持設定に応じてリサイズ方法を変更
        if self.preserve_quality:
            # 画質を保持：元の解像度を維持し、必要最小限のリサイズのみ
            height, width = frame.shape[:2]
            ratio = max(screen_width / width, screen_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            # 高品質なリサイズ（LANCZOS）
            frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            
            # 中央部分を切り取り
            start_x = (new_width - screen_width) // 2
            start_y = (new_height - screen_height) // 2
            frame = frame[start_y:start_y + screen_height, start_x:start_x + screen_width]
        else:
            # パフォーマンス優先：画面サイズに直接リサイズ
            frame = cv2.resize(frame, (screen_width, screen_height), interpolation=cv2.INTER_LINEAR)
        
        # BGRからRGBに変換
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 明るさ調整
        frame = cv2.convertScaleAbs(frame, alpha=self.image_brightness, beta=0)
        
        # PIL Imageに変換
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image)
        
        # ラベルに表示
        self.video_label.configure(image=photo)
        self.video_label.image = photo  # 参照を保持
        
        # フレームカウント更新
        if hasattr(self, 'frame_count'):
            self.frame_count += 1
        else:
            self.frame_count = 1
        
        # デバッグ情報（100フレームごと）
        if self.frame_count % 100 == 0:
            current_time = time()
            if hasattr(self, 'start_time'):
                actual_fps = 100 / (current_time - self.start_time)
                print(f"実際のFPS: {actual_fps:.2f}, 目標FPS: {self.original_fps:.2f}")
            self.start_time = current_time
        
        # 次のフレームを元のFPSに合わせてスケジュール
        frame_interval_ms = int(1000 / self.original_fps)
        self.root.after(frame_interval_ms, self.update_video_frame)

    # 時計のUI作成
    def show_clock_without_margin_widget(self):
        # ラベルを作成
        self.date_label = self.canvas.create_text(self.root.winfo_screenwidth() // 3.5, self.root.winfo_screenheight() - 300, font=('calibri', DATE_FONT_SIZE, 'bold'), fill="white")
        self.time_label = self.canvas.create_text(self.root.winfo_screenwidth() // 3.5, self.root.winfo_screenheight() - 150, font=('calibri', TIME_FONT_SIZE, 'bold'), fill="white")

        # 日付と曜日、時間を更新する関数を初回呼び出し
        self.update_time()

    # 時計のUI更新
    def update_time(self):
        # 現在の時間と日付を取得
        current_time = strftime('%H:%M:%S')
        current_date = strftime('%Y-%m-%d %A', localtime())

        # ラベルのテキストを更新
        self.canvas.itemconfig(self.time_label, text=current_time)
        self.canvas.itemconfig(self.date_label, text=current_date)

        # 次の更新まで待機
        self.root_after_id_time = self.root.after(1000, self.update_time)

    # 天気のUI作成
    def show_weather_without_margin_widget(self):
        # 天気を表示するラベルを作成し、配置
        self.weather_label = self.canvas.create_text(self.root.winfo_screenwidth() // 1.33, self.root.winfo_screenheight() - 200, font=('calibri', WEATHER_FONT_SIZE, 'bold'), fill="white")

        # １時間ごとに天気更新
        self.update_weather()

    # 天気のUI更新
    def update_weather(self):
        # 天気データの取得
        # print("天気を更新します。")
        forecast_data = fetch_weather_from_tenkijp.get_precipitation_forecast()
        if forecast_data != None:
            forecast_text = (forecast_data["weather_data"][0]['weather_icon'] + "　" + "↑" + forecast_data["weather_data"][0]['high_temp'] + "°" + "↓" + forecast_data["weather_data"][0]['low_temp'] + "°" + "\n" 
                + "00~06" + ":" + forecast_data["today_probabilities"][0] + "%" + "　" + "06~12" + ":" + forecast_data["today_probabilities"][1] + "%" + "\n"
                + "12~18" + ":" + forecast_data["today_probabilities"][2] + "%" + "　" + "18~24" + ":" + forecast_data["today_probabilities"][3] + "%" + "\n"
                + "\n"
                + forecast_data["weather_data"][1]['weekday'] + " " + forecast_data["weather_data"][2]['weekday'] + " " + forecast_data["weather_data"][3]['weekday'] + " " + forecast_data["weather_data"][4]['weekday'] + " " + forecast_data["weather_data"][5]['weekday'] + " " + forecast_data["weather_data"][6]['weekday'] + "\n"
                + forecast_data["weather_data"][1]['weather_icon'] + "     " + forecast_data["weather_data"][2]['weather_icon'] + "     " + forecast_data["weather_data"][3]['weather_icon'] + "     " + forecast_data["weather_data"][4]['weather_icon'] + "     " + forecast_data["weather_data"][5]['weather_icon'] + "     " + forecast_data["weather_data"][6]['weather_icon'])

            self.canvas.itemconfig(self.weather_label, text=forecast_text, anchor="center", justify="center")

        # 次の更新まで待機
        self.root_after_id_weather = self.root.after(3600 * 1000, self.update_weather)

    # 列車時刻表のUI作成
    def show_train_schedule_without_margin_widget(self):
        # 列車時刻表を表示するラベルを作成し、配置
        self.train_schedule_label = self.canvas.create_text(self.root.winfo_screenwidth() // 1.33, self.root.winfo_screenheight() - 400, font=('calibri', WEATHER_FONT_SIZE, 'bold'), fill="white")

        # 列車時刻表のUI更新
        self.update_train_schedule()

    # 列車時刻表のUI更新
    def update_train_schedule(self):
        # 列車時刻表データの取得
        # JSONファイルを読み込む
        train_schedule_dataA = None
        train_schedule_dataB = None
        print(TRAIN_SCHEDULE_FILE_PATH_A)
        with open(TRAIN_SCHEDULE_FILE_PATH_A, 'r') as file:
            train_schedule_dataA = json.load(file)
        with open(TRAIN_SCHEDULE_FILE_PATH_B, 'r') as file:
            train_schedule_dataB = json.load(file)

        next_trainsA = fetch_train_schedule.get_next_trains(train_schedule_dataA)
        next_trainsB = fetch_train_schedule.get_next_trains(train_schedule_dataB)
        if next_trainsA != None and next_trainsB != None:
            train_schedule_text = (
                DESTINATION_A + "　" + DESTINATION_B + "\n"
                + next_trainsA[0]['time'] + "　　　" + next_trainsB[0]['time'] + "\n"
                + next_trainsA[1]['time'] + "　　　" + next_trainsB[1]['time'] + "\n"
                + next_trainsA[2]['time'] + "　　　" + next_trainsB[2]['time'] + "\n")
            
            self.canvas.itemconfig(self.train_schedule_label, text=train_schedule_text, anchor="center", justify="center")

        # 次の更新まで待機（5分）
        self.root_after_id_train_schedule = self.root.after(300 * 1000, self.update_train_schedule)
    
    def automatic_brightness_adjustment(self):
        now = datetime.now().time()
        
        if now >= datetime.strptime("09:00", "%H:%M").time() and now < datetime.strptime("17:00", "%H:%M").time():
            # 昼の時間帯は明るさを1.0に設定
            self.image_brightness = 1.0
            # print("今は昼間（09:00〜17:00）です。")
        
        elif now >= datetime.strptime("21:00", "%H:%M").time() or now < datetime.strptime("05:00", "%H:%M").time():
            # 夜の時間帯は明るさを0.2に設定
            self.image_brightness = 0.2
            # print("今は夜間（21:00〜05:00）です。")
        
        else:
            # 変化する時間帯（05:00 - 09:00、17:00 - 21:00）は徐々に変化させる
            if now >= datetime.strptime("05:00", "%H:%M").time() and now < datetime.strptime("09:00", "%H:%M").time():
                # 朝、夜から昼にかけて徐々に明るくする
                hours_since_6am = (datetime.combine(datetime.today(), now) - datetime.strptime("05:00", "%H:%M")).seconds / 3600
                self.image_brightness = 0.2 + (0.8 * (hours_since_6am / 4))
                # print(f"今は朝（05:00〜09:00）です。徐々に明るくしています。")

            elif now >= datetime.strptime("17:00", "%H:%M").time() and now < datetime.strptime("21:00", "%H:%M").time():
                # 夕方、昼から夜にかけて徐々に暗くする
                hours_since_5pm = (datetime.combine(datetime.today(), now) - datetime.strptime("17:00", "%H:%M")).seconds / 3600
                self.image_brightness = 1.0 - (0.8 * (hours_since_5pm / 4))
                # print(f"今は夕方（17:00〜21:00）です。徐々に暗くしています。")

        # 次の1時間後に再度明るさ調整を予約
        self.root_after_id_brightness_adjustment = self.root.after(3600 * 1000, self.automatic_brightness_adjustment)

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
        self.player = music_player.MusicPlayer(path)

        # play_music_loopを別スレッドで実行
        self.music_thread = threading.Thread(target=self.player.play_music)
        self.music_thread.start()

    # 自動音予約
    def automatic_sound_booking(self):
        # 初回起動時ではない時
        if hasattr(self, 'player'):
            # 音楽を再生
            self.player = music_player.MusicPlayer(self.sound_path)
            self.music_thread = threading.Thread(target=self.player.play_music)
            self.music_thread.start()

            # 停止予約
            self.root_after_id_sound_stop_booking = self.root.after(int(MUSIC_STOP_MINUTES * 60) * 1000, self.player.stop_music)

        # 朝までの時間計算
        time_to_morning = self.calculate_time_next_trigger(TIME_BRIGHTNESS_HOUR, TIME_BRIGHTNESS_MINUTE)
        if time_to_morning < 1:
            time_to_morning += 86400

        # 予約
        print("音が流れるまで：", int(time_to_morning), "秒")
        self.root_after_id_sound_start_booking = self.root.after(int(time_to_morning) * 1000, self.automatic_sound_booking)
    
    # 予約処理のキャンセル
    def cancel_root_after(self):
        if hasattr(self, 'root_after_id_time'):
            self.root.after_cancel(self.root_after_id_time)
        if hasattr(self, 'root_after_id_weather'):
            self.root.after_cancel(self.root_after_id_weather)
        if hasattr(self, 'root_after_id_train_schedule'):
            self.root.after_cancel(self.root_after_id_train_schedule)
        if hasattr(self, 'root_after_id_brightness_adjustment'):
            self.root.after_cancel(self.root_after_id_brightness_adjustment)
        if hasattr(self, 'root_after_id_sound_stop_booking'):
            self.root.after_cancel(self.root_after_id_sound_stop_booking)
        if hasattr(self, 'root_after_id_sound_start_booking'):
            self.root.after_cancel(self.root_after_id_sound_start_booking)


def create_screen():
    root = tk.Tk()
    try:
        VideoModeScreen(root)
        root.mainloop()  # エラーがない場合のみ実行
    except FileNotFoundError:
        # 音楽停止
        root.destroy()
        messagebox.showerror("Error", "Video file not found!")
        video_mode_setting_screen.create_screen()
