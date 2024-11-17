import tkinter as tk
import screens.image_mode_setting_screen as image_mode_setting_screen
import screens.video_mode_setting_screen as video_mode_setting_screen
import screens.study_mode_setting_screen as study_mode_setting_screen
import utils.settings_manager as settings_manager

class HomeScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Select Mode")
        self.center_window(200, 200)
        
        # ラジオボタンの選択値を保持する変数
        settings = settings_manager.load_settings()
        self.mode = tk.StringVar(value=settings.get("mode"))

        # UIパーツを設定
        self.create_widgets()

    def center_window(self, width, height):
        """大きさを調整し、ウィンドウを画面中央に配置"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """モード選択画面のUI要素を作成"""
        tk.Label(self.root, text="Select Mode:").pack(pady=10)
        self.create_radio_buttons()
        tk.Button(self.root, text="Confirm", command=self.confirm_mode).pack(pady=10)

    def create_radio_buttons(self):
        """ラジオボタンを作成"""
        modes = [("Image", "Image"), ("Study", "Study")]
        # modes = [("Image", "Image"), ("Video", "Video"), ("Study", "Study")]
        for mode_name, mode_value in modes:
            tk.Radiobutton(self.root, text=mode_name, variable=self.mode, value=mode_value).pack()

    def confirm_mode(self):
        """選択されたモードを確定し処理を呼び出す"""
        selected_mode = self.mode.get()
        settings_manager.save_settings(mode=selected_mode)
        
        self.root.destroy()
        if selected_mode == "Image":
            image_mode_setting_screen.create_screen()
        # if selected_mode == "Video":
        #     video_mode_setting_screen.create_screen()
        elif selected_mode == "Study":
            study_mode_setting_screen.create_screen()

def create_screen():
    root = tk.Tk()
    HomeScreen(root)
    root.mainloop()