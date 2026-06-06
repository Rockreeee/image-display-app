"""モード選択画面。

起動時に最初に表示され、画像モード/勉強モードを選択して
それぞれの設定画面へ進む。
"""

import tkinter as tk

import utils.settings_manager as settings_manager
import utils.ui as ui
import screens.image_mode_setting_screen as image_mode_setting_screen
import screens.study_mode_setting_screen as study_mode_setting_screen

# 選択肢(表示名, 保存値)
MODES = [("Image", "Image"), ("Study", "Study")]


class HomeScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Select Mode")
        ui.center_window(self.root, 200, 200)

        settings = settings_manager.load_settings()
        self.mode = tk.StringVar(value=settings.get("mode"))

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Select Mode:").pack(pady=10)
        for mode_name, mode_value in MODES:
            tk.Radiobutton(
                self.root, text=mode_name, variable=self.mode, value=mode_value
            ).pack()
        tk.Button(self.root, text="Confirm", command=self.confirm_mode).pack(pady=10)

    def confirm_mode(self):
        """選択モードを保存し、対応する設定画面を開く。"""
        selected_mode = self.mode.get()
        settings_manager.save_settings(mode=selected_mode)
        self.root.destroy()

        if selected_mode == "Image":
            image_mode_setting_screen.create_screen()
        elif selected_mode == "Study":
            study_mode_setting_screen.create_screen()


def create_screen():
    root = tk.Tk()
    HomeScreen(root)
    root.mainloop()
