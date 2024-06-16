import pygame
import threading
import os
import random

class MusicPlayer:
    def __init__(self, mp3_Path):
        self.mp3_Path = mp3_Path
        # ミュート状態を保持するための変数
        self.is_muted = False
        pygame.mixer.init()
        self._stop_event = threading.Event()

    def play_music(self):
        mp3_file = self.selectMusicFile()
        print(mp3_file)
        pygame.mixer.music.load(mp3_file)
        pygame.mixer.music.play()
        self._stop_event.clear()
        threading.Thread(target=self._check_music_playing).start()

    def stop_music(self):
        pygame.mixer.music.stop()
        self._stop_event.set()

    def _check_music_playing(self):
        while pygame.mixer.music.get_busy():
            if self._stop_event.is_set():
                print("Music stopped")
                return
            pygame.time.Clock().tick(1)
        if not self._stop_event.is_set():
            print("music finished")
            self.play_music()

    def selectMusicFile(self):
        file = [f for f in os.listdir(self.mp3_Path) if f.endswith('.mp3')]
        random_file = random.choice(file)
        random_file_path = os.path.join(self.mp3_Path, random_file)
        return random_file_path
    
    # ミュート切り替え関数
    def sound_mute(self):
        self.is_muted = not self.is_muted
        if self.is_muted:
            pygame.mixer.music.set_volume(0)
            print("ミュートにしました")
        else:
            pygame.mixer.music.set_volume(1)
            print("ミュートを解除しました")