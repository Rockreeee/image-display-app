"""設定画面で使う共通UIヘルパー。

各設定画面でコピペされていたウィンドウ配置・入力値チェック・
ウィジェット生成処理をここに集約する。
"""

import tkinter as tk

# 補足説明テキストの色
HELP_COLOR = "#666666"


def center_window(root, width, height):
    """ウィンドウを指定サイズにし、画面中央へ配置する。"""
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")


def fit_window(root, min_width=0, min_height=0):
    """ウィジェット配置後に呼び出し、内容に合うサイズへ調整して中央配置する。

    説明文などで縦に伸びても、すべての項目(下部のボタン含む)が
    収まるようにする。min_width / min_height で最小サイズを保証できる。
    """
    root.update_idletasks()
    width = max(root.winfo_reqwidth(), min_width)
    height = max(root.winfo_reqheight(), min_height)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")


def is_positive_int(value):
    """文字列が 1 以上の整数として解釈できれば True を返す。"""
    try:
        return int(value) > 0
    except (ValueError, TypeError):
        return False


class SettingsForm:
    """設定項目をグリッドに積み上げていくためのフォームビルダー。

    行番号を内部で自動管理するので、呼び出し側は項目を順番に
    追加していくだけでよい。各項目には任意で補足説明(help)を
    付けられ、ユーザーが意味を理解しやすくする。
    """

    def __init__(self, master):
        self.frame = tk.Frame(master)
        self.frame.pack(padx=20, pady=15, fill="both", expand=True)
        # 入力欄(列1)を横に伸ばす
        self.frame.columnconfigure(1, weight=1)
        self._row = 0

    def _next_row(self):
        row = self._row
        self._row += 1
        return row

    def add_section(self, title):
        """セクション見出しを追加し、関連項目をグループ化する。"""
        row = self._next_row()
        pady = (12, 4) if row > 0 else (0, 4)
        tk.Label(
            self.frame, text=title, font=(None, 13, "bold"), anchor="w"
        ).grid(row=row, column=0, columnspan=3, sticky="w", pady=pady)

    def add_help(self, text):
        """直前の項目に対する補足説明を一段下げて表示する。"""
        row = self._next_row()
        tk.Label(
            self.frame, text=text, fg=HELP_COLOR, anchor="w",
            justify="left", wraplength=520,
        ).grid(row=row, column=0, columnspan=3, sticky="w", padx=(24, 0))

    def _add_field_label(self, row, text):
        tk.Label(self.frame, text=text, anchor="w").grid(
            row=row, column=0, sticky="w", padx=(12, 8)
        )

    def add_entry(self, label, variable, help_text=None):
        """ラベル付きのテキスト入力欄を追加する。"""
        row = self._next_row()
        self._add_field_label(row, label)
        tk.Entry(self.frame, textvariable=variable).grid(
            row=row, column=1, columnspan=2, sticky="ew"
        )
        if help_text:
            self.add_help(help_text)

    def add_path(self, label, variable, command, help_text=None):
        """入力欄 + 「Browse」ボタンの組を追加する(フォルダ/ファイル選択用)。"""
        row = self._next_row()
        self._add_field_label(row, label)
        tk.Entry(self.frame, textvariable=variable).grid(
            row=row, column=1, sticky="ew"
        )
        tk.Button(self.frame, text="Browse", command=command).grid(
            row=row, column=2, padx=(8, 0)
        )
        if help_text:
            self.add_help(help_text)

    def add_checkbox(self, label, variable, help_text=None):
        """オン/オフのチェックボックスを追加する。"""
        row = self._next_row()
        tk.Checkbutton(
            self.frame, text=label, variable=variable, anchor="w"
        ).grid(row=row, column=0, columnspan=3, sticky="w", padx=(8, 0))
        if help_text:
            self.add_help(help_text)

    def add_radio(self, label, variable, value, help_text=None):
        """ラジオボタン(択一選択肢)を1つ追加する。"""
        row = self._next_row()
        tk.Radiobutton(
            self.frame, text=label, variable=variable, value=value, anchor="w"
        ).grid(row=row, column=0, columnspan=3, sticky="w", padx=(24, 0))
        if help_text:
            self.add_help(help_text)

    def add_action_buttons(self, back_command, start_command):
        """画面下部に「戻る」「開始」ボタンを配置する。"""
        row = self._next_row()
        bar = tk.Frame(self.frame)
        bar.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(18, 0))
        tk.Button(bar, text="<< Back", command=back_command).pack(side="left")
        tk.Button(bar, text="Start", command=start_command).pack(side="right")
