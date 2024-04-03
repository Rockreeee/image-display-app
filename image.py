import os
import random
import tkinter as tk
from PIL import Image, ImageEnhance, ImageTk
from tkinter import filedialog
from tkinter import messagebox
import datetime

import start

# 設定項目
image_directory = ""
interval = 0 
show_margin = False
automatic_brightness = False

root_after_id_1 = ""
root_after_id_2 = ""
root_after_id_3 = ""
label_brightness = 1.0

image_path = ""
image_brightness = 1.0

def cancel_root_after(root):
    root.after_cancel(root_after_id_1)

    if root_after_id_2 != "":
        root.after_cancel(root_after_id_2)

    if root_after_id_3 != "":
        root.after_cancel(root_after_id_3)

def create_image_setting_widgets():
    """開始画面を生成する関数"""
    root_start = tk.Tk()
    root_start.title("Image Display App")
    
    # 設定をロード
    image_directory = start.load_settings(column=1)
    interval = start.load_settings(column=2)
    show_margin = start.load_settings(column=3)
    automatic_brightness = start.load_settings(column=4)
    
    # デフォルトの表示間隔を設定
    interval_var = tk.StringVar()
    interval_var.set(interval)
    
    # 前回選択したファイルパスを設定
    path_var = tk.StringVar()
    path_var.set(image_directory)
    
    # 余白表示のON/OFF状態を保持する変数
    show_margin_var = tk.BooleanVar()
    show_margin_var.set(show_margin)
    
    # 余白表示のON/OFF状態を保持する変数
    automatic_brightness_var = tk.BooleanVar()
    automatic_brightness_var.set(automatic_brightness)

    # ファイル選択ダイアログを表示する関数
    def select_path():
        path = filedialog.askdirectory()
        if path:
            path_var.set(path)

    # 開始ボタンのアクション
    def start_action():
        global image_directory
        global interval
        global show_margin
        global automatic_brightness
        
        image_directory = path_var.get()
        interval = int(interval_var.get())
        show_margin = show_margin_var.get()
        automatic_brightness = automatic_brightness_var.get()

        # 設定を保存
        start.save_settings(image_directory=image_directory, image_interval=str(interval), show_margin=show_margin, automatic_brightness=automatic_brightness)

        root_start.destroy()

        try:
            show_random_image()
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
    
    # 自動輝度調整のチェックボックス
    tk.Label(settings_frame, text="Automatic Brightness").grid(row=4, column=0, sticky="w")
    tk.Checkbutton(settings_frame, variable=automatic_brightness_var).grid(row=4, column=1, sticky="w")
    
    # スタートボタン
    start_button = tk.Button(settings_frame, text="Start", command=start_action)
    start_button.grid(row=5, columnspan=3, pady=10, sticky="nsew")
    
    # スペース
    image_label = tk.Label(root_start)
    image_label.grid(row=1, column=0)

    root_start.mainloop()


def show_random_image():
    """ランダムに画像を表示する関数"""
    image_files = [f for f in os.listdir(image_directory) if f.endswith(('.jpg', '.jpeg', '.png'))]
    root = tk.Tk()
    root.title("Image Display App")
    
    root.configure(background='white')
    

    # 終了する時の関数
    def close_window(event):
        cancel_root_after(root)
        root.destroy()
        create_image_setting_widgets()
    
    # 終了する時のキーバインド
    root.bind("<Escape>", close_window)


    # 明るさを調整する関数
    def label_brightness_adjustment(event):
        global label_brightness
        label_brightness -= 0.2
        if label_brightness < 0:
            label_brightness = 1
        label.config(bg=f'#{int(label_brightness*255):02x}{int(label_brightness*255):02x}{int(label_brightness*255):02x}')  # 背景色を調整
    
    # 明るさを調整するキーバインド
    root.bind("<b>", label_brightness_adjustment)


    # 明るさを調整する関数
    def image_brightness_adjustment(event):
        global image_brightness

        image_brightness -= 0.2
        if image_brightness < 0:
            image_brightness = 1

        if show_margin:
            show_image_with_margin()
        else:
            show_image_without_margin()

    # 明るさを調整するキーバインド
    root.bind("<v>", image_brightness_adjustment)


    # ウィンドウの大きさを調整
    def toggle_fullscreen(event=None):
        root.attributes("-fullscreen", not root.attributes("-fullscreen"))

    # キーイベントをバインドしてフルスクリーン表示の切り替えを有効にする
    root.bind("<f>", toggle_fullscreen)
    

    label = tk.Label(root, bg='white')
    label.pack(fill=tk.BOTH, expand=True)
        
    def calculate_time_next_trigger(target_hour, target_minute):
        # 現在の時刻を取得
        current_time = datetime.datetime.now()

        # 次に発動させたい時間を計算
        target_time = current_time.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

        # 現在の時刻から次の発動までの時間を計算
        delta_time = target_time - current_time

        total_seconds = delta_time.total_seconds()

        return total_seconds

    # 自動明るさ調整
    def automatic_brightness_adjustment():
        global root_after_id_2
        global root_after_id_3
        global image_brightness
        global label_brightness

        # 朝、夜までの時間計算
        time_to_morning = calculate_time_next_trigger(6, 0)
        time_to_night = calculate_time_next_trigger(21, 0)

        # すでに夜の時
        if time_to_night < 0 or time_to_morning > 0:
            print("今は夜です")
            image_brightness = 0.2
            label_brightness = 0
            label.config(bg=f'#{int(label_brightness*255):02x}{int(label_brightness*255):02x}{int(label_brightness*255):02x}')  # 背景色を調整
        else:
            print("今は昼です")
            image_brightness = 1.0
            label_brightness = 1.0
            label.config(bg=f'#{int(label_brightness*255):02x}{int(label_brightness*255):02x}{int(label_brightness*255):02x}')  # 背景色を調整

        if time_to_morning < 0:
            time_to_morning += 86400

        if time_to_night < 0:
            time_to_night += 86400

        # 予約
        print("画面が明るくなるまで：", int(time_to_morning))
        print("画面が暗くなるまで：", int(time_to_night))
        root_after_id_2 = root.after(int(time_to_morning) * 1000, automatic_brightness_adjustment)
        root_after_id_3 = root.after(int(time_to_night) * 1000, automatic_brightness_adjustment)


    if automatic_brightness:
        automatic_brightness_adjustment()


    # ランダムな御像を選ぶ関数
    def select_random_image():
        global image_path

        random_image = random.choice(image_files)
        image_path = os.path.join(image_directory, random_image)
        if show_margin:
            show_image_with_margin()
        else:
            show_image_without_margin()


    def show_image_with_margin():
        global image_brightness

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
        
        # 明るさを調整するためのBrightnessオブジェクトを作成し、ファクターを設定
        enhancer = ImageEnhance.Brightness(img)
        adjusted_image = enhancer.enhance(image_brightness)

        # 画像を表示するラベルに設定
        photo = ImageTk.PhotoImage(adjusted_image)
        label.configure(image=photo)
        label.image = photo


    def show_image_without_margin():
        global image_brightness

        img = Image.open(image_path)
        img_width, img_height = img.size
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        ratio = max(screen_width / img_width, screen_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        img = img.resize((new_width, new_height), Image.ANTIALIAS)
        
        # 明るさを調整するためのBrightnessオブジェクトを作成し、ファクターを設定
        enhancer = ImageEnhance.Brightness(img)
        adjusted_image = enhancer.enhance(image_brightness)

        # 画像を表示するラベルを作成し、中央に配置する
        photo = ImageTk.PhotoImage(adjusted_image)
        label.configure(image=photo)
        label.image = photo
    

    def show_next_image():
        global root_after_id_1
        select_random_image()
        root_after_id_1 = root.after(interval * 1000, show_next_image)

    show_next_image()


    # 次のイメージにする関数
    def next_image(event):
        select_random_image()
        
    root.bind("<space>", next_image)


    root.mainloop()

    