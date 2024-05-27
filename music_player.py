import pygame
import threading

class MusicPlayer:
    def __init__(self, mp3_file):
        self.mp3_file = mp3_file
        self._is_playing = False
        pygame.mixer.init()

    def play_music(self):
        if not self._is_playing:
            pygame.mixer.music.load(self.mp3_file)
            pygame.mixer.music.play(loops=-1)
            self._is_playing = True
            threading.Thread(target=self._check_music_playing).start()

    def _check_music_playing(self):
        while self._is_playing and pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def stop_music(self):
        if self._is_playing:
            pygame.mixer.music.stop()
            self._is_playing = False

    def play_music_loop(self):
        self.play_music()
        try:
            while self._is_playing:
                pygame.time.Clock().tick(10)
        except KeyboardInterrupt:
            self.stop_music()
