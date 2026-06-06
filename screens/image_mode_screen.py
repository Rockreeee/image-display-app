"""画像モードの表示画面(このアプリの中心機能)。

フォルダ内またはネット上の画像をランダムに全画面スライドショー表示し、
任意で時計・天気・列車時刻表を重ねて表示する。時間帯に応じた明るさの
自動調整や BGM 再生にも対応する。

調整値・地域固有データ(フォント, 明るさの時間帯, 天気地点, 列車路線など)は
config.py に集約してある。
"""

import os
import json
import random
import threading
from datetime import datetime
from time import strftime, localtime

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageEnhance, ImageTk

import config
import utils.settings_manager as settings_manager
import utils.music_player as music_player
import services.fetch_weather_from_tenkijp as fetch_weather_from_tenkijp
import services.fetch_image_from_pixel as fetch_image_from_pixel
import services.fetch_train_schedule as fetch_train_schedule
import screens.image_mode_setting_screen as image_mode_setting_screen
from screens.mixins import WindowControlsMixin


class ImageModeScreen(WindowControlsMixin):
    def __init__(self, root):
        self.root = root
        self.root.title("Image Display App")
        self.root.configure(background="white")
        self.image_brightness = 1.0
        self.label_brightness = 1.0
        self.volume = 1.0

        self.initialize_settings()
        self.set_keybinding()
        self.create_widgets()

    def initialize_settings(self):
        settings = settings_manager.load_settings()
        self.auto_image = settings.get("auto_image")
        self.image_path = settings.get("image_path")
        self.interval = int(settings.get("interval"))
        self.automatic_brightness = settings.get("automatic_brightness")
        self.show_time = settings.get("show_time")
        self.show_weather = settings.get("show_weather")
        self.show_train_schedule = settings.get("show_train_schedule")
        self.sound_path = settings.get("sound_path")
        self.sound_mode = settings.get("sound_mode")

        # 画像フォルダが指定されている場合のみファイル一覧を取得する
        if self.image_path and os.path.isdir(self.image_path):
            self.image_files = [
                f for f in os.listdir(self.image_path)
                if f.lower().endswith(config.IMAGE_EXTENSIONS)
            ]
        else:
            self.image_files = []

    def set_keybinding(self):
        self.root.bind("<Escape>", self.close_window)
        self.root.bind("<q>", self.close_window)
        self.root.bind("<b>", self.label_brightness_adjustment)
        self.root.bind("<i>", self.image_brightness_adjustment)
        self.root.bind("<f>", self.toggle_fullscreen)
        self.root.bind("<h>", self.toggle_cursor)
        self.root.bind("<v>", self.set_volume)
        self.root.bind("<m>", self.sound_mute)
        self.root.bind("<space>", self.next_image)

    # --- キーバインド処理 ---
    def close_window(self, event=None):
        print("停止します")
        if hasattr(self, "player"):
            self.player.stop_music()
        self.cancel_root_after()
        self.root.destroy()
        image_mode_setting_screen.create_screen()

    def label_brightness_adjustment(self, event=None):
        """時計・天気などの文字色の明るさを一段階下げる。"""
        self.label_brightness -= 0.2
        if self.label_brightness < 0:
            self.label_brightness = 1

        brightness = int(255 * self.label_brightness)
        color = f"#{brightness:02x}{brightness:02x}{brightness:02x}"
        for attr in ("date_label", "time_label", "weather_label", "train_schedule_label"):
            if hasattr(self, attr):
                self.canvas.itemconfig(getattr(self, attr), fill=color)

    def image_brightness_adjustment(self, event=None):
        """画像の明るさを一段階下げる。"""
        self.image_brightness -= 0.2
        if self.image_brightness < 0:
            self.image_brightness = 1
        if hasattr(self, "enhancer"):
            self.update_image_brightness()

    def set_volume(self, event=None):
        if not hasattr(self, "player"):
            print("プレイヤーが定義されていません")
            return
        self.volume = max(0.1, self.volume - 0.2) if self.volume >= 0.1 else 1.0
        print(f"音量を {self.volume} に変更しました")
        self.player.set_volume(self.volume)

    def sound_mute(self, event=None):
        if not hasattr(self, "player"):
            print("プレイヤーが定義されていません")
            return
        self.player.sound_mute()

    def next_image(self, event=None):
        """次の画像へ即座に切り替える。"""
        self.root.after_cancel(self.root_after_id_image)
        self.update_image_widget()

    # --- UI 作成 ---
    def create_widgets(self):
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas_image = self.canvas.create_image(0, 0, anchor="nw")

        if self.show_time:
            self.show_clock_widget()
        if self.show_weather:
            self.show_weather_widget()
        if self.show_train_schedule:
            self.show_train_schedule_widget()

        self.update_image_widget()

        if self.automatic_brightness:
            self.automatic_brightness_adjustment()

        if self.sound_path != "":
            if self.sound_mode == "1":
                self.play_sound(self.sound_path)
            elif self.sound_mode == "2":
                self.automatic_sound_booking()

    # --- 時計 ---
    def show_clock_widget(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.date_label = self.canvas.create_text(
            screen_width // 3.5, screen_height - 300,
            font=("calibri", config.DATE_FONT_SIZE, "bold"), fill="white",
        )
        self.time_label = self.canvas.create_text(
            screen_width // 3.5, screen_height - 150,
            font=("calibri", config.TIME_FONT_SIZE, "bold"), fill="white",
        )
        self.update_time()

    def update_time(self):
        self.canvas.itemconfig(self.time_label, text=strftime("%H:%M:%S"))
        self.canvas.itemconfig(self.date_label, text=strftime("%Y-%m-%d %A", localtime()))
        self.root_after_id_time = self.root.after(1000, self.update_time)

    # --- 天気 ---
    def show_weather_widget(self):
        self.weather_label = self.canvas.create_text(
            self.root.winfo_screenwidth() // 1.33, self.root.winfo_screenheight() - 200,
            font=("calibri", config.WEATHER_FONT_SIZE, "bold"), fill="white",
        )
        self.update_weather()

    def update_weather(self):
        """tenki.jp から天気を取得し、1時間ごとに更新する。"""
        forecast_data = fetch_weather_from_tenkijp.get_precipitation_forecast()
        if forecast_data is not None:
            weather = forecast_data["weather_data"]
            probs = forecast_data["today_probabilities"]
            forecast_text = (
                weather[0]["weather_icon"] + "　↑" + weather[0]["high_temp"] + "°↓" + weather[0]["low_temp"] + "°\n"
                + "00~06:" + probs[0] + "%　06~12:" + probs[1] + "%\n"
                + "12~18:" + probs[2] + "%　18~24:" + probs[3] + "%\n\n"
                + " ".join(weather[i]["weekday"] for i in range(1, 7)) + "\n"
                + "     ".join(weather[i]["weather_icon"] for i in range(1, 7))
            )
            self.canvas.itemconfig(self.weather_label, text=forecast_text, anchor="center", justify="center")

        self.root_after_id_weather = self.root.after(3600 * 1000, self.update_weather)

    # --- 列車時刻表 ---
    def show_train_schedule_widget(self):
        self.train_schedule_label = self.canvas.create_text(
            self.root.winfo_screenwidth() // 1.33, self.root.winfo_screenheight() - 500,
            font=("calibri", config.WEATHER_FONT_SIZE, "bold"), fill="white",
        )
        self.update_train_schedule()

    def update_train_schedule(self):
        """JSON の時刻表から次の列車を読み取り、1分ごとに更新する。"""
        with open(config.TRAIN_SCHEDULE_FILE_A) as f:
            schedule_a = json.load(f)
        with open(config.TRAIN_SCHEDULE_FILE_B) as f:
            schedule_b = json.load(f)
        with open(config.TRAIN_SCHEDULE_FILE_C) as f:
            schedule_c = json.load(f)

        next_a = fetch_train_schedule.get_next_trains(schedule_a)
        next_b = fetch_train_schedule.get_next_trains(schedule_b)
        next_c = fetch_train_schedule.get_next_trains(schedule_c)
        if next_a and next_b and next_c:
            text = (
                f"【{config.TRAIN_LINE_AB_NAME}】\n"
                + "　" + schedule_a["destination"] + "　　" + schedule_b["destination"] + "\n"
                + next_a[0]["time"] + "　　　" + next_b[0]["time"] + "\n"
                + next_a[1]["time"] + "　　　" + next_b[1]["time"] + "\n"
                + next_a[2]["time"] + "　　　" + next_b[2]["time"] + "\n\n"
                + f"【{config.TRAIN_LINE_C_NAME}】\n"
                + schedule_c["destination"] + "\n"
                + next_c[0]["time"] + "\n"
                + next_c[1]["time"] + "\n"
                + next_c[2]["time"] + "\n"
            )
            self.canvas.itemconfig(self.train_schedule_label, text=text, anchor="center", justify="center")

        self.root_after_id_train_schedule = self.root.after(60 * 1000, self.update_train_schedule)

    # --- 画像 ---
    def update_image_widget(self):
        """次の画像を読み込み、画面いっぱいに表示する。"""
        if self.auto_image:
            img = fetch_image_from_pixel.fetch_image_from_url()
        else:
            if not self.image_files:
                # フォルダが空/存在しない場合は設定画面へ戻す(create_screen が捕捉)
                raise FileNotFoundError(self.image_path)
            img = Image.open(self.random_image_path())

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        img_width, img_height = img.size

        # 画面を覆うように拡大し、はみ出した部分を中央基準で切り取る
        ratio = max(screen_width / img_width, screen_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        img = img.resize((new_width, new_height), Image.LANCZOS)

        x = (new_width - screen_width) // 2
        y = (new_height - screen_height) // 2
        if x > 0 or y > 0:
            img = img.crop((x, y, x + screen_width, y + screen_height))

        self.enhancer = ImageEnhance.Brightness(img)
        self.update_image_brightness()

        self.root_after_id_image = self.root.after(self.interval * 1000, self.update_image_widget)

    def random_image_path(self):
        """画像フォルダからランダムに1ファイルのパスを返す。"""
        return os.path.join(self.image_path, random.choice(self.image_files))

    def update_image_brightness(self):
        adjusted_image = self.enhancer.enhance(self.image_brightness)
        # PhotoImage は参照が切れると消えるため、インスタンス属性に保持する
        self.photo = ImageTk.PhotoImage(adjusted_image)
        self.canvas.itemconfig(self.canvas_image, image=self.photo)

    # --- 自動明るさ調整 ---
    def automatic_brightness_adjustment(self):
        """時間帯に応じて画像の明るさを設定し、1時間ごとに再調整する。"""
        now = datetime.now().time()
        day_start = datetime.strptime(f"{config.DAY_START_HOUR:02d}:00", "%H:%M").time()
        day_end = datetime.strptime(f"{config.DAY_END_HOUR:02d}:00", "%H:%M").time()
        night_start = datetime.strptime(f"{config.NIGHT_START_HOUR:02d}:00", "%H:%M").time()
        night_end = datetime.strptime(f"{config.NIGHT_END_HOUR:02d}:00", "%H:%M").time()

        if day_start <= now < day_end:
            # 昼間: 最大の明るさ
            self.image_brightness = config.DAY_BRIGHTNESS
        elif now >= night_start or now < night_end:
            # 夜間: 最小の明るさ
            self.image_brightness = config.NIGHT_BRIGHTNESS
        elif night_end <= now < day_start:
            # 朝(夜→昼): 徐々に明るくする
            hours = (datetime.combine(datetime.today(), now)
                     - datetime.strptime(f"{config.NIGHT_END_HOUR:02d}:00", "%H:%M")).seconds / 3600
            span = config.DAY_START_HOUR - config.NIGHT_END_HOUR
            self.image_brightness = config.NIGHT_BRIGHTNESS + (config.DAY_BRIGHTNESS - config.NIGHT_BRIGHTNESS) * (hours / span)
        else:
            # 夕方(昼→夜): 徐々に暗くする
            hours = (datetime.combine(datetime.today(), now)
                     - datetime.strptime(f"{config.DAY_END_HOUR:02d}:00", "%H:%M")).seconds / 3600
            span = config.NIGHT_START_HOUR - config.DAY_END_HOUR
            self.image_brightness = config.DAY_BRIGHTNESS - (config.DAY_BRIGHTNESS - config.NIGHT_BRIGHTNESS) * (hours / span)

        self.update_image_brightness()
        self.root_after_id_brightness_adjustment = self.root.after(3600 * 1000, self.automatic_brightness_adjustment)

    def calculate_time_next_trigger(self, target_hour, target_minute):
        """指定時刻までの残り秒数を返す。"""
        now = datetime.now()
        target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        return int((target_time - now).total_seconds())

    # --- BGM ---
    def play_sound(self, path):
        """別スレッドで BGM をループ再生する。"""
        self.player = music_player.MusicPlayer(path)
        self.music_thread = threading.Thread(target=self.player.play_music)
        self.music_thread.start()

    def automatic_sound_booking(self):
        """毎朝決まった時刻に一定時間だけ BGM を再生するよう予約する。"""
        # 初回呼び出し時は再生せず、翌朝の予約だけ行う
        if hasattr(self, "player"):
            self.player = music_player.MusicPlayer(self.sound_path)
            self.music_thread = threading.Thread(target=self.player.play_music)
            self.music_thread.start()
            self.root_after_id_sound_stop_booking = self.root.after(
                int(config.MUSIC_STOP_MINUTES * 60) * 1000, self.player.stop_music
            )

        time_to_morning = self.calculate_time_next_trigger(
            config.MORNING_SOUND_HOUR, config.MORNING_SOUND_MINUTE
        )
        if time_to_morning < 1:
            time_to_morning += 86400

        print("音が流れるまで：", int(time_to_morning), "秒")
        self.root_after_id_sound_start_booking = self.root.after(
            int(time_to_morning) * 1000, self.automatic_sound_booking
        )

    def cancel_root_after(self):
        """予約済みの after コールバックをすべてキャンセルする。"""
        for attr in (
            "root_after_id_time",
            "root_after_id_weather",
            "root_after_id_train_schedule",
            "root_after_id_image",
            "root_after_id_brightness_adjustment",
            "root_after_id_sound_stop_booking",
            "root_after_id_sound_start_booking",
        ):
            if hasattr(self, attr):
                self.root.after_cancel(getattr(self, attr))


def create_screen():
    root = tk.Tk()
    try:
        ImageModeScreen(root)
        root.mainloop()
    except FileNotFoundError:
        root.destroy()
        messagebox.showerror("Error", "Image file not found!")
        image_mode_setting_screen.create_screen()
