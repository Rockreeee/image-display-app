import screens.video_mode_setting_screen as video_mode_setting_screen
import utils.settings_manager as settings_manager
import utils.fetch_weather_from_tenkijp as fetch_weather_from_tenkijp
import utils.music_player as music_player
import os
import random
from datetime import datetime
import threading
from tkinter import messagebox
from time import strftime, localtime
from PIL import Image, ImageEnhance, ImageTk
import pygame
import cv2
import sys
import numpy as np

# start: カスタム設定
# 日付UIとディスプレイ距離
MARGIN_ABOVE_CLOCK = 50
# 文字の大きさ
DATE_FONT_SIZE = 30
TIME_FONT_SIZE = 75
WEATHER_FONT_SIZE = 25
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
# end: カスタム設定

class VideoModeScreen:
    def __init__(self, ):
        self.image_brightness = 1.0
        self.volume = 1.0
        self.last_video_change_time = pygame.time.get_ticks()  # 最後に動画を変更した時間

        # 設定変数の初期化
        self.initialize_settings()
        # self.set_keybinding()
        self.create_widgets()

    # 設定をロードし、各変数に設定
    def initialize_settings(self):
        settings = settings_manager.load_settings()
        self.video_path = settings.get('video_path')
        self.interval = int(settings.get('interval'))
        self.automatic_brightness = settings.get('automatic_brightness')
        self.show_time = settings.get('show_time')
        self.show_weather = settings.get('show_weather')
        self.sound_path = settings.get('sound_path')
        self.sound_mode = settings.get('sound_mode')

        self.video_files = [f for f in os.listdir(self.video_path) if f.endswith(('.mp4', '.avi', '.mov', '.MOV'))]

    # start: キーバインドのための関数一覧
    # 終了する時の関数
    def close_window(self):
        print("停止します")
        # 音楽停止
        if hasattr(self, 'player'):
            self.player.stop_music()
        # 動画停止
        self.running = False
        self.cap.release()
        pygame.quit()

        video_mode_setting_screen.create_screen()

    # 明るさを調整する関数
    def image_brightness_adjustment(self):
        self.image_brightness -= 0.2
        if self.image_brightness < 0:
            self.image_brightness = 1

    # ウィンドウの大きさを調整
    def toggle_fullscreen(self):
        # 現在のモードを取得し、全画面かどうかを切り替える
        current_mode = pygame.display.get_surface()
        is_fullscreen = current_mode.get_flags() & pygame.FULLSCREEN

        pygame.display.set_mode(
            (0, 0), 
            0 if is_fullscreen else pygame.FULLSCREEN
        )

    # カーソルを隠す関数
    def toggle_cursor(self):
        # 現在のカーソル表示状態を取得して反転
        pygame.mouse.set_visible(not pygame.mouse.get_visible())

    # 音量を調整する関数
    def set_volume(self):
        if not hasattr(self, 'player'):
            print("プレイヤーが定義されていません")
            return
        self.volume = max(0.1, self.volume - 0.2) if self.volume >= 0.1 else 1.0
        print(f"音量を {self.volume} に変更しました")
        self.player.set_volume(self.volume)

    # ミュートにする関数
    def sound_mute(self):
        if not hasattr(self, 'player'):
            print("プレイヤーが定義されていません")
            return
        self.player.sound_mute()

    def next_video(self):
        self.running = False
        self.update_video_without_margin_widget()
    # end: キーバインドのための関数一覧

    # UI作成
    def create_widgets(self):
        # マージンなし動画UIを表示
        self.update_video_without_margin_widget()

        # 自動明るさ調整
        if self.automatic_brightness:
            self.automatic_brightness_adjustment()

        # 音楽再生
        if self.sound_path != "":
            if self.sound_mode == "1":
                self.play_sound(self.sound_path)
            elif self.sound_mode == "2":
                self.automatic_sound_booking()


    # 時計のUI作成
    def show_clock_without_margin_widget(self):
        # 現在の時間と日付を取得
        current_date = strftime('%Y-%m-%d %A', localtime())
        current_time = strftime('%H:%M:%S')

        font = pygame.font.SysFont('calibri', DATE_FONT_SIZE)
        current_date_surface = font.render(current_date, True, (255, 255, 255))
        # self.screen.blit(current_date_surface, (self.video_width // 4, self.video_height - 300))
        self.screen.blit(current_date_surface, (pygame.display.Info().current_w // 4, pygame.display.Info().current_h - 300))

        font = pygame.font.SysFont('calibri', TIME_FONT_SIZE)
        current_time_surface = font.render(current_time, True, (255, 255, 255))
        # self.screen.blit(current_time_surface, (self.video_width // 4, self.video_height - 150))
        self.screen.blit(current_time_surface, (pygame.display.Info().current_w // 4, pygame.display.Info().current_h - 150))


    # 天気のUI作成
    def show_weather_with_margin_widget(self):
        # 天気を表示するラベルを作成
        self.weather_label = tk.Label(self.root, font=('calibri', WEATHER_FONT_SIZE, 'bold'), bg='white', fg='gray')

        # ラベルの高さを取得して天気ラベルを配置
        clock_height = 0
        if self.show_time:
            clock_height = self.date_label.winfo_height() + self.time_label.winfo_height()
        self.weather_label.pack(pady=(MARGIN_ABOVE_CLOCK + clock_height, 0))

        # １時間ごとに天気更新
        self.update_weather()

    # 天気のUI作成
    def show_weather_without_margin_widget(self):
        # 天気を表示するラベルを作成し、配置
        self.weather_label = self.canvas.create_text(self.root.winfo_screenwidth() // 1.3, self.root.winfo_screenheight() - 200, font=('calibri', WEATHER_FONT_SIZE, 'bold'), fill="white")

        # １時間ごとに天気更新
        self.update_weather()

    # 天気のUI更新
    def update_weather(self):
        # 天気データの取得
        print("天気を更新します。")
        forecast_data = fetch_weather_from_tenkijp.get_precipitation_forecast()
        forecast_text = ("     " + forecast_data["weather"] + "     " 
                + "↑" + forecast_data["high_temperature_value"] + "°" + " " 
                + "↓" + forecast_data["low_temperature_value"] + "°" + "\n" 
                + "00~06" + ":" + forecast_data["probabilities"][0] + "%" + " " 
                + "06~12" + ":" + forecast_data["probabilities"][1] + "%" + " " + "\n"
                + "12~18" + ":" + forecast_data["probabilities"][2] + "%" + " " 
                + "18~24" + ":" + forecast_data["probabilities"][3] + "%" + " ")
        
        if self.show_margin:
            self.weather_label.config(text=forecast_text)
        else:
            self.canvas.itemconfig(self.weather_label, text=forecast_text)

        # 次の更新まで待機
        self.root_after_id_weather = self.root.after(3600 * 1000, self.update_weather)


    def update_video_without_margin_widget(self):
        # ランダムな動画を選択
        random_video_path = self.make_random_file_path(path=self.video_path, files=self.video_files)
        # 初期化
        pygame.init()
        pygame.display.set_caption("Video Display App")
        # 動画の読み込み
        self.cap = cv2.VideoCapture(random_video_path)
        # FPS設定
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        # clock設定
        clock = pygame.time.Clock()
        # タイマーイベント設定
        TIMER_EVENT_ID = pygame.USEREVENT + 1
        pygame.time.set_timer(TIMER_EVENT_ID, int(1000 / fps))
        # display大きさに調整        
        self.screen = pygame.display.set_mode((pygame.display.Info().current_w, pygame.display.Info().current_h))
        # loopフラグ
        self.running = True

        # 動画更新
        while self.running:
            for event in pygame.event.get():
                if event.type == TIMER_EVENT_ID:
                    self.update_video_without_margin_frame()
                elif event.type == pygame.QUIT:
                    self.close_window()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:  # ESC or Qキーが押された場合
                        self.close_window()
                    elif event.key == pygame.K_f:  # Fキーが押された場合
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_h:  # Hキーが押された場合
                        self.toggle_cursor()
                    elif event.key == pygame.K_v:  # Vキーが押された場合
                        self.set_volume()
                    elif event.key == pygame.K_m:  # Mキーが押された場合
                        self.sound_mute()
                    elif event.key == pygame.K_i:  # Iキーが押された場合
                        self.image_brightness_adjustment()
                    elif event.key == pygame.K_SPACE:  # SPACEキーが押された場合
                        self.next_video()

            # interval経過したかチェック
            print(pygame.time.get_ticks() - self.last_video_change_time)
            if pygame.time.get_ticks() - self.last_video_change_time >= self.interval * 1000:
                self.last_video_change_time = pygame.time.get_ticks()  # 現在の時間を保存
                self.next_video()  # 新しい動画を読み込む
            
            clock.tick(fps)
            
    def update_video_without_margin_frame(self):
        # 動画フレームの取得
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # ループ再生
            ret, frame = self.cap.read()

        # フレームの左右反転を解除（必要な場合）
        frame = cv2.flip(frame, 1)  # 1は水平反転（左右反転）

        # フレームの回転補正（縦動画の場合）
        frame = self.correct_rotation(frame)

        # OpenCVからPygameサーフェスへ変換
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # BGRからRGBへ変換
        frame_surface = pygame.surfarray.make_surface(frame)

        # フレームの大きさに合わせて拡大
        ratio = max(
            self.screen.get_width() / frame_surface.get_width(),
            self.screen.get_height() / frame_surface.get_height()
        )
        new_width = int(frame_surface.get_width() * ratio)
        new_height = int(frame_surface.get_height() * ratio)
        frame_surface = pygame.transform.scale(frame_surface, (new_width, new_height))

        offset_x = (new_width - self.screen.get_width()) // 2
        offset_y = (new_height - self.screen.get_height()) // 2

        clip_area = pygame.Rect(offset_x, offset_y, self.screen.get_width(), self.screen.get_height())
        self.screen.blit(frame_surface, (0, 0), area=clip_area)

        # 透明度を持つ黒いオーバーレイを描画
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.fill((0, 0, 0))  # 黒
        overlay.set_alpha(int(255 - self.image_brightness * 255)) 
        self.screen.blit(overlay, (0, 0))  # オーバーレイを描画
        
        if self.show_time:
            self.show_clock_without_margin_widget()

        pygame.display.flip()


    def correct_rotation(self, frame):
        # フレームの縦横サイズを取得
        height, width = frame.shape[:2]
        
        # 縦長動画の場合（縦横比が1より大きい場合）
        if height > width:
            frame = np.rot90(frame)  # 90度回転
        
        return frame

    # ランダムな画像を選ぶ関数
    def make_random_file_path(self, path, files):
        random_file = random.choice(files)
        random_file_path = os.path.join(path, random_file)
        return random_file_path
    
    def automatic_brightness_adjustment(self):
        now = datetime.now().time()
        
        if now >= datetime.strptime("09:00", "%H:%M").time() and now < datetime.strptime("17:00", "%H:%M").time():
            # 昼の時間帯は明るさを1.0に設定
            self.image_brightness = 1.0
            self.label_brightness = 1.0
            print("今は昼間（09:00〜17:00）です。")
        
        elif now >= datetime.strptime("21:00", "%H:%M").time() or now < datetime.strptime("05:00", "%H:%M").time():
            # 夜の時間帯は明るさを0.2に設定
            self.image_brightness = 0.2
            self.label_brightness = 0
            print("今は夜間（21:00〜05:00）です。")
        
        else:
            # 変化する時間帯（05:00 - 09:00、17:00 - 21:00）は徐々に変化させる
            if now >= datetime.strptime("05:00", "%H:%M").time() and now < datetime.strptime("09:00", "%H:%M").time():
                # 朝、夜から昼にかけて徐々に明るくする
                hours_since_6am = (datetime.combine(datetime.today(), now) - datetime.strptime("05:00", "%H:%M")).seconds / 3600
                self.image_brightness = 0.2 + (0.8 * (hours_since_6am / 4))
                self.label_brightness = 0 + (1.0 * (hours_since_6am / 4))
                print(f"今は朝（05:00〜09:00）です。徐々に明るくしています。")

            elif now >= datetime.strptime("17:00", "%H:%M").time() and now < datetime.strptime("21:00", "%H:%M").time():
                # 夕方、昼から夜にかけて徐々に暗くする
                hours_since_5pm = (datetime.combine(datetime.today(), now) - datetime.strptime("17:00", "%H:%M")).seconds / 3600
                self.image_brightness = 1.0 - (0.8 * (hours_since_5pm / 4))
                self.label_brightness = 1.0 - (1.0 * (hours_since_5pm / 4))
                print(f"今は夕方（17:00〜21:00）です。徐々に暗くしています。")

        # 背景色や画像の更新処理
        self.update_background_color()
        self.update_image_brightness()
        
        # 次の1時間後に再度明るさ調整を予約
        self.root_after_id_brightness_adjustment = self.root.after(3600 * 1000, self.automatic_brightness_adjustment)


    # 特定の時間までの残り時間を計算
    def calculate_time_next_trigger(self, target_hour, target_minute):
        # 現在の時刻を取得
        current_time = datetime.datetime.now()

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
    
    


def create_screen():
    try:
        VideoModeScreen()
    except FileNotFoundError:
        # 音楽停止
        messagebox.showerror("Error", "Video file not found!")
        video_mode_setting_screen.create_screen()
