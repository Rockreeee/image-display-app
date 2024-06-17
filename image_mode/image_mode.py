import os
import random
import tkinter as tk
from PIL import Image, ImageEnhance, ImageTk
from tkinter import filedialog
from tkinter import messagebox
import datetime
from time import strftime, localtime
import threading

import image_mode.fetch_weather as fetch_weather
import image_mode.music_player as music_player
import image_mode.image_mode_setting as image_mode_setting
import load_and_save_data as ls

# カスタム項目＝＝===========

# カレンダーの上とモニターの距離
margin_above_the_clock = 50
# 明るくなる時間
time_of_brightness = 7
# 暗くなる時間
time_of_darkness = 21
# 音楽が止まるまでの時間（分）
time_to_stop_music = 30

# カスタム項目＝＝===========

image_path = None
interval = None
show_margin = None
automatic_brightness = None
show_time = None
show_weather = None
sound_path = None
sound_mode = None
morning_sound_mode = None

root = None
label = None
image_files = None
player = None
music_thread = None
label_brightness = 1.0
image_brightness = 1.0
date_label = None
time_label = None
weather_label = None

root_after_id_1 = ""
root_after_id_2 = ""
root_after_id_3 = ""
root_after_id_4 = ""
root_after_id_5 = ""
root_after_id_6 = ""
root_after_id_7 = ""


# ランダムに画像を表示する関数
def create_image_widgets():

    global root
    global label
    global image_files

    global image_path
    global interval
    global show_margin
    global automatic_brightness
    global show_time
    global show_weather
    global sound_path
    global sound_mode
    global morning_sound_mode
    
    # 設定をロード
    image_path = str(ls.load_settings(column=1))
    interval = int(ls.load_settings(column=2))
    show_margin = str_to_bool(ls.load_settings(column=3))
    automatic_brightness = str_to_bool(ls.load_settings(column=4))
    show_time = str_to_bool(ls.load_settings(column=5))
    show_weather = str_to_bool(ls.load_settings(column=6))
    sound_path = str(ls.load_settings(column=7))
    sound_mode = str_to_bool(ls.load_settings(column=8))
    morning_sound_mode = str_to_bool(ls.load_settings(column=9))

    image_files = [f for f in os.listdir(image_path) if f.endswith(('.jpg', '.jpeg', '.png'))]

    root = tk.Tk()
    root.title("Image Display App")

    label = tk.Label(root, bg='white')
    label.pack(fill=tk.BOTH, expand=True, side="bottom")
    
    # 終了する時のキーバインド
    root.bind("<Escape>", close_window)
    root.bind("<q>", close_window)
    
    # 明るさを調整するキーバインド
    root.bind("<b>", label_brightness_adjustment)

    # 明るさを調整するキーバインド
    root.bind("<v>", image_brightness_adjustment)

    # キーイベントをバインドしてフルスクリーン表示の切り替えを有効にする
    root.bind("<f>", toggle_fullscreen)

    # キーイベントをバインドしてカーソルを表示きりかえ
    root.bind("<h>", toggle_cursor)

    # キーイベントをバインドしてミュートの切り替えを有効にする
    root.bind("<m>", sound_mute)
        
    # キーイベントをバインドして画像変更を有効にする
    root.bind("<space>", next_image)

    if automatic_brightness:
        automatic_brightness_adjustment()
    
    if show_time:
        show_clock_widget()

    if show_weather:
        show_weather_widget()

    if sound_path != "":
        if sound_mode:
            play_sound(sound_path)
        elif morning_sound_mode:
            automatic_sound_booking()
        
    show_next_image()

    root.mainloop()

    
# 予約処理のキャンセル
def cancel_root_after(root):
    global date_label
    global time_label
    global weather_label

    root.after_cancel(root_after_id_1)

    if root_after_id_2 != "":
        root.after_cancel(root_after_id_2)

    if root_after_id_3 != "":
        root.after_cancel(root_after_id_3)

    if root_after_id_4 != "":
        root.after_cancel(root_after_id_4)

    if root_after_id_5 != "":
        root.after_cancel(root_after_id_5)

    if root_after_id_6 != "":
        root.after_cancel(root_after_id_6)

    if root_after_id_7 != "":
        root.after_cancel(root_after_id_7)

    date_label = None
    time_label = None
    weather_label = None

# 終了する時の関数
def close_window(event):
    
    # 音楽停止
    if player != None:
        player.stop_music()

    cancel_root_after(root)
    root.destroy()
    image_mode_setting.create_image_setting_widgets()

# 明るさを調整する関数
def label_brightness_adjustment(event):
    global label_brightness
    label_brightness -= 0.2
    if label_brightness < 0:
        label_brightness = 1
    label.config(bg=f'#{int(label_brightness*255):02x}{int(label_brightness*255):02x}{int(label_brightness*255):02x}')  # 背景色を調整
    if show_time:
        show_clock_widget()
    if show_weather:
        show_weather_widget()

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

# ウィンドウの大きさを調整
def toggle_fullscreen(event):
    root.attributes("-fullscreen", not root.attributes("-fullscreen"))

# カーソルを隠す関数
def toggle_cursor(event):
    cursor_state = root.cget("cursor")

    if cursor_state == "none":
        root.config(cursor="arrow") 
    else:
        root.config(cursor="none")  # "none"はカーソルを非表示にする

# ミュートにする関数
def sound_mute(event):
    if player != None:
        player.sound_mute()

# 次のイメージにする関数
def next_image(event):
    if show_margin:
        show_image_with_margin()
    else:
        show_image_without_margin()
        
# 特定の時間までの残り時間を計算
def calculate_time_next_trigger(target_hour, target_minute):
    # 現在の時刻を取得
    current_time = datetime.datetime.now()

    # 次に発動させたい時間を計算
    target_time = current_time.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

    # 現在の時刻から次の発動までの時間を計算
    delta_time = target_time - current_time

    total_seconds = delta_time.total_seconds()

    return total_seconds

# 時計表示
def show_clock_widget():
    global date_label
    global time_label
    global root_after_id_4

    # 予約キャンセル
    if root_after_id_4 !="":
        root.after_cancel(root_after_id_4)
    # 親ウィンドウの背景色を取得
    parent_bg_color = label.cget('bg')
    # 日付と曜日以外の背景色を変更
    root.configure(background=parent_bg_color)
    # 初期化
    if date_label != None:
        date_label.pack_forget()
    # font size
    date_font_size = root.winfo_screenwidth() // 20
    # 日付と曜日を表示するラベルを作成
    date_label = tk.Label(root, font=('calibri', date_font_size, 'bold'), bg=parent_bg_color, fg='gray')
    date_label.pack(pady=(margin_above_the_clock, 0))

    # 初期化
    if time_label != None:
        time_label.pack_forget()
    # font size
    time_font_size = root.winfo_screenwidth() // 10
    # 時間を表示するラベルを作成
    time_label = tk.Label(root, font=('calibri', time_font_size, 'bold'), bg=parent_bg_color, fg='gray')
    # ラベルの高さを取得
    date_label_height = date_label.winfo_height()
    time_label.pack(pady=(date_label_height + margin_above_the_clock, 0))  # 日付の下に配置

    # 日付と曜日、時間を更新する関数
    def update_time():
        global root_after_id_4
        # 予約キャンセル
        if root_after_id_4 !="":
            root.after_cancel(root_after_id_4)
            
        current_time = strftime('%H:%M:%S')
        current_date = strftime('%Y-%m-%d %A', localtime())
        time_label.config(text=current_time)
        date_label.config(text=current_date)
        root_after_id_4 = root.after(1000, update_time)  # 次の更新まで待機

    update_time()  # 初回の呼び出し

# 天気
def show_weather_widget():
    global weather_label

    clock_height = 0

    if show_time:
        clock_height = margin_above_the_clock + date_label.winfo_height() + time_label.winfo_height()

    # 親ウィンドウの背景色を取得
    parent_bg_color = label.cget('bg')
    # 日付と曜日以外の背景色を変更
    root.configure(background=parent_bg_color)

    # 初期化
    if weather_label != None:
        weather_label.pack_forget()
    # font size
    weather_font_size = root.winfo_screenwidth() // 30
    # 天気を表示するラベルを作成
    weather_label = tk.Label(root, font=('calibri', weather_font_size, 'bold'), bg=parent_bg_color, fg='gray')
    weather_label.pack(pady=(clock_height, 0))

    # １時間ごとに天気更新
    def update_weather():
        global root_after_id_5

        # 予約キャンセル
        if root_after_id_5 !="":
            root.after_cancel(root_after_id_5)

        forecast_data = fetch_weather.get_precipitation_forecast()
        weather_label.config(text=forecast_data["weather"] 
                            + "     " + "↑" + forecast_data["high_temperature_value"] + "°" + " " + "↓" +  forecast_data["low_temperature_value"] + "°" + "\n" 
                            + "00~06" + ":" + forecast_data["probabilities"][0] + "%" + " " 
                            + "06~12" + ":" + forecast_data["probabilities"][1] + "%" + " " + "\n"
                            + "12~18" + ":" + forecast_data["probabilities"][2] + "%" + " " 
                            + "18~24" + ":" + forecast_data["probabilities"][3] + "%" + " ")

        root_after_id_5 = root.after(60 * 1000, update_weather)  # 次の更新まで待機

    update_weather()  # 初回の呼び出し

# 自動明るさ調整
def automatic_brightness_adjustment():
    global root_after_id_2
    global root_after_id_3
    global image_brightness
    global label_brightness

    # 予約キャンセル
    if root_after_id_2 !="":
        root.after_cancel(root_after_id_2)
    if root_after_id_3 !="":
        root.after_cancel(root_after_id_3)

    # 朝、夜までの時間計算
    time_to_morning = calculate_time_next_trigger(time_of_brightness, 0)
    time_to_night = calculate_time_next_trigger(time_of_darkness, 0)

    # すでに夜の時
    if time_to_night < 0 or time_to_morning > 0:
        print("今は夜です")
        image_brightness = 0.2
        label_brightness = 0
        label.config(bg=f'#{int(label_brightness*255):02x}{int(label_brightness*255):02x}{int(label_brightness*255):02x}')  # 背景色を調整
        if show_time:
            show_clock_widget()
        if show_weather:
            show_weather_widget()
    else:
        print("今は昼です")
        image_brightness = 1.0
        label_brightness = 1.0
        label.config(bg=f'#{int(label_brightness*255):02x}{int(label_brightness*255):02x}{int(label_brightness*255):02x}')  # 背景色を調整
        if show_time:
            show_clock_widget()
        if show_weather:
            show_weather_widget()

    if time_to_morning < 0:
        time_to_morning += 86400

    if time_to_night < 0:
        time_to_night += 86400

    # 予約
    print("画面が明るくなるまで：", int(time_to_morning))
    print("画面が暗くなるまで：", int(time_to_night))
    root_after_id_2 = root.after(int(time_to_morning) * 1000, automatic_brightness_adjustment)
    root_after_id_3 = root.after(int(time_to_night) * 1000, automatic_brightness_adjustment)

# 音楽再生
def play_sound(path):
    global player
    global music_thread

    player = music_player.MusicPlayer(path)

    # play_music_loopを別スレッドで実行
    music_thread = threading.Thread(target=player.play_music)
    music_thread.start()

# 自動音予約
def automatic_sound_booking():
    global root_after_id_6
    global root_after_id_7
    global player
    global music_thread

    if root_after_id_7 != "":
        root.after_cancel(root_after_id_7)

    # root_after_id_6に値がある=初回起動時ではない
    if root_after_id_6 != "":
        # 音楽を再生
        player = music_player.MusicPlayer(sound_path)
        music_thread = threading.Thread(target=player.play_music)
        music_thread.start()

        # 初回起動時以外は音楽を停止予約
        root_after_id_7 = root.after(int(time_to_stop_music * 60) * 1000, player.stop_music)

    # 予約キャンセル
    if root_after_id_6 != "":
        root.after_cancel(root_after_id_6)


    # 朝までの時間計算
    time_to_morning = calculate_time_next_trigger(time_of_brightness, 0)

    if time_to_morning < 0:
        time_to_morning += 86400

    # 予約
    print("朝音が流れるまで：", int(time_to_morning))
    root_after_id_6 = root.after(int(time_to_morning) * 1000, automatic_sound_booking)

# ランダムな画像を選ぶ関数
def make_random_image_path(image_path):
    random_image = random.choice(image_files)
    random_image_path = os.path.join(image_path, random_image)
    return random_image_path

def show_image_with_margin():
    global image_brightness

    clock_height = 0
    if show_time:
        date_label_height = date_label.winfo_height()
        time_label_height = time_label.winfo_height()
        clock_height = margin_above_the_clock + date_label_height + time_label_height

    weather_height = 0
    if show_weather:
        weather_height = weather_label.winfo_height()

    random_image_path = make_random_image_path(image_path=image_path)

    img = Image.open(random_image_path)
    img_width, img_height = img.size
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight() - clock_height - weather_height
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

    random_image_path = make_random_image_path(image_path=image_path)

    img = Image.open(random_image_path)
    img_width, img_height = img.size
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    ratio = max(screen_width / img_width, screen_height / img_height)
    new_width = int(img_width * ratio)
    new_height = int(img_height * ratio)
    img = img.resize((new_width, new_height), Image.ANTIALIAS)

    # 画像の中央部分を切り取るための座標を計算
    x = (new_width - screen_width) // 2
    y = (new_height - screen_height) // 2

    # 画像が画面より大きい場合は切り取る
    if x > 0 or y > 0:
        img = img.crop((x, y, x + screen_width, y + screen_height))

    # 明るさを調整するためのBrightnessオブジェクトを作成し、ファクターを設定
    enhancer = ImageEnhance.Brightness(img)
    adjusted_image = enhancer.enhance(image_brightness)

    photo = ImageTk.PhotoImage(adjusted_image)
    label.configure(image=photo)
    label.image = photo

def show_next_image():
    global root_after_id_1
    if root_after_id_1 != "":
        root.after_cancel(root_after_id_1)
    if show_margin:
        show_image_with_margin()
    else:
        show_image_without_margin()
    root_after_id_1 = root.after(interval * 1000, show_next_image)

def str_to_bool(s):
    return s.lower() == "true"