import tkinter as tk

root = tk.Tk()
root.title("Transparent Label Example")
root.config(background='')

# 親ウィンドウの背景色を設定
parent_bg_color = root.cget('bg')

# ラベルの背景色を親の背景色と同じに設定し、文字色を設定
label = tk.Label(root, text="This is a transparent label", bg=parent_bg_color, fg="black")
label.pack()

root.mainloop()
