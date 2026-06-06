"""勉強モードの設定画面。

CSV の問題ファイルと、答え表示・問題切り替えのタイミングを設定し、
勉強モードを開始する。
"""

import tkinter as tk
from tkinter import filedialog, messagebox

import utils.settings_manager as settings_manager
import utils.ui as ui
import screens.home_screen as home_screen
import screens.study_mode_screen as study_mode_screen


class StudyModeSettingScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Study Display App")

        self.initialize_settings()
        self.create_widgets()
        # 説明文を含む全項目が収まるよう、内容に合わせてサイズ調整する
        ui.fit_window(self.root, min_width=600)

    def initialize_settings(self):
        settings = settings_manager.load_settings()
        self.study_file_var = tk.StringVar(value=settings.get("study_file"))
        self.answer_interval_var = tk.StringVar(value=settings.get("answer_interval"))
        self.change_interval_var = tk.StringVar(value=settings.get("change_interval"))

    def create_widgets(self):
        form = ui.SettingsForm(self.root)

        form.add_section("勉強モード (Study)")
        form.add_path(
            "Study File (.csv):", self.study_file_var, self.select_study_file,
            help_text="1列目に問題、2列目に答えを書いた CSV ファイル。",
        )
        form.add_entry(
            "Answer Interval (seconds):", self.answer_interval_var,
            help_text="問題が出てから答えが表示されるまでの時間(秒)。",
        )
        form.add_entry(
            "Change Interval (seconds):", self.change_interval_var,
            help_text="答えが出てから次の問題に変わるまでの時間(秒)。",
        )

        form.add_action_buttons(self.back_action, self.start_action)

    def select_study_file(self):
        path = filedialog.askopenfilename(
            title="Select a study file",
            initialdir=self.study_file_var.get() or None,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.study_file_var.set(path)

    def start_action(self):
        """入力値を検証し、勉強モードを開始する。"""
        if self.study_file_var.get() == "":
            messagebox.showerror("Error", "問題ファイル(Study File)を指定してください。")
            return
        if not ui.is_positive_int(self.answer_interval_var.get()) or \
                not ui.is_positive_int(self.change_interval_var.get()):
            messagebox.showerror("Error", "各 Interval には 1 以上の整数を入力してください。")
            return

        settings_manager.save_settings(
            study_file=self.study_file_var.get(),
            answer_interval=self.answer_interval_var.get(),
            change_interval=self.change_interval_var.get(),
        )
        self.root.destroy()
        study_mode_screen.create_screen()

    def back_action(self):
        self.root.destroy()
        home_screen.create_screen()


def create_screen():
    root = tk.Tk()
    StudyModeSettingScreen(root)
    root.mainloop()
