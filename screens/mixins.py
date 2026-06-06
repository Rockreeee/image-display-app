"""表示画面(画像モード・勉強モード)で共通するウィンドウ操作。

フルスクリーン切り替えとカーソル表示切り替えは全画面で同じ
挙動なので、ミックスインとして共有する。
"""


class WindowControlsMixin:
    """フルスクリーン/カーソル表示のトグルを提供するミックスイン。

    利用側のクラスは `self.root`(Tk ウィンドウ)を持っている前提。
    """

    def toggle_fullscreen(self, event=None):
        """フルスクリーン表示を切り替える。"""
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    def toggle_cursor(self, event=None):
        """マウスカーソルの表示/非表示を切り替える。"""
        if self.root.cget("cursor") == "none":
            self.root.config(cursor="arrow")
        else:
            self.root.config(cursor="none")
