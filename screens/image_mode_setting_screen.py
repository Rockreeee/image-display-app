"""画像モードの設定画面。

画像の取得元・切り替え間隔・オーバーレイ表示(時計/天気/列車)・
BGM などを設定し、画像表示モードを開始する。
"""

import tkinter as tk
from tkinter import filedialog, messagebox

import utils.settings_manager as settings_manager
import utils.ui as ui
import screens.home_screen as home_screen
import screens.image_mode_screen as image_mode_screen


class ImageModeSettingScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Display App")

        self.initialize_settings()
        self.create_widgets()
        # 説明文を含む全項目が収まるよう、内容に合わせてサイズ調整する
        ui.fit_window(self.root, min_width=600)

    def initialize_settings(self):
        settings = settings_manager.load_settings()
        self.auto_image_var = tk.BooleanVar(value=settings.get("auto_image"))
        self.image_path_var = tk.StringVar(value=settings.get("image_path"))
        self.interval_var = tk.StringVar(value=settings.get("interval"))
        self.automatic_brightness_var = tk.BooleanVar(value=settings.get("automatic_brightness"))
        self.show_time_var = tk.BooleanVar(value=settings.get("show_time"))
        self.show_weather_var = tk.BooleanVar(value=settings.get("show_weather"))
        self.show_train_schedule_var = tk.BooleanVar(value=settings.get("show_train_schedule"))
        self.sound_path_var = tk.StringVar(value=settings.get("sound_path"))
        self.sound_mode_var = tk.StringVar(value=settings.get("sound_mode"))

    def create_widgets(self):
        form = ui.SettingsForm(self.root)

        form.add_section("画像 (Image)")
        form.add_checkbox(
            "Auto Image", self.auto_image_var,
            help_text="オンにすると、フォルダの代わりにインターネットから画像を自動取得します。",
        )
        form.add_path(
            "Image Path:", self.image_path_var, self.select_image_path,
            help_text="表示する画像が入ったフォルダ。Auto Image がオフのとき必須です。",
        )
        form.add_entry(
            "Display Interval (seconds):", self.interval_var,
            help_text="画像を切り替える間隔(秒)。例: 3600 で1時間ごと。",
        )

        form.add_section("画面表示 (Overlay)")
        form.add_checkbox(
            "Automatic Brightness Adjustment", self.automatic_brightness_var,
            help_text="時間帯に応じて画面の明るさを自動調整します(夜は暗く)。",
        )
        form.add_checkbox("Show Clock", self.show_time_var,
                          help_text="日付と時刻を画面に表示します。")
        form.add_checkbox("Show Weather", self.show_weather_var,
                          help_text="天気予報と降水確率を表示します(ネット接続が必要)。")
        form.add_checkbox("Show Train Schedule", self.show_train_schedule_var,
                          help_text="最寄り駅の次の列車時刻を表示します。")

        form.add_section("サウンド (Sound)")
        form.add_path(
            "Sound Path:", self.sound_path_var, self.select_sound_path,
            help_text="BGM に使う mp3 が入ったフォルダ。",
        )
        form.add_radio("Sound Off", self.sound_mode_var, "0",
                       help_text="BGM を再生しません。")
        form.add_radio("Sound On", self.sound_mode_var, "1",
                       help_text="常に BGM を再生します。")
        form.add_radio("Morning Sound Only", self.sound_mode_var, "2",
                       help_text="毎朝7時から10分間だけ BGM を再生します。")

        form.add_action_buttons(self.back_action, self.start_action)

    def select_image_path(self):
        path = filedialog.askdirectory(initialdir=self.image_path_var.get() or None)
        if path:
            self.image_path_var.set(path)

    def select_sound_path(self):
        path = filedialog.askdirectory(initialdir=self.sound_path_var.get() or None)
        if path:
            self.sound_path_var.set(path)

    def start_action(self):
        """入力値を検証し、画像表示モードを開始する。"""
        # Auto Image がオフのときだけ画像フォルダが必須
        if not self.auto_image_var.get() and self.image_path_var.get() == "":
            messagebox.showerror("Error", "画像フォルダ(Image Path)を指定してください。")
            return
        if not ui.is_positive_int(self.interval_var.get()):
            messagebox.showerror("Error", "Display Interval には 1 以上の整数を入力してください。")
            return

        settings_manager.save_settings(
            auto_image=self.auto_image_var.get(),
            image_path=self.image_path_var.get(),
            interval=self.interval_var.get(),
            automatic_brightness=self.automatic_brightness_var.get(),
            show_time=self.show_time_var.get(),
            show_weather=self.show_weather_var.get(),
            show_train_schedule=self.show_train_schedule_var.get(),
            sound_path=self.sound_path_var.get(),
            sound_mode=self.sound_mode_var.get(),
        )
        self.root.destroy()
        image_mode_screen.create_screen()

    def back_action(self):
        self.root.destroy()
        home_screen.create_screen()


def create_screen():
    root = tk.Tk()
    ImageModeSettingScreen(root)
    root.mainloop()
