import tkinter as tk
from tkinter import filedialog, messagebox
import utils.settings_manager as settings_manager
import screens.home_screen as home_screen
import screens.image_mode_screen as image_mode_screen

class ImageModeSettingScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Display App")
        self.center_window(600, 350)

        # 設定変数の初期化
        self.initialize_settings()
        self.create_widgets()

    def center_window(self, width, height):
        """ウィンドウを画面中央に配置"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def initialize_settings(self):
        # 設定をロードし、各変数に設定
        settings = settings_manager.load_settings()
        self.auto_image_var = tk.BooleanVar(value=settings.get('auto_image'))
        self.image_path_var = tk.StringVar(value=settings.get('image_path'))
        self.interval_var = tk.StringVar(value=settings.get('interval'))
        self.automatic_brightness_var = tk.BooleanVar(value=settings.get('automatic_brightness'))
        self.show_time_var = tk.BooleanVar(value=settings.get('show_time'))
        self.show_weather_var = tk.BooleanVar(value=settings.get('show_weather'))
        self.show_train_schedule_var = tk.BooleanVar(value=settings.get('show_train_schedule'))
        self.sound_path_var = tk.StringVar(value=settings.get('sound_path'))
        self.sound_mode_var = tk.StringVar(value=settings.get('sound_mode'))

    def create_widgets(self):
        settings_frame = tk.Frame(self.root)
        settings_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # ラベル・エントリ・ボタンの設定
        self.create_checkbutton(settings_frame, "Auto Image", self.auto_image_var, row=0)
        self.create_label_entry_button(settings_frame, "Image Path:", self.image_path_var, self.select_image_path, row=1)
        self.create_label_entry(settings_frame, "Display Interval (seconds): *", self.interval_var, row=2)
        self.create_checkbutton(settings_frame, "Automatic Brightness Adjustment", self.automatic_brightness_var, row=3)
        self.create_checkbutton(settings_frame, "Show Clock", self.show_time_var, row=4)
        self.create_checkbutton(settings_frame, "Show Weather", self.show_weather_var, row=5)
        self.create_checkbutton(settings_frame, "Show Train Schedule", self.show_train_schedule_var, row=6)
        self.create_label_entry_button(settings_frame, "Sound Path:", self.sound_path_var, self.select_sound_path, row=7)
        self.create_radiobutton(settings_frame, "Sound Off", self.sound_mode_var, "0", row=8)
        self.create_radiobutton(settings_frame, "Sound On", self.sound_mode_var, "1", row=9)
        self.create_radiobutton(settings_frame, "Morning Sound Only", self.sound_mode_var, "2", row=10)

        # アクションボタン
        tk.Button(settings_frame, text="<< Back", command=self.back_action).grid(row=11, column=0, pady=10)
        tk.Button(settings_frame, text="Start", command=self.start_action).grid(row=11, column=2, pady=10)

    def create_label_entry_button(self, frame, text, variable, command, row):
        """ラベル、エントリ、ボタンのウィジェットを作成"""
        tk.Label(frame, text=text).grid(row=row, column=0, sticky="w")
        tk.Entry(frame, textvariable=variable).grid(row=row, column=1, sticky="ew")
        tk.Button(frame, text="Browse", command=command).grid(row=row, column=2)

    def create_label_entry(self, frame, text, variable, row):
        """ラベルとエントリのウィジェットを作成"""
        tk.Label(frame, text=text).grid(row=row, column=0, sticky="w")
        tk.Entry(frame, textvariable=variable).grid(row=row, column=1, columnspan=2, sticky="ew")

    def create_checkbutton(self, frame, text, variable, row):
        """チェックボックスのウィジェットを作成"""
        tk.Label(frame, text=text).grid(row=row, column=0, sticky="w")
        tk.Checkbutton(frame, variable=variable).grid(row=row, column=1, sticky="w")

    def create_radiobutton(self, frame, text, variable, value, row):
        """ラジオボタンのウィジェットを作成"""
        tk.Label(frame, text=text).grid(row=row, column=0, sticky="w")
        tk.Radiobutton(frame, variable=variable, value=value).grid(row=row, column=1, sticky="w")


    def select_image_path(self):
        """画像ファイル選択ダイアログを表示"""
        path = filedialog.askdirectory(initialdir=self.image_path_var)
        if path:
            self.image_path_var.set(path)

    def select_sound_path(self):
        """サウンドファイル選択ダイアログを表示"""
        path = filedialog.askdirectory(initialdir=self.sound_path_var)
        if path:
            self.sound_path_var.set(path)

    def start_action(self):
        """開始ボタンのアクション"""
        # 必須項目の確認
        if self.image_path_var.get() == "" or self.is_invalide_value(self.interval_var.get()):
            messagebox.showerror("Error", "Invalid value!")
            return

        settings = {
            "auto_image": self.auto_image_var.get(),
            "image_path": self.image_path_var.get(),
            "interval": self.interval_var.get(),
            "automatic_brightness": self.automatic_brightness_var.get(),
            "show_time": self.show_time_var.get(),
            "show_weather": self.show_weather_var.get(),
            "show_train_schedule": self.show_train_schedule_var.get(),
            "sound_path": self.sound_path_var.get(),
            "sound_mode": self.sound_mode_var.get(),
        }

        # 設定を保存
        settings_manager.save_settings(**settings)
        self.root.destroy()

        image_mode_screen.create_screen()

    def back_action(self):
        """戻るボタンのアクション"""
        self.root.destroy()
        home_screen.create_screen()

    def is_invalide_value(self, string_value):
        try:
            int_value = int(string_value)
            if int_value == 0:
                return True
            return False
        except ValueError:
            return True

def create_screen():
    root = tk.Tk()
    ImageModeSettingScreen(root)
    root.mainloop()