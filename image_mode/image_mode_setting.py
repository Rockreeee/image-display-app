import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import main
import load_and_save_data as ls
import image_mode.image_mode as image_mode

root_start = None

image_path_var = None
interval_var = None
show_margin_var = None
automatic_brightness_var = None
show_time_var = None
show_weather_var = None
sound_path_var = None
sound_mode_var = None
morning_sound_mode_var = None

# 開始画面を生成する関数
def create_image_setting_widgets():

    global root_start
    global image_path_var
    global interval_var
    global show_margin_var
    global automatic_brightness_var
    global show_time_var
    global show_weather_var
    global sound_path_var
    global sound_mode_var
    global morning_sound_mode_var

    root_start = tk.Tk()
    root_start.title("Image Display App")
    
    # 設定をロード
    image_path = ls.load_settings(column=1)
    interval = ls.load_settings(column=2)
    show_margin = ls.load_settings(column=3)
    automatic_brightness = ls.load_settings(column=4)
    show_time = ls.load_settings(column=5)
    show_weather = ls.load_settings(column=6)
    sound_path = ls.load_settings(column=7)
    sound_mode = ls.load_settings(column=8)
    morning_sound_mode = ls.load_settings(column=9)
    
    # デフォルトの表示間隔を設定
    interval_var = tk.StringVar()
    interval_var.set(interval)
    
    # 前回選択したファイルパスを設定
    image_path_var = tk.StringVar()
    image_path_var.set(image_path)
    
    # 余白表示のON/OFF状態を保持する変数
    show_margin_var = tk.BooleanVar()
    show_margin_var.set(show_margin)
    
    # 余白表示のON/OFF状態を保持する変数
    automatic_brightness_var = tk.BooleanVar()
    automatic_brightness_var.set(automatic_brightness)
    
    # 時間表示のON/OFF状態を保持する変数
    show_time_var = tk.BooleanVar()
    show_time_var.set(show_time)
    
    # 天気表示のON/OFF状態を保持する変数
    show_weather_var = tk.BooleanVar()
    show_weather_var.set(show_weather)
    
    # 音ファイルパスを保持する変数
    sound_path_var = tk.StringVar()
    sound_path_var.set(sound_path)
    
    # 音を流すかを保持する変数
    sound_mode_var = tk.BooleanVar()
    sound_mode_var.set(sound_mode)
    
    # 音を流すのを朝だけにする状態を保持する変数
    morning_sound_mode_var = tk.BooleanVar()
    morning_sound_mode_var.set(morning_sound_mode)

    # 画像ファイル選択ダイアログを表示する関数
    def select_image_path():
        path = filedialog.askdirectory()
        if path:
            image_path_var.set(path)

    # ファイル選択ダイアログを表示する関数
    def select_sound_path():
        path = filedialog.askdirectory()
        if path:
            sound_path_var.set(path)


    settings_frame = tk.Frame(root_start)
    settings_frame.grid(row=0, column=0, sticky="w")
    
    # 戻るボタン
    back_button = tk.Button(settings_frame, text="<<", command=back_action)
    back_button.grid(row=0, pady=10, sticky="nsew")

    # ファイル場所
    tk.Label(settings_frame, text="Image Path:").grid(row=1, column=0, sticky="w")
    tk.Entry(settings_frame, textvariable=image_path_var).grid(row=1, column=1, sticky="w")
    tk.Button(settings_frame, text="Browse", command=select_image_path).grid(row=1, column=2, sticky="w")

    # 切り替え間隔
    tk.Label(settings_frame, text="Display Interval (seconds):").grid(row=2, column=0, sticky="w")
    tk.Entry(settings_frame, textvariable=interval_var).grid(row=2, column=1, sticky="w")
    
    # 余白表示のチェックボックス
    tk.Label(settings_frame, text="Show Margin").grid(row=3, column=0, sticky="w")
    tk.Checkbutton(settings_frame, variable=show_margin_var).grid(row=3, column=1, sticky="w")
    
    # 自動輝度調整のチェックボックス
    tk.Label(settings_frame, text="Automatic Brightness").grid(row=4, column=0, sticky="w")
    tk.Checkbutton(settings_frame, variable=automatic_brightness_var).grid(row=4, column=1, sticky="w")
    
    # 時間表示のチェックボックス
    tk.Label(settings_frame, text="Show Clock(Please Also Check Show Margin)").grid(row=5, column=0, sticky="w")
    tk.Checkbutton(settings_frame, variable=show_time_var).grid(row=5, column=1, sticky="w")
    
    # 天気表示のチェックボックス
    tk.Label(settings_frame, text="Show Weather(Please Also Check Show Margin)").grid(row=6, column=0, sticky="w")
    tk.Checkbutton(settings_frame, variable=show_weather_var).grid(row=6, column=1, sticky="w")

    # 音ファイル場所
    tk.Label(settings_frame, text="Sound Path:").grid(row=7, column=0, sticky="w")
    tk.Entry(settings_frame, textvariable=sound_path_var).grid(row=7, column=1, sticky="w")
    tk.Button(settings_frame, text="Browse", command=select_sound_path).grid(row=7, column=2, sticky="w")
    
    # 朝のみに音楽を流す時のチェックボックス
    tk.Label(settings_frame, text="sound on/off").grid(row=8, column=0, sticky="w")
    tk.Checkbutton(settings_frame, variable=sound_mode_var).grid(row=8, column=1, sticky="w")
    
    # 朝のみに音楽を流す時のチェックボックス
    tk.Label(settings_frame, text="morning sound").grid(row=9, column=0, sticky="w")
    tk.Checkbutton(settings_frame, variable=morning_sound_mode_var).grid(row=9, column=1, sticky="w")

    # スタートボタン
    start_button = tk.Button(settings_frame, text="Start", command=start_action)
    start_button.grid(row=10, columnspan=3, pady=10, sticky="nsew")
    
    # スペース
    image_label = tk.Label(root_start)
    image_label.grid(row=1, column=0)

    root_start.mainloop()


# 開始ボタンのアクション
def start_action():
    
    image_path = image_path_var.get()
    interval = int(interval_var.get())
    show_margin = show_margin_var.get()
    automatic_brightness = automatic_brightness_var.get()
    show_time = show_time_var.get()
    show_weather = show_weather_var.get()
    sound_path = sound_path_var.get()
    sound_mode = sound_mode_var.get()
    morning_sound_mode = morning_sound_mode_var.get()

    # 設定を保存
    ls.save_settings(
        image_path=image_path, 
        image_interval=str(interval), 
        show_margin=show_margin, 
        automatic_brightness=automatic_brightness, 
        show_time=show_time,
        show_weather=show_weather,
        sound_path=sound_path,
        sound_mode=sound_mode,
        morning_sound_mode=morning_sound_mode)

    root_start.destroy()

    try:
        image_mode.create_image_widgets()
    except FileNotFoundError:
        messagebox.showerror("Error", "Image file not found!")
        create_image_setting_widgets()


# 戻るボタンのアクション
def back_action():
    root_start.destroy()
    main.create_start_widget()