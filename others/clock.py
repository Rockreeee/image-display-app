import tkinter as tk
from time import strftime, localtime

root = tk.Tk()
root_after_id = ""
x_pos = 0
y_pos = 0

# ウィンドウをドラッグして移動するための関数
def move_window(event):
    global x_pos, y_pos
    x, y = event.x_root, event.y_root
    root.geometry(f"+{x - x_pos}+{y - y_pos}")

def on_button_press(event):
    global x_pos, y_pos
    x_pos, y_pos = event.x, event.y

def on_button_release(event):
    pass

# 時計表示
def show_clock_widget():

    root.title("Calender & Clock")

    # ウィンドウのスタイルを変更してタイトルバーと境界を非表示にする
    root.overrideredirect(True)

    # ウィンドウ全体の透明度を50%に設定
    root.attributes("-alpha", 1.0)  
    # 日付と曜日以外の背景色を変更
    root.configure(background="white")
    # font size
    date_font_size = root.winfo_screenwidth() // 20
    # 日付と曜日を表示するラベルを作成
    date_label = tk.Label(root, font=('calibri', date_font_size, 'bold'), bg="white", fg='gray')
    date_label.pack(pady=(0, 0))

    # font size
    time_font_size = root.winfo_screenwidth() // 10
    # 時間を表示するラベルを作成
    time_label = tk.Label(root, font=('calibri', time_font_size, 'bold'), bg="white", fg='gray')
    # ラベルの高さを取得
    time_label.pack(pady=(0, 0))  # 日付の下に配置

    # ウィンドウ移動用のイベントハンドラを設定
    root.bind("<B1-Motion>", move_window)
    root.bind("<ButtonPress-1>", on_button_press)
    root.bind("<ButtonRelease-1>", on_button_release)

    # 日付と曜日、時間を更新する関数
    def update_time():
        global root_after_id
        # 予約キャンセル
        if root_after_id !="":
            root.after_cancel(root_after_id)
            
        current_time = strftime('%H:%M:%S')
        current_date = strftime('%Y-%m-%d %A', localtime())
        time_label.config(text=current_time)
        date_label.config(text=current_date)
        root_after_id = root.after(1000, update_time)  # 次の更新まで待機

    update_time()  # 初回の呼び出し

    root.mainloop()


show_clock_widget()