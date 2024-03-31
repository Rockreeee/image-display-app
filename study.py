import os
import random
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog
from tkinter import messagebox
from time import strftime, localtime
import csv

import start

root_after_id_1 = ""
root_after_id_2 = ""
root_after_id_3 = ""
brightness = 1.0

def cancel_root_after(root):
    root.after_cancel(root_after_id_1)
    root.after_cancel(root_after_id_2)
    root.after_cancel(root_after_id_3)


def create_study_setting_widgets():
    """開始画面を生成する関数"""
    root_start = tk.Tk()
    root_start.title("Study Display App")
    
    # 設定をロード
    study_file = start.load_settings(column=6)
    answer_interval = start.load_settings(column=7)
    change_interval = start.load_settings(column=8)
    
    # デフォルトの表示間隔を設定
    answer_interval_var = tk.StringVar()
    answer_interval_var.set(answer_interval)
    
    # デフォルトの表示間隔を設定
    change_interval_var = tk.StringVar()
    change_interval_var.set(change_interval)
    
    # 前回選択したファイルパスを設定
    path_var = tk.StringVar()
    path_var.set(study_file)

    # ファイル選択ダイアログを表示する関数
    def select_path():
        path = filedialog.askdirectory()
        if path:
            path_var.set(path)

    # 開始ボタンのアクション
    def start_action():
        study_file = path_var.get()
        answer_interval = int(answer_interval_var.get())
        change_interval = int(change_interval_var.get())

        # 設定を保存
        start.save_settings(study_file=study_file, study_answer_interval=answer_interval, study_change_interval=change_interval)

        root_start.destroy()

        try:
            create_time_study_widget(study_file, answer_interval, change_interval)
        except FileNotFoundError:
            messagebox.showerror("Error", "Study file not found!")
            create_study_setting_widgets()


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
    tk.Label(settings_frame, text="Study File(.csv):").grid(row=1, column=0, sticky="w")
    tk.Entry(settings_frame, textvariable=path_var).grid(row=1, column=1, sticky="w")
    tk.Button(settings_frame, text="Browse", command=select_path).grid(row=1, column=2, sticky="w")

    # 答え表示間隔
    tk.Label(settings_frame, text="Answer Interval (seconds):").grid(row=2, column=0, sticky="w")
    tk.Entry(settings_frame, textvariable=answer_interval_var).grid(row=2, column=1, sticky="w")

    # 切り替え表示間隔
    tk.Label(settings_frame, text="Change Interval (seconds):").grid(row=3, column=0, sticky="w")
    tk.Entry(settings_frame, textvariable=change_interval_var).grid(row=3, column=1, sticky="w")
    
    # スタートボタン
    start_button = tk.Button(settings_frame, text="Start", command=start_action)
    start_button.grid(row=4, columnspan=3, pady=10, sticky="nsew")
    
    # スペース
    study_label = tk.Label(root_start)
    study_label.grid(row=1, column=0)

    root_start.mainloop()


def create_time_study_widget(file, answer_interval, change_interval):
    root = tk.Tk()
    root.title("Study App")
    root.attributes("-fullscreen", True)
    root.configure(background='black')
    
    # 終了する時の関数
    def close_window(event):
        cancel_root_after(root)
        root.destroy()
        create_study_setting_widgets()
    
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

    create_time_widget(root)
    create_study_widget(root, file, answer_interval, change_interval)
    # show_image(root)


def create_time_widget(root):
    """時間を上半分に表示する関数"""

    # ウィンドウの幅と高さを取得
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 上半分の高さを計算
    half_screen_height = screen_height // 2

    # 日付と曜日を表示するラベルを作成
    date_label = tk.Label(root, font=('calibri', 50, 'bold'), bg='black', fg='white')
    date_label.pack(anchor='nw', padx=100, pady=50)

    # 時間を表示するラベルを作成
    time_label = tk.Label(root, font=('calibri', 200, 'bold'), bg='black', fg='white')
    time_label.pack(anchor='n')

    # 次の更新までの待機時間を計算する関数
    def calculate_wait_time():
        current_second = int(strftime('%S'))
        return (60 - current_second) * 1000  # 次の分の最初までのミリ秒数を返す

    # 日付と曜日、時間を更新する関数
    def update_time():
        global root_after_id_1

        current_time = strftime('%H:%M:%S')
        current_date = strftime('%Y-%m-%d %A', localtime())
        time_label.config(text=current_time)
        date_label.config(text=current_date)
        wait_time = calculate_wait_time() if strftime('%S') == '00' else 1000  # 次の分の最初までの待機時間を計算
        root_after_id_1 = root.after(wait_time, update_time)  # 次の更新まで待機

    update_time()  # 初回の呼び出し

    # ウィンドウの幅と高さを設定
    root.geometry(f"{screen_width}x{half_screen_height}+0+0")

def create_study_widget(root, file, answer_interval, change_interval):
    """英語と翻訳を下半分に表示する関数"""

    # ラベルの初期フォントサイズ
    study_font_size = 50
    translation_font_size = 30
    study_font_color = 'white'
    translation_font_color = 'white'

    study_label = tk.Label(root, text="", font=('calibri', study_font_size), bg='black', fg=study_font_color)
    study_label.pack(pady=50)

    translation_label = tk.Label(root, text="", font=('calibri', translation_font_size), bg='black', fg=translation_font_color)
    translation_label.pack()

    # 
    data = []
    random_data = ""

    # データをファイルから読み込む
    with open(file, newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        data.extend(row for row in csvreader)

    def adjust_font_color(color = ''):
        nonlocal study_font_color, translation_font_color
        # ウィンドウのサイズに合わせてフォントサイズを調整
        study_font_color = color
        translation_font_color = color
        study_label.config(fg=study_font_color)  # フォントの色と背景色を変更
        translation_label.config(fg=translation_font_color)  # フォントの色と背景色を変更

    def update_text():
        """英語と翻訳の更新を行う関数"""
        global root_after_id_2

        adjust_font_color('white')
        nonlocal random_data  # ローカル変数ではなく外部の変数を参照するためにnonlocalを使用
        random_data = random.choice(data)
        study_label.config(text=random_data[0])
        translation_label.config(text="")
        root_after_id_2 = root.after(answer_interval * 1000, lambda: update_translation(random_data))

    def update_translation(random_data):
        """翻訳の更新を行う関数"""
        global root_after_id_3

        translation_label.config(text=random_data[1])
        root_after_id_3 = root.after(change_interval * 1000, update_text)

    # 初回の呼び出し
    update_text()

    # ウィンドウサイズが変更されたときにフォントサイズを調整する
    def adjust_font_size(event):
        nonlocal study_font_size, translation_font_size
        # ウィンドウのサイズに合わせてフォントサイズを調整
        study_font_size = max(10, int(root.winfo_width() / 8))
        translation_font_size = max(10, int(root.winfo_width() / 10))
        study_label.config(font=('calibri', study_font_size))
        translation_label.config(font=('calibri', translation_font_size))


    # 暗記機能
    def got_it(event):
        try:
            data.remove(random_data)
            adjust_font_color('grey')
        except ValueError:
            pass
        
    root.bind("<space>", got_it)

    root.bind("<Configure>", adjust_font_size)

def show_image(root):
    image = "/Users/morimotoakihito/Desktop/image app/paintings/fime.jpg"
    img = Image.open(image)
    img_width, img_height = img.size
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    photo = ImageTk.PhotoImage(img)
    label = tk.Label(root)
    label.configure(image=photo)
    label.image = photo
    label.pack(fill=tk.BOTH, expand=True)