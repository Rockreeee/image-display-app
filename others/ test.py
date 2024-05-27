import tkinter as tk

root = tk.Tk()
root.wait_visibility(root)
root.attributes('-alpha', 0.0)
root.overrideredirect(True)
root.geometry('300x200')
root.mainloop()