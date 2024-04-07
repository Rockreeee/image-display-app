import os
import random
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog
from tkinter import messagebox

import image
import movie
import study

# 設定ファイルのパス
SETTINGS_FILE = ".settings.txt"

def load_settings(column = int):
    """設定ファイルから設定を読み込む関数"""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            lines = f.readlines()
            
            # mode
            if column == 0:
                try:
                    return lines[0].strip()
                except IndexError:
                    return "Image"
            
            # image_directory
            if column == 1:
                try:
                    return lines[1].strip()
                except IndexError:
                    return ""
            
            # image_interval
            if column == 2:
                try:
                    return lines[2].strip()
                except IndexError:
                    return "60"
            
            # margin
            if column == 3:
                try:
                    return lines[3].strip()
                except IndexError:
                    return False
            
            # automatic brightness
            if column == 4:
                try:
                    return lines[4].strip()
                except IndexError:
                    return False
            
            # time
            if column == 5:
                try:
                    return lines[5].strip()
                except IndexError:
                    return False
            
            # weather
            if column == 6:
                try:
                    return lines[6].strip()
                except IndexError:
                    return False
            
            # video_interval
            if column == 7:
                try:
                    return lines[7].strip()
                except IndexError:
                    return "60"
            
            # video_interval
            if column == 8:
                try:
                    return lines[8].strip()
                except IndexError:
                    return "60"
            
            # study_directory
            if column == 9:
                try:
                    return lines[9].strip()
                except IndexError:
                    return ""
            
            # study_answer_interval
            if column == 10:
                try:
                    return lines[10].strip()
                except IndexError:
                    return "2"
            
            # study_change_interval
            if column == 11:
                try:
                    return lines[11].strip()
                except IndexError:
                    return "5"

    else:
        # デフォルトの値
        if column == 0:
            return "Image"
        if column == 1:
            return ""
        if column == 2:
            return "60"
        if column == 3:
            return False
        if column == 4:
            return False
        if column == 5:
            return False
        if column == 6:
            return False
        if column == 7:
            return ""
        if column == 8:
            return "60"
        if column == 9:
            return ""
        if column == 10:
            return "2"
        if column == 11:
            return "5"

def save_settings(mode=None, image_directory=None,
                image_interval=None, show_margin=None, 
                automatic_brightness=None, show_time=None, 
                show_weather=None, 
                video_directory=None, video_interval=None,
                study_file=None, study_answer_interval=None, 
                study_change_interval=None):
    """設定を設定ファイルに保存する関数"""
    if mode == None:
        mode = load_settings(column=0)

    if image_directory == None:
        image_directory = load_settings(column=1)

    if image_interval == None:
        image_interval = load_settings(column=2)

    if show_margin == None:
        show_margin = load_settings(column=3)

    if automatic_brightness == None:
        automatic_brightness = load_settings(column=4)

    if show_time == None:
        show_time = load_settings(column=5)

    if show_weather == None:
        show_weather = load_settings(column=6)

    if video_directory == None:
        video_directory = load_settings(column=7)

    if video_interval == None:
        video_interval = load_settings(column=8)

    if study_file == None:
        study_file = load_settings(column=9)

    if study_answer_interval == None:
        study_answer_interval = load_settings(column=10)

    if study_change_interval == None:
        study_change_interval = load_settings(column=11)

    with open(SETTINGS_FILE, "w") as f:
        # 書き込む
        f.write(mode + "\n")
        f.write(image_directory + "\n")
        f.write(image_interval + "\n")
        f.write(str(show_margin) + "\n")
        f.write(str(automatic_brightness) + "\n")
        f.write(str(show_time) + "\n")
        f.write(str(show_weather) + "\n")
        f.write(video_directory + "\n")
        f.write(video_interval + "\n")
        f.write(study_file + "\n")
        f.write(str(study_answer_interval) + "\n")
        f.write(str(study_change_interval) + "\n")

def create_start_widget():
    # 新しいウィンドウを作成
    mode_window = tk.Tk()
    mode_window.title("Select Mode")

    # ウィンドウの幅と高さを指定
    mode_window.geometry("200x200") 

    # ラベルを作成
    label = tk.Label(mode_window, text="Select Mode:")
    label.pack(pady=10)

    # ラジオボタンの値を保持する変数を作成
    mode_var = tk.StringVar()

    # デフォルトのモードを設定
    mode = load_settings(column=0)
    mode_var.set(mode)

    # ラジオボタンAを作成
    mode_a = tk.Radiobutton(mode_window, text="Image", variable=mode_var, value="Image")
    mode_a.pack()

    # ラジオボタンBを作成
    mode_b = tk.Radiobutton(mode_window, text="Movie", variable=mode_var, value="Movie")
    mode_b.pack()

    # ラジオボタンCを作成
    mode_c = tk.Radiobutton(mode_window, text="Study", variable=mode_var, value="Study")
    mode_c.pack()

    def confirm_mode():
        # 選択されたモードを取得
        selected_mode = mode_var.get()

        # モード選択ウィンドウを閉じる
        mode_window.destroy()

        # 設定を保存
        save_settings(mode=selected_mode)
        
        if selected_mode == "Image":
            image.create_image_setting_widgets()
        elif selected_mode == "Movie":
            movie.create_movie_setting_widgets()
        elif selected_mode == "Study":
            study.create_study_setting_widgets()


    # 確認ボタンを作成
    confirm_button = tk.Button(mode_window, text="Confirm", command=confirm_mode)
    confirm_button.pack(pady=10)

    mode_window.mainloop()


if __name__ == "__main__":
    create_start_widget()

