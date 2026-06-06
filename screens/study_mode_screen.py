"""勉強モードの表示画面。

時計とともに、CSV から読み込んだ問題をランダムに表示する。一定時間後に
答えを表示し、さらに一定時間後に次の問題へ。Space キーで覚えた問題を
ループから除外でき、すべて覚え終わると完了メッセージを出す。
"""

import tkinter as tk
from tkinter import messagebox
from time import strftime, localtime
import csv
import random

import utils.settings_manager as settings_manager
import screens.study_mode_setting_screen as study_mode_setting_screen
from screens.mixins import WindowControlsMixin


class StudyModeScreen(WindowControlsMixin):
    def __init__(self, root):
        self.root = root
        self.root.title("Study Display App")
        self.root.configure(background="black")
        self.brightness = 1.0

        self.initialize_settings()
        self.set_keybinding()
        self.create_widgets()

    def initialize_settings(self):
        settings = settings_manager.load_settings()
        self.study_file = settings.get("study_file")
        self.answer_interval = int(settings.get("answer_interval"))
        self.change_interval = int(settings.get("change_interval"))

    def set_keybinding(self):
        self.root.bind("<Escape>", self.close_window)
        self.root.bind("<q>", self.close_window)
        self.root.bind("<f>", self.toggle_fullscreen)
        self.root.bind("<h>", self.toggle_cursor)
        self.root.bind("<b>", self.brightness_adjustment)
        self.root.bind("<space>", self.remember)

    # --- キーバインド処理 ---
    def close_window(self, event=None):
        self.cancel_root_after()
        self.root.destroy()
        study_mode_setting_screen.create_screen()

    def brightness_adjustment(self, event=None):
        """画面全体の明るさ(透明度)を一段階下げる。0 を下回ったら元に戻す。"""
        self.brightness -= 0.2
        if self.brightness < 0:
            self.brightness = 1
        self.root.attributes("-alpha", self.brightness)

    def remember(self, event=None):
        """表示中の問題を「覚えた」としてループから除外する。"""
        try:
            self.data.remove(self.random_data)
            self.study_label.config(fg="grey")
            self.translation_label.config(fg="grey")
        except ValueError:
            pass

    # --- UI 作成 ---
    def create_widgets(self):
        self.show_clock_widget()
        self.show_study_widget()

    def show_clock_widget(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        date_font_size = screen_width // 20
        time_font_size = screen_width // 8

        self.date_label = tk.Label(self.root, font=("calibri", date_font_size, "bold"), bg="black", fg="white")
        self.date_label.pack(pady=(int(screen_height * 0.2), 0))
        self.time_label = tk.Label(self.root, font=("calibri", time_font_size, "bold"), bg="black", fg="white")
        self.time_label.pack(pady=(int(screen_height * 0.05), 0))

        self.update_time()

    def update_time(self):
        self.time_label.config(text=strftime("%H:%M:%S"))
        self.date_label.config(text=strftime("%Y-%m-%d %A", localtime()))
        self.root_after_id_time = self.root.after(1000, self.update_time)

    def show_study_widget(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        font_size = screen_width // 15

        self.study_label = tk.Label(self.root, text="", font=("calibri", font_size), bg="black", fg="white")
        self.translation_label = tk.Label(self.root, text="", font=("calibri", font_size), bg="black", fg="white")
        self.study_label.pack(pady=(int(screen_height * 0.05), 0))
        self.translation_label.pack(pady=(int(screen_height * 0.05), 0))

        # CSV を読み込む(1列目: 問題, 2列目: 答え)
        with open(self.study_file, newline="", encoding="utf-8") as csvfile:
            self.data = list(csv.reader(csvfile))

        self.update_question()

    def update_question(self):
        """新しい問題をランダムに表示する。すべて覚え終わったら完了。"""
        self.study_label.config(fg="white")
        self.translation_label.config(fg="white")

        if len(self.data) == 0:
            self.cancel_root_after()
            self.root.destroy()
            study_mode_setting_screen.create_screen()
            messagebox.showerror("Complete", "You got it!")
            return

        self.random_data = random.choice(self.data)
        self.study_label.config(text=self.random_data[0])
        self.translation_label.config(text="")
        self.root_after_id_question = self.root.after(self.answer_interval * 1000, self.update_answer)

    def update_answer(self):
        """答えを表示し、一定時間後に次の問題へ進む。"""
        self.translation_label.config(text=self.random_data[1])
        self.root_after_id_answer = self.root.after(self.change_interval * 1000, self.update_question)

    def cancel_root_after(self):
        """予約済みの after コールバックをすべてキャンセルする。"""
        for attr in ("root_after_id_time", "root_after_id_question", "root_after_id_answer"):
            if hasattr(self, attr):
                self.root.after_cancel(getattr(self, attr))


def create_screen():
    root = tk.Tk()
    try:
        StudyModeScreen(root)
        root.mainloop()
    except FileNotFoundError:
        root.destroy()
        messagebox.showerror("Error", "Study file not found!")
        study_mode_setting_screen.create_screen()
