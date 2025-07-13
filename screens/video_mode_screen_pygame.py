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
import pygame
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

class VideoModeScreenPygame:
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
        # 動画を表示
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

    def update_video_without_margin_widget(self):
        # ランダムな動画を選択
        random_video_path = self.make_random_file_path(path=self.video_path, files=self.video_files)
        self.current_video_path = random_video_path  # 現在の動画パスを保存
        
        # 初期化
        pygame.init()
        pygame.display.set_caption("Video Display App (Pygame)")
        
        # 動画の読み込み
        self.cap = cv2.VideoCapture(random_video_path)
        if not self.cap.isOpened():
            print(f"動画ファイルを開けません: {random_video_path}")
            return
        
        # 動画の最適化設定
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # バッファサイズを最小に
        
        # 動画の向き情報を取得（キャッシュ）
        self.video_orientation = self.cap.get(cv2.CAP_PROP_ORIENTATION_META)
        
        # 動画の寸法を取得
        self.video_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.video_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        # 回転が必要かどうかを事前に判断
        self.rotation_needed = self.determine_rotation_needed()
        
        # 左右反転が必要かどうかを判断
        self.flip_needed = self.determine_flip_needed()
        
        # FPS設定
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30.0
        
        print(f"動画の向き情報: {self.video_orientation}")
        print(f"動画の寸法: {self.video_width} x {self.video_height}")
        print(f"動画のFPS: {fps}")
        print(f"回転が必要: {self.rotation_needed}")
        print(f"左右反転が必要: {self.flip_needed}")
        
        # フレーム間隔を計算（秒）
        frame_interval = 1.0 / fps
        
        # clock設定
        clock = pygame.time.Clock()
        
        # display大きさに調整        
        self.screen = pygame.display.set_mode((pygame.display.Info().current_w, pygame.display.Info().current_h))
        
        # loopフラグ
        self.running = True
        last_frame_time = time()

        # 動画更新
        while self.running:
            current_time = time()
            
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
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

            # フレーム更新のタイミング制御
            if current_time - last_frame_time >= frame_interval:
                self.update_video_without_margin_frame()
                last_frame_time = current_time

            # interval経過したかチェック
            if current_time - self.last_video_change_time >= self.interval:
                self.last_video_change_time = current_time
                self.next_video()
            
            # 音楽停止のタイミングチェック
            if hasattr(self, 'music_stop_time') and current_time >= self.music_stop_time:
                if hasattr(self, 'player'):
                    self.player.stop_music()
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
            
            # FPS制限（動画のFPSに合わせる）
            clock.tick(int(fps))  # 動画の元のFPSに合わせる
            
    def update_video_without_margin_frame(self):
        # 動画フレームの取得
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # ループ再生
            ret, frame = self.cap.read()

        # フレームの左右反転を適用（必要な場合のみ）
        # 現在は無効化（問題がある場合は有効化）
        # if getattr(self, 'flip_needed', False):
        #     frame = cv2.flip(frame, 1)  # 1は水平反転（左右反転）

        # フレームの回転補正（縦動画の場合）
        frame = self.correct_rotation(frame)

        # OpenCVからPygameサーフェスへ変換
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # BGRからRGBへ変換
        frame_surface = pygame.surfarray.make_surface(frame)

        # フレームの大きさに合わせて拡大（キャッシュを活用）
        if not hasattr(self, 'scale_ratio') or not hasattr(self, 'screen_size'):
            self.scale_ratio = max(
                self.screen.get_width() / frame_surface.get_width(),
                self.screen.get_height() / frame_surface.get_height()
            )
            self.screen_size = (self.screen.get_width(), self.screen.get_height())
        
        new_width = int(frame_surface.get_width() * self.scale_ratio)
        new_height = int(frame_surface.get_height() * self.scale_ratio)
        
        # 高品質なリサイズ
        frame_surface = pygame.transform.scale(frame_surface, (new_width, new_height))

        offset_x = (new_width - self.screen_size[0]) // 2
        offset_y = (new_height - self.screen_size[1]) // 2

        clip_area = pygame.Rect(offset_x, offset_y, self.screen_size[0], self.screen_size[1])
        self.screen.blit(frame_surface, (0, 0), area=clip_area)

        # 透明度を持つ黒いオーバーレイを描画（明るさ調整）
        if self.image_brightness < 1.0:
            if not hasattr(self, 'overlay_surface') or self.overlay_surface.get_size() != self.screen_size:
                self.overlay_surface = pygame.Surface(self.screen_size)
                self.overlay_surface.fill((0, 0, 0))
            self.overlay_surface.set_alpha(int(255 - self.image_brightness * 255))
            self.screen.blit(self.overlay_surface, (0, 0))
        
        if self.show_time:
            self.show_clock_without_margin_widget()

        if self.show_weather:
            self.show_weather_without_margin_widget()

        if self.show_train_schedule:
            self.show_train_schedule_without_margin_widget()

        pygame.display.flip()

    def determine_rotation_needed(self):
        """回転が必要かどうかを判断する"""
        orientation = getattr(self, 'video_orientation', 0)
        video_width = getattr(self, 'video_width', 0)
        video_height = getattr(self, 'video_height', 0)
        
        # 動画の向き情報が有効な場合
        if orientation in [90, 180, 270]:
            return orientation
        # 向き情報がない場合は寸法で判断
        elif video_width > 0 and video_height > 0:
            # 縦長動画（スマホで撮影された動画）の場合
            if video_height > video_width and video_height / video_width > 1.3:
                return 90
        return 0  # 回転不要

    def determine_flip_needed(self):
        """左右反転が必要かどうかを判断する"""
        # 基本的には反転しない（保守的なアプローチ）
        orientation = getattr(self, 'video_orientation', 0)
        
        # 向き情報がある場合は反転しない
        if orientation in [90, 180, 270]:
            return False
        
        # 動画ファイル名から判断（明らかにカメラ動画の場合のみ）
        current_video_path = getattr(self, 'current_video_path', '')
        if current_video_path:
            filename = os.path.basename(current_video_path).lower()
            # より具体的なカメラ関連のキーワード
            camera_keywords = ['selfie', 'front_camera', 'back_camera', 'mirror']
            if any(keyword in filename for keyword in camera_keywords):
                print(f"カメラ動画と判断: {filename}")
                return True
        
        # デフォルトは反転しない
        print(f"左右反転なし: {current_video_path}")
        return False

    def correct_rotation(self, frame):
        # 事前に判断された回転情報を使用
        rotation = getattr(self, 'rotation_needed', 0)
        
        if rotation == 90:
            frame = np.rot90(frame, k=1)
        elif rotation == 180:
            frame = np.rot90(frame, k=2)
        elif rotation == 270:
            frame = np.rot90(frame, k=3)
        
        return frame

    # 時計のUI作成
    def show_clock_without_margin_widget(self):
        # 現在の時間と日付を取得
        current_date = strftime('%Y-%m-%d %A', localtime())
        current_time = strftime('%H:%M:%S')

        # フォントをキャッシュ（初回のみ作成）
        if not hasattr(self, 'date_font'):
            self.date_font = pygame.font.SysFont('calibri', DATE_FONT_SIZE, bold=True)
            self.time_font = pygame.font.SysFont('calibri', TIME_FONT_SIZE, bold=True)
        
        current_date_surface = self.date_font.render(current_date, True, (255, 255, 255))
        current_time_surface = self.time_font.render(current_time, True, (255, 255, 255))
        
        # 位置を調整（image_modeと同じ位置）
        self.screen.blit(current_date_surface, (self.screen_size[0] // 3.5, self.screen_size[1] - 300))
        self.screen.blit(current_time_surface, (self.screen_size[0] // 3.5, self.screen_size[1] - 150))

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

    # 改行付きテキストを描画する関数
    def render_multiline_text(self, text, font, color, x, y, line_height=None, center_align=False):
        if line_height is None:
            line_height = font.get_height() + 2
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if line.strip():  # 空行でない場合のみ描画
                text_surface = font.render(line, True, color)
                if center_align:
                    # 中央揃えの場合、テキストの幅を考慮して位置を調整
                    text_width = text_surface.get_width()
                    text_x = x - text_width // 2
                else:
                    text_x = x
                self.screen.blit(text_surface, (text_x, y + i * line_height))

    # 天気のUI作成
    def show_weather_without_margin_widget(self):
        # キャッシュされた天気データを使用
        if self.weather_data != None:
            forecast_text = (self.weather_data["weather_data"][0]['weather_icon'] + "　" + "↑" + self.weather_data["weather_data"][0]['high_temp'] + "°" + "↓" + self.weather_data["weather_data"][0]['low_temp'] + "°" + "\n" 
                + "00~06" + ":" + self.weather_data["today_probabilities"][0] + "%" + "　" + "06~12" + ":" + self.weather_data["today_probabilities"][1] + "%" + "\n"
                + "12~18" + ":" + self.weather_data["today_probabilities"][2] + "%" + "　" + "18~24" + ":" + self.weather_data["today_probabilities"][3] + "%" + "\n"
                + "\n"
                + self.weather_data["weather_data"][1]['weekday'] + " " + self.weather_data["weather_data"][2]['weekday'] + " " + self.weather_data["weather_data"][3]['weekday'] + " " + self.weather_data["weather_data"][4]['weekday'] + " " + self.weather_data["weather_data"][5]['weekday'] + " " + self.weather_data["weather_data"][6]['weekday'] + "\n"
                + self.weather_data["weather_data"][1]['weather_icon'] + "     " + self.weather_data["weather_data"][2]['weather_icon'] + "     " + self.weather_data["weather_data"][3]['weather_icon'] + "     " + self.weather_data["weather_data"][4]['weather_icon'] + "     " + self.weather_data["weather_data"][5]['weather_icon'] + "     " + self.weather_data["weather_data"][6]['weather_icon'])

            # pygameでテキストを表示（太字で統一）
            if not hasattr(self, 'weather_font'):
                self.weather_font = pygame.font.SysFont('calibri', WEATHER_FONT_SIZE, bold=True)
            
            # 改行付きテキストを描画（中央揃え）
            text_x = self.screen_size[0] // 1.33
            text_y = self.screen_size[1] - 200
            self.render_multiline_text(forecast_text, self.weather_font, (255, 255, 255), text_x, text_y, center_align=True)

    # 列車時刻表の表示
    def show_train_schedule_without_margin_widget(self):
        # キャッシュされた列車時刻表データを使用
        try:
            if self.train_data and self.train_data['A'] is not None and self.train_data['B'] is not None:
                train_schedule_text = (
                    DESTINATION_A + "　" + DESTINATION_B + "\n"
                    + self.train_data['A'][0]['time'] + "　　　" + self.train_data['B'][0]['time'] + "\n"
                    + self.train_data['A'][1]['time'] + "　　　" + self.train_data['B'][1]['time'] + "\n"
                    + self.train_data['A'][2]['time'] + "　　　" + self.train_data['B'][2]['time'] + "\n")
                
                # pygameでテキストを表示（太字で統一）
                if not hasattr(self, 'train_font'):
                    self.train_font = pygame.font.SysFont('calibri', WEATHER_FONT_SIZE, bold=True)
                
                # 改行付きテキストを描画（中央揃え）
                text_x = self.screen_size[0] // 1.33
                text_y = self.screen_size[1] - 400
                self.render_multiline_text(train_schedule_text, self.train_font, (255, 255, 255), text_x, text_y, center_align=True)
        except Exception as e:
            print(f"列車時刻表の表示でエラーが発生しました: {e}")

    # ランダムな動画を選ぶ関数
    def make_random_file_path(self, path, files):
        random_file = random.choice(files)
        random_file_path = os.path.join(path, random_file)
        return random_file_path

    # キーバインドのための関数一覧
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

    def image_brightness_adjustment(self):
        self.image_brightness -= 0.2
        if self.image_brightness < 0:
            self.image_brightness = 1

    def toggle_fullscreen(self):
        # 現在のモードを取得し、全画面かどうかを切り替える
        current_mode = pygame.display.get_surface()
        is_fullscreen = current_mode.get_flags() & pygame.FULLSCREEN

        pygame.display.set_mode(
            (0, 0), 
            0 if is_fullscreen else pygame.FULLSCREEN
        )

    def toggle_cursor(self):
        # 現在のカーソル表示状態を取得して反転
        pygame.mouse.set_visible(not pygame.mouse.get_visible())

    def set_volume(self):
        if not hasattr(self, 'player'):
            print("プレイヤーが定義されていません")
            return
        self.volume = max(0.1, self.volume - 0.2) if self.volume >= 0.1 else 1.0
        print(f"音量を {self.volume} に変更しました")
        self.player.set_volume(self.volume)

    def sound_mute(self):
        if not hasattr(self, 'player'):
            print("プレイヤーが定義されていません")
            return
        self.player.sound_mute()

    def next_video(self):
        self.running = False
        self.update_video_without_margin_widget()

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
        VideoModeScreenPygame()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        messagebox.showerror("Error", f"動画再生エラー: {e}")
        video_mode_setting_screen.create_screen() 