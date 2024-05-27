import os
import random
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog
from tkinter import messagebox
import cv2

import load_and_save_data as ls

# 開始画面を生成する関数
def create_landscape_widgets():
    
    root_start = tk.Tk()
    root_start.title("video Display App")
    
    # 設定をロード
    video_directory = ls.load_settings(column=10)
    interval = ls.load_settings(column=11)
    
    # デフォルトの表示間隔を設定
    interval_var = tk.StringVar()
    interval_var.set(interval)
    
    # 前回選択したファイルパスを設定
    path_var = tk.StringVar()
    path_var.set(video_directory)

    # ファイル選択ダイアログを表示する関数
    def select_path():
        path = filedialog.askdirectory()
        if path:
            path_var.set(path)

    # 開始ボタンのアクション
    def start_action():
        video_directory = path_var.get()
        interval = int(interval_var.get())

        # 設定を保存
        ls.save_settings(None, None, None, video_directory, str(interval))

        root_start.destroy()

        try:
            show_random_video(video_directory, interval)
        except FileNotFoundError:
            messagebox.showerror("Error", "Video file not found!")
            create_landscape_widgets()


    # 戻るボタンのアクション
    def back_action():
        root_start.destroy()
        ls.create_start_widget()

    settings_frame = tk.Frame(root_start)
    settings_frame.grid(row=0, column=0, sticky="w")
    
    # 戻るボタン
    back_button = tk.Button(settings_frame, text="<<", command=back_action)
    back_button.grid(row=0, pady=10, sticky="nsew")

    # ファイル場所
    tk.Label(settings_frame, text="Vmage Directory:").grid(row=1, column=0, sticky="w")
    tk.Entry(settings_frame, textvariable=path_var).grid(row=1, column=1, sticky="w")
    tk.Button(settings_frame, text="Browse", command=select_path).grid(row=1, column=2, sticky="w")

    # 切り替え間隔
    tk.Label(settings_frame, text="Display Interval (seconds):").grid(row=2, column=0, sticky="w")
    tk.Entry(settings_frame, textvariable=interval_var).grid(row=2, column=1, sticky="w")
    
    # スタートボタン
    start_button = tk.Button(settings_frame, text="Start", command=start_action)
    start_button.grid(row=3, columnspan=3, pady=10, sticky="nsew")
    
    # スペース
    video_label = tk.Label(root_start)
    video_label.grid(row=1, column=0)

    root_start.mainloop()

# ランダムに動画を表示する関数
def show_random_video(directory, interval):
    
    video_files = [f for f in os.listdir(directory) if f.endswith(('.mp4', '.MOV', '.gif'))]
    root = tk.Tk()
    root.title("Video Display App")
    root.attributes("-fullscreen", True)
    root.configure(background='black')  # 背景色を黒色に設定
    
    def close_window(event):
        root.destroy()
        create_landscape_widgets()
    
    root.bind("<Escape>", close_window)
    
    label = tk.Label(root, bg='black')  # ラベルの背景色を黒色に設定
    label.pack(fill=tk.BOTH, expand=True)
    
    # def show_next_video():
    #     show_video()
    #     root.after(interval * 1000, show_next_video)

    def show_video():
        random_video = random.choice(video_files)
        video_path = os.path.join(directory, random_video)
        
        # 動画を読み込む
        cap = cv2.VideoCapture(video_path)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(image=image)


        cap.release()

    show_video()
    root.mainloop()



# def show_random_video(directory, interval):
#     """ランダムに動画を表示する関数"""
#     video_files = [f for f in os.listdir(directory) if f.endswith(('.mp4', '.MOV', '.gif'))]
#     root = tk.Tk()
#     root.title("Video Display App")
#     root.attributes("-fullscreen", True)
#     root.configure(background='black')  # 背景色を黒色に設定
    
#     def close_window(event):
#         root.destroy()
#         create_landscape_widgets()
    
#     root.bind("<Escape>", close_window)
    
#     label = tk.Label(root, bg='black')  # ラベルの背景色を黒色に設定
#     label.pack(fill=tk.BOTH, expand=True)
    
#     def show_next_video():
#         show_video()
#         root.after(interval * 1000, show_next_video)

#     def show_video():
#         random_video = random.choice(video_files)
#         video_path = os.path.join(directory, random_video)
        
#         # 動画を読み込む
#         cap = cv2.VideoCapture(video_path)

#         # 動画のフレームを1フレームずつ読み込んで表示
#         while True:
#             ret, frame = cap.read()
#             if ret:
#                 # フレームをウィンドウに表示
#                 cv2.imshow('Video Player', frame)
#                 # 'q'キーが押されたらループを抜ける
#                 if cv2.waitKey(25) & 0xFF == ord('q'):
#                     break
#             else:
#                 # 動画の最後まで再生された場合はループを抜ける
#                 break

#         # キャプチャを解放
#         cap.release()
#         # OpenCVのウィンドウを閉じる
#         cv2.destroyAllWindows()

#         # random_video = random.choice(video_files)
#         # video_path = os.path.join(directory, random_video)
        
#         # # 動画を読み込む
#         # cap = cv2.VideoCapture(video_path)
        
#         # # 動画のフレームを表示
#         # while True:
#         #     ret, frame = cap.read()
#         #     if ret:
#         #         # ウィンドウサイズにフレームをリサイズ
#         #         frame = cv2.resize(frame, (root.winfo_screenwidth(), root.winfo_screenheight()))
                
#         #         # OpenCVのBGR形式をPILのRGB形式に変換
#         #         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
#         #         # フレームを画像として表示
#         #         photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
#         #         label.configure(image=photo)
#         #         label.image = photo
                
#         #         # ループを継続
#         #         if cv2.waitKey(1) & 0xFF == ord('q'):
#         #             break
#         #     else:
#         #         # 動画の最後まで再生された場合は、再生をリセットしてループする
#         #         cap.release()
#         #         cap = cv2.VideoCapture(video_path)

#         # # キャプチャを解放
#         # cap.release()

#     show_next_video()

#     root.mainloop()
