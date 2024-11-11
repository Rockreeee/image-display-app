import tkinter as tk
import screens.image_mode_setting_screen as image_mode_setting_screen
import utils.settings_manager as settings_manager
import utils.fetch_weather as fetch_weather
import utils.music_player as music_player
import os
import random
from datetime import datetime
import threading
from tkinter import messagebox
from time import strftime, localtime
from PIL import Image, ImageEnhance, ImageTk

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

class ImageModeScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Display App")
        self.root.configure(background='white')
        self.image_brightness = 1.0
        self.label_brightness = 1.0
        self.volume = 1.0

        # 設定変数の初期化
        self.initialize_settings()
        self.set_keybinding()
        self.create_widgets()

    # 設定をロードし、各変数に設定
    def initialize_settings(self):
        settings = settings_manager.load_settings()
        self.image_path = settings.get('image_path')
        self.interval = int(settings.get('interval'))
        self.show_margin = settings.get('show_margin')
        self.automatic_brightness = settings.get('automatic_brightness')
        self.show_time = settings.get('show_time')
        self.show_weather = settings.get('show_weather')
        self.sound_path = settings.get('sound_path')
        self.sound_mode = settings.get('sound_mode')

        self.image_files = [f for f in os.listdir(self.image_path) if f.endswith(('.jpg', '.jpeg', '.png'))]

    # キーバインド一覧
    def set_keybinding(self):
        # 終了する時のキーバインド
        self.root.bind("<Escape>", self.close_window)
        self.root.bind("<q>", self.close_window)

        # 文字の明るさを調整するキーバインド
        self.root.bind("<b>", self.label_brightness_adjustment)

        # 画像の明るさを調整するキーバインド
        self.root.bind("<i>", self.image_brightness_adjustment)

        # キーイベントをバインドしてフルスクリーン表示の切り替えを有効にする
        self.root.bind("<f>", self.toggle_fullscreen)

        # キーイベントをバインドしてカーソルを表示きりかえ
        self.root.bind("<h>", self.toggle_cursor)

        # キーイベントをバインドして音量の調整を有効にする
        self.root.bind("<v>", self.set_volume)

        # キーイベントをバインドしてミュートの切り替えを有効にする
        self.root.bind("<m>", self.sound_mute)
            
        # キーイベントをバインドして画像変更を有効にする
        self.root.bind("<space>", self.next_image)

    # start: キーバインドのための関数一覧
    # 終了する時の関数
    def close_window(self, event):
        print("停止します")
        # 音楽停止
        if hasattr(self, 'player'):
            self.player.stop_music()
        self.cancel_root_after()
        self.root.destroy()
        image_mode_setting_screen.create_screen()

    # 明るさを調整する関数
    def label_brightness_adjustment(self, event):
        if not hasattr(self, 'label_brightness'):
            print("文字が定義されていません")
            return
        else:
            self.label_brightness -= 0.2
            if self.label_brightness < 0:
                self.label_brightness = 1
            self.update_background_color()

    # 明るさを調整する関数
    def image_brightness_adjustment(self, event):
        self.image_brightness -= 0.2
        if self.image_brightness < 0:
            self.image_brightness = 1
        if hasattr(self, 'enhancer'):
            self.update_image_brightness()

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
    # end: キーバインドのための関数一覧

    # UI作成
    def create_widgets(self):

        # 余白を表示
        if self.show_margin:
            self.label = tk.Label(self.root, bg='white')
            self.label.pack(fill=tk.BOTH, expand=True, side="bottom")
            # 時計を表示
            if self.show_time:
                self.show_clock_with_margin_widget()
                
            # 天気を表示
            if self.show_weather:
                self.show_weather_with_margin_widget()

            # 余白あり画像表示
            self.update_image_with_margin_widget()
                
        else:
            self.canvas = tk.Canvas(self.root, bg='white')
            self.canvas.pack(fill=tk.BOTH, expand=True)

            # 時計を表示
            if self.show_time:
                self.show_clock_without_margin_widget()

            # 天気を表示
            if self.show_weather:
                self.show_weather_without_margin_widget()

            # 余白なし画像を表示
            self.update_image_without_margin_widget()


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
    def show_clock_with_margin_widget(self):
        # ラベルを作成
        self.date_label = tk.Label(self.root, font=('calibri', DATE_FONT_SIZE, 'bold'), bg='white', fg='gray')
        self.time_label = tk.Label(self.root, font=('calibri', TIME_FONT_SIZE, 'bold'), bg='white', fg='gray')

        # ラベルの高さを取得して時間ラベルを配置
        self.date_label.pack(pady=(MARGIN_ABOVE_CLOCK, 0))
        self.time_label.pack(pady=(self.date_label.winfo_height() + MARGIN_ABOVE_CLOCK, 0))

        # 日付と曜日、時間を更新する関数を初回呼び出し
        self.update_time()

    # 時計のUI作成
    def show_clock_without_margin_widget(self):
        # ラベルを作成
        self.date_label = self.canvas.create_text(self.root.winfo_screenwidth() // 4, self.root.winfo_screenheight() - 300, font=('calibri', DATE_FONT_SIZE, 'bold'), fill="white")
        self.time_label = self.canvas.create_text(self.root.winfo_screenwidth() // 4, self.root.winfo_screenheight() - 150, font=('calibri', TIME_FONT_SIZE, 'bold'), fill="white")

        # 日付と曜日、時間を更新する関数を初回呼び出し
        self.update_time()

    # 時計のUI更新
    def update_time(self):
        # 現在の時間と日付を取得
        current_time = strftime('%H:%M:%S')
        current_date = strftime('%Y-%m-%d %A', localtime())

        # ラベルのテキストを更新
        if self.show_margin:
            self.time_label.config(text=current_time)
            self.date_label.config(text=current_date)
        else:
            self.canvas.itemconfig(self.time_label, text=current_time)
            self.canvas.itemconfig(self.date_label, text=current_date)

        # 次の更新まで待機
        self.root_after_id_time = self.root.after(1000, self.update_time)


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
        forecast_data = fetch_weather.get_precipitation_forecast()
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

    def next_image(self, event):
        if self.show_margin:
            self.root.after_cancel(self.root_after_id_image_with_margin)
            self.update_image_with_margin_widget()
        else:
            self.root.after_cancel(self.root_after_id_image_without_margin)
            self.update_image_without_margin_widget()


    # 画像（マージンあり）のUI作成
    def update_image_with_margin_widget(self):
        # その他要素の高さを取得
        clock_height = 0
        if self.show_time:
            date_label_height = self.date_label.winfo_height()
            time_label_height = self.time_label.winfo_height()
            clock_height = MARGIN_ABOVE_CLOCK + date_label_height + time_label_height

        weather_height = 0
        if self.show_weather:
            weather_height = self.weather_label.winfo_height()

        # ランダムな画像を選択
        random_image_path = self.make_random_image_path(image_path=self.image_path)

        # 画像UIを配置
        img = Image.open(random_image_path)
        img_width, img_height = img.size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight() - clock_height - weather_height
        
        if img_width > screen_width or img_height > screen_height:
            ratio = min(screen_width / img_width, screen_height / img_height)
            new_width = int(img_width * ratio * CONSTANT_MARGIN)
            new_height = int(img_height * ratio * CONSTANT_MARGIN)
            img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # 明るさを調整するためのBrightnessオブジェクトを作成し、ファクターを設定
        self.enhancer = ImageEnhance.Brightness(img)
        self.update_image_brightness()

        # 次の更新まで待機
        self.root_after_id_image_with_margin = self.root.after(self.interval * 1000, self.update_image_with_margin_widget)
    

    # 画像（マージンなし）のUI作成
    def update_image_without_margin_widget(self):
        # ランダムな画像を選択
        random_image_path = self.make_random_image_path(image_path=self.image_path)

        # 画像UIを配置
        img = Image.open(random_image_path)
        img_width, img_height = img.size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        ratio = max(screen_width / img_width, screen_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        img = img.resize((new_width, new_height), Image.LANCZOS)

        # 画像の中央部分を切り取るための座標を計算
        x = (new_width - screen_width) // 2
        y = (new_height - screen_height) // 2

        # 画像が画面より大きい場合は切り取る
        if x > 0 or y > 0:
            img = img.crop((x, y, x + screen_width, y + screen_height))

        # 明るさを調整するためのBrightnessオブジェクトを作成し、ファクターを設定
        self.enhancer = ImageEnhance.Brightness(img)
        self.update_image_brightness()

        # 次の更新まで待機
        self.root_after_id_image_without_margin = self.root.after(self.interval * 1000, self.update_image_without_margin_widget)

    # ランダムな画像を選ぶ関数
    def make_random_image_path(self, image_path):
        random_image = random.choice(self.image_files)
        random_image_path = os.path.join(image_path, random_image)
        return random_image_path
    
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
    
    def update_image_brightness(self):
        adjusted_image = self.enhancer.enhance(self.image_brightness)
        self.photo = ImageTk.PhotoImage(adjusted_image)
        if self.show_margin:
            self.label.configure(image=self.photo)
            self.label.image = self.photo
        else:
            image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
            self.canvas.tag_lower(image_id)
    
    def update_background_color(self):

        if self.show_margin:
            original_color_value = int(self.label_brightness * 255)
            bg_color = f'#{original_color_value:02x}{original_color_value:02x}{original_color_value:02x}'
            if 50 <= original_color_value and original_color_value <= 200:
                fg_color = 'white'
            else:
                fg_color = 'grey'
            self.root.configure(background=bg_color)
            self.label.config(bg=bg_color)
            if self.show_time:
                self.date_label.config(background=bg_color, foreground=fg_color)
                self.time_label.config(background=bg_color, foreground=fg_color)
            if self.show_weather:
                self.weather_label.config(background=bg_color, foreground=fg_color)
        else:
            original_color_value = int(self.label_brightness * 255)
            fg_color = f'#{original_color_value:02x}{original_color_value:02x}{original_color_value:02x}'
            # if self.show_time:
            #     self.canvas.itemconfig(self.date_label, fill=fg_color)
            #     self.canvas.itemconfig(self.time_label, fill=fg_color)
            # if self.show_weather:
            #     self.canvas.itemconfig(self.weather_label, fill=fg_color)


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
        if hasattr(self, 'root_after_id_image_with_margin'):
            self.root.after_cancel(self.root_after_id_image_with_margin)
        if hasattr(self, 'root_after_id_image_without_margin'):
            self.root.after_cancel(self.root_after_id_image_without_margin)
        if hasattr(self, 'root_after_id_brightness_adjustment'):
            self.root.after_cancel(self.root_after_id_brightness_adjustment)
        if hasattr(self, 'root_after_id_sound_stop_booking'):
            self.root.after_cancel(self.root_after_id_sound_stop_booking)
        if hasattr(self, 'root_after_id_sound_start_booking'):
            self.root.after_cancel(self.root_after_id_sound_start_booking)


def create_screen():
    root = tk.Tk()
    try:
        ImageModeScreen(root)
        root.mainloop()  # エラーがない場合のみ実行
    except FileNotFoundError:
        # 音楽停止
        root.destroy()
        messagebox.showerror("Error", "Image file not found!")
        image_mode_setting_screen.create_screen()
