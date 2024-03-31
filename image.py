import os
import random
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog
from tkinter import messagebox

import start

root_after_id = ""
brightness = 1.0

def cancel_root_after(root):
    root.after_cancel(root_after_id)

def create_image_setting_widgets():
    """開始画面を生成する関数"""
    root_start = tk.Tk()
    root_start.title("Image Display App")
    
    # 設定をロード
    image_directory = start.load_settings(column=1)
    interval = start.load_settings(column=2)
    show_margin = start.load_settings(column=3)
    
    # デフォルトの表示間隔を設定
    interval_var = tk.StringVar()
    interval_var.set(interval)
    
    # 前回選択したファイルパスを設定
    path_var = tk.StringVar()
    path_var.set(image_directory)
    
    # 余白表示のON/OFF状態を保持する変数
    show_margin_var = tk.BooleanVar()
    show_margin_var.set(show_margin)

    # ファイル選択ダイアログを表示する関数
    def select_path():
        path = filedialog.askdirectory()
        if path:
            path_var.set(path)

    # 開始ボタンのアクション
    def start_action():
        image_directory = path_var.get()
        interval = int(interval_var.get())
        show_margin = show_margin_var.get()

        # 設定を保存
        start.save_settings(image_directory=image_directory, image_interval=str(interval), show_margin=show_margin)

        root_start.destroy()

        try:
            show_random_image(image_directory, interval, show_margin)
        except FileNotFoundError:
            messagebox.showerror("Error", "Image file not found!")
            create_image_setting_widgets()


    # 戻るボタンのアクション
    def back_action():
        root_start.destroy()
        start.create_start_widget()

    settings_frame = tk.Frame(root_start)
    settings_frame.grid(row=0, column=0, sticky="w")
    
    # 戻るボタン
    back_button = tk.Button(settings_frame, text="<<", command=back_action)
    back_button.grid(row=0, pady=10, sticky="nsew")

    # ファイル場所
    tk.Label(settings_frame, text="Image Directory:").grid(row=1, column=0, sticky="w")
    tk.Entry(settings_frame, textvariable=path_var).grid(row=1, column=1, sticky="w")
    tk.Button(settings_frame, text="Browse", command=select_path).grid(row=1, column=2, sticky="w")

    # 切り替え間隔
    tk.Label(settings_frame, text="Display Interval (seconds):").grid(row=2, column=0, sticky="w")
    tk.Entry(settings_frame, textvariable=interval_var).grid(row=2, column=1, sticky="w")
    
    # 余白表示のチェックボックス
    tk.Label(settings_frame, text="Show Margin").grid(row=3, column=0, sticky="w")
    tk.Checkbutton(settings_frame, variable=show_margin_var).grid(row=3, column=1, sticky="w")
    
    # スタートボタン
    start_button = tk.Button(settings_frame, text="Start", command=start_action)
    start_button.grid(row=4, columnspan=3, pady=10, sticky="nsew")
    
    # スペース
    image_label = tk.Label(root_start)
    image_label.grid(row=1, column=0)

    root_start.mainloop()


def show_random_image(directory, interval, margin):
    """ランダムに画像を表示する関数"""
    image_files = [f for f in os.listdir(directory) if f.endswith(('.jpg', '.jpeg', '.png'))]
    root = tk.Tk()
    root.title("Image Display App")
    root.attributes("-fullscreen", True)
    root.configure(background='white')
    
    # 終了する時の関数
    def close_window(event):
        cancel_root_after(root)
        root.destroy()
        create_image_setting_widgets()
    
    # 終了する時のキーバインド
    root.bind("<Escape>", close_window)

    # 明るさを調整する関数
    def brightness_adjustment(event):
        global brightness
        brightness -= 0.2
        if brightness < 0:
            brightness = 1
        root.attributes('-alpha', brightness)
    
    # 明るさを調整するキーバインド
    root.bind("<b>", brightness_adjustment)
    
    label = tk.Label(root, bg='white')
    label.pack(fill=tk.BOTH, expand=True)
    
    def show_next_image():
        global root_after_id
        if margin:
            show_image_with_margin()
        else:
            show_image_without_margin()
        root_after_id = root.after(interval * 1000, show_next_image)

    def show_image_with_margin():
        random_image = random.choice(image_files)
        image_path = os.path.join(directory, random_image)
        img = Image.open(image_path)
        img_width, img_height = img.size
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        constant_margin = 200
        
        if img_width > screen_width or img_height > screen_height:
            ratio = min(screen_width / img_width, screen_height / img_height)
            new_width = int(img_width * ratio) - constant_margin
            new_height = int(img_height * ratio) - constant_margin
            img = img.resize((new_width, new_height), Image.ANTIALIAS)
        
        photo = ImageTk.PhotoImage(img)
        label.configure(image=photo)
        label.image = photo

    def show_image_without_margin():
        random_image = random.choice(image_files)
        image_path = os.path.join(directory, random_image)
        img = Image.open(image_path)
        img_width, img_height = img.size
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        ratio = max(screen_width / img_width, screen_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        img = img.resize((new_width, new_height), Image.ANTIALIAS)

        # 画像を表示するラベルを作成し、中央に配置する
        photo = ImageTk.PhotoImage(img)
        label.configure(image=photo)
        label.image = photo

    show_next_image()

    def next_image(event):
        if margin:
            show_image_with_margin()
        else:
            show_image_without_margin()
        
    root.bind("<space>", next_image)

    root.mainloop()

