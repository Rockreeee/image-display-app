import tkinter as tk

# グローバル変数として明るさを初期化
brightness = 1

# 明るさを調整する関数
def brightness_adjustment(event):
    global brightness
    brightness -= 0.2
    if brightness < 0:
        brightness = 1
    label.config(bg=f'#{int(brightness*255):02x}{int(brightness*255):02x}{int(brightness*255):02x}')  # 背景色を調整
    label.config(fg=f'#{int((1-brightness)*255):02x}{int((1-brightness)*255):02x}{int((1-brightness)*255):02x}')  # テキスト色を調整
    print("明るさを変更しました：", brightness)

root = tk.Tk()
root.geometry("200x200")

# ラベルを作成して、明るさを調整する関数を呼び出す
label = tk.Label(root, text="透明度を調整するラベル")
label.pack()

# キーイベントをバインドして明るさを調整する関数を呼び出す
root.bind("<KeyPress>", brightness_adjustment)

root.mainloop()
