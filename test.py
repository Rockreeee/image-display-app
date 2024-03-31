import tkinter as tk
from PIL import Image, ImageTk

class VideoPlayer:
    def __init__(self, window, video_source=0):
        self.window = window
        self.window.title("Video Player")

        self.video_source = video_source
        self.vid = Image.open(video_source)
        self.photo = ImageTk.PhotoImage(self.vid)

        self.canvas = tk.Canvas(window, width=self.vid.width, height=self.vid.height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    player = VideoPlayer(root, video_source="/Users/morimotoakihito/Desktop/image app/landscapes/1.MOV")
