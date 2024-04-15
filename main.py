import tkinter as tk

import image_mode
import study_mode
import load_and_save_data as ls

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
    mode = ls.load_settings(column=0)
    mode_var.set(mode)

    # ラジオボタンAを作成
    mode_a = tk.Radiobutton(mode_window, text="Image", variable=mode_var, value="Image")
    mode_a.pack()

    # # ラジオボタンBを作成
    # mode_b = tk.Radiobutton(mode_window, text="Movie", variable=mode_var, value="Movie")
    # mode_b.pack()

    # ラジオボタンCを作成
    mode_c = tk.Radiobutton(mode_window, text="Study", variable=mode_var, value="Study")
    mode_c.pack()

    def confirm_mode():
        # 選択されたモードを取得
        selected_mode = mode_var.get()

        # モード選択ウィンドウを閉じる
        mode_window.destroy()

        # 設定を保存
        ls.save_settings(mode=selected_mode)
        
        if selected_mode == "Image":
            image_mode.create_image_setting_widgets()
        # elif selected_mode == "Movie":
        #     movie.create_movie_setting_widgets()
        elif selected_mode == "Study":
            study_mode.create_study_setting_widgets()


    # 確認ボタンを作成
    confirm_button = tk.Button(mode_window, text="Confirm", command=confirm_mode)
    confirm_button.pack(pady=10)

    mode_window.mainloop()


if __name__ == "__main__":
    create_start_widget()

