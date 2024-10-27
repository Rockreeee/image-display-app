import tkinter as tk
import screens.study_mode_setting_screen as study_mode_setting_screen
import utils.settings_manager as settings_manager
from tkinter import messagebox
from time import strftime, localtime
import csv
import random

class StudyModeScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Study Display App")
        self.root.configure(background='black')
        self.brightness = 1.0

        # 設定変数の初期化
        self.initialize_settings()
        self.set_keybinding()
        self.create_widgets()

    # 設定をロードし、各変数に設定
    def initialize_settings(self):
        settings = settings_manager.load_settings()
        self.study_file = settings.get('study_file')
        self.answer_interval = int(settings.get('answer_interval'))
        self.change_interval = int(settings.get('change_interval'))

    # キーバインド一覧
    def set_keybinding(self):
        # 終了する時のキーバインド
        self.root.bind("<Escape>", self.close_window)
        self.root.bind("<q>", self.close_window)

        # キーイベントをバインドしてフルスクリーン表示の切り替えを有効にする
        self.root.bind("<f>", self.toggle_fullscreen)

        # キーイベントをバインドしてカーソルを表示きりかえ
        self.root.bind("<h>", self.toggle_cursor)
    
        # 明るさを調整するキーバインド
        self.root.bind("<b>", self.brightness_adjustment)
    
        # 暗記キーバインド
        self.root.bind("<space>", self.remember)
    
    # start: キーバインドのための関数一覧
    # 終了する時の関数
    def close_window(self, event):
        self.cancel_root_after()
        self.root.destroy()
        study_mode_setting_screen.create_screen()

    # ウィンドウの大きさを調整
    def toggle_fullscreen(self, event):
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    # カーソルを隠す関数
    def toggle_cursor(self, event):
        cursor_state = self.root.cget("cursor")
        if cursor_state == "none":
            self.root.config(cursor="arrow") 
        else:
            self.root.config(cursor="none")

    # 明るさを調整する関数
    def brightness_adjustment(self, event):
        self.brightness -= 0.2
        if self.brightness < 0:
            self.brightness = 1
        self.root.attributes('-alpha', self.brightness)

    def remember(self, event):
        try:
            self.data.remove(self.random_data)
            self.study_label.config(fg='grey')
            self.translation_label.config(fg='grey')
        except ValueError:
            pass
    # end: キーバインドのための関数一覧

    # UI作成
    def create_widgets(self):

        # 時計を表示
        self.show_clock_widget()
            
        # 単語を表示
        self.show_study_widget()

    # 時計のUI作成
    def show_clock_widget(self):
        # 大きさ調整
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # フォントサイズの設定
        date_font_size = screen_width // 20
        time_font_size = screen_width // 8

        # 日付と時間を表示するラベルを作成
        self.date_label = tk.Label(self.root, font=('calibri', date_font_size, 'bold'), bg='black', fg='white')
        self.date_label.pack(pady=(screen_height * 0.2, 0))
        self.time_label = tk.Label(self.root, font=('calibri', time_font_size, 'bold'), bg='black', fg='white')
        self.time_label.pack(pady=(screen_height * 0.05, 0))

        self.update_time()

    def update_time(self):
        current_time = strftime('%H:%M:%S')
        current_date = strftime('%Y-%m-%d %A', localtime())
        self.time_label.config(text=current_time)
        self.date_label.config(text=current_date)
        self.root_after_id_time = self.root.after(1000, self.update_time)


    def show_study_widget(self):
        # フォントサイズの設定
        study_font_size = self.root.winfo_screenwidth() // 15
        translation_font_size = self.root.winfo_screenwidth() // 15

        # ラベルを作成
        self.study_label = tk.Label(self.root, text="", font=('calibri', study_font_size), bg='black', fg='white')
        self.translation_label = tk.Label(self.root, text="", font=('calibri', translation_font_size), bg='black', fg='white')

        # 大きさ調整
        screen_height = self.root.winfo_screenheight()
        self.study_label.pack(pady=(screen_height * 0.05, 0))
        self.translation_label.pack(pady=(screen_height * 0.05, 0))

        # データをファイルから読み込む
        with open(self.study_file, newline='', encoding='utf-8') as csvfile:
            self.data = list(csv.reader(csvfile))

        # 初回表示のためにデータを更新
        self.update_question()

    # 問題の更新を行う関数
    def update_question(self):
        # テキスト色を元の白に戻す
        self.study_label.config(fg='white')
        self.translation_label.config(fg='white')

        # すべて暗記が終わった時
        if len(self.data) == 0:
            self.cancel_root_after()
            self.root.destroy()
            study_mode_setting_screen.create_screen()
            messagebox.showerror("Complete", "You got it!")
            return
        
        self.random_data = random.choice(self.data)
        self.study_label.config(text=self.random_data[0])
        self.translation_label.config(text="")
        self.root_after_id_question = self.root.after(self.answer_interval * 1000, self.update_answer)

    # 答えの更新を行う関数
    def update_answer(self):
        self.translation_label.config(text=self.random_data[1])
        self.root_after_id_answer = self.root.after(self.change_interval * 1000, self.update_question)


    # 予約処理のキャンセル
    def cancel_root_after(self):
        if hasattr(self, 'root_after_id_time'):
            self.root.after_cancel(self.root_after_id_time)
        if hasattr(self, 'root_after_id_question'):
            self.root.after_cancel(self.root_after_id_question)
        if hasattr(self, 'root_after_id_answer'):
            self.root.after_cancel(self.root_after_id_answer)

def create_screen():
    root = tk.Tk()
    try:
        StudyModeScreen(root)
        root.mainloop()  # エラーがない場合のみ実行
    except FileNotFoundError:
        # 音楽停止
        root.destroy()
        messagebox.showerror("Error", "Study file not found!")
        study_mode_setting_screen.create_screen()