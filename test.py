import tkinter as tk

def change_text_color(label):
    text = label['text']
    words = text.split()
    label.config(text="")  # ラベルのテキストをクリア

    for word in words:
        if word == "red":
            label.config(text=label["text"] + word + " ", fg="red")
        elif word == "green":
            label.config(text=label["text"] + word + " ", fg="green")
        elif word == "blue":
            label.config(text=label["text"] + word + " ", fg="blue")
        else:
            label.config(text=label["text"] + word + " ")

root = tk.Tk()

label = tk.Label(root, text="red green blue")
label.pack()

change_text_color(label)

root.mainloop()
