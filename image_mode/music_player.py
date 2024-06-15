import pygame
import threading
import os
import random

class MusicPlayer:
    def __init__(self, mp3_Path):
        self.mp3_Path = mp3_Path
        pygame.mixer.init()

    def play_music(self):
        mp3_file = self.selectMusicFile()
        pygame.mixer.music.load(mp3_file)
        pygame.mixer.music.play()
        threading.Thread(target=self._check_music_playing).start()

    def stop_music(self):
        pygame.mixer.music.stop()

    def _check_music_playing(self):
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(1)
        print("music finish => next ..")
        self.play_music()

    def selectMusicFile(self):
        file = [f for f in os.listdir(self.mp3_Path) if f.endswith('.mp3')]
        random_file = random.choice(file)
        random_file_path = os.path.join(self.mp3_Path, random_file)
        return random_file_path