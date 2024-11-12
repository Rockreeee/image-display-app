import tkinter as tk
from tkinter import filedialog, messagebox
import utils.settings_manager as settings_manager
import screens.home_screen as home_screen
import screens.study_mode_screen as study_mode_screen

class StudyModeSettingScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Study Display App")
        self.center_window(600, 200)

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
        self.study_file_var = tk.StringVar(value=settings.get('study_file'))
        self.answer_interval_var = tk.StringVar(value=settings.get('answer_interval'))
        self.change_interval_var = tk.StringVar(value=settings.get('change_interval'))

    def create_widgets(self):
        settings_frame = tk.Frame(self.root)
        settings_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # ラベル・エントリ・ボタンの設定
        self.create_label_entry_button(settings_frame, "Study File(.csv): *", self.study_file_var, self.select_study_file, row=0)
        self.create_label_entry(settings_frame, "Answer Interval (seconds): *", self.answer_interval_var, row=1)
        self.create_label_entry(settings_frame, "Change Interval (seconds): *", self.change_interval_var, row=2)

        # アクションボタン
        tk.Button(settings_frame, text="<< Back", command=self.back_action).grid(row=9, column=0, pady=10)
        tk.Button(settings_frame, text="Start", command=self.start_action).grid(row=9, column=2, pady=10)

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

    def select_study_file(self):
        """勉強ファイル選択ダイアログを表示"""
        path = filedialog.askopenfilename(
            title="Select a sound file",
            initialdir = self.study_file_var
        )
        if path:
            self.study_file_var.set(path)

    def start_action(self):
        """開始ボタンのアクション"""
        # 必須項目の確認
        if self.study_file_var.get() == "" or self.is_invalide_value(self.answer_interval_var.get()) or self.is_invalide_value(self.change_interval_var.get()):
            messagebox.showerror("Error", "Invalid value!")
            return
        settings = {
            "study_file": self.study_file_var.get(),
            "answer_interval": self.answer_interval_var.get(),
            "change_interval": self.change_interval_var.get()
        }

        # 設定を保存
        settings_manager.save_settings(**settings)
        self.root.destroy()

        study_mode_screen.create_screen()

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
    StudyModeSettingScreen(root)
    root.mainloop()