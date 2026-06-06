"""設定の読み書きを担当するモジュール。

設定は JSON ファイル(.settings.json)に保存する。読み込み時は
DEFAULT_SETTINGS をベースに、保存済みの値で上書きする。これにより
新しい設定キーを追加してもデフォルト値で安全に動作する。
"""

import os
import json

SETTINGS_FILE = ".settings.json"

# 各設定キーのデフォルト値。実際にアプリ内で使われているキーのみを定義する。
DEFAULT_SETTINGS = {
    # 共通
    "mode": "Image",            # 起動モード: "Image" または "Study"
    # 画像モード
    "auto_image": False,         # True: ネットから画像を自動取得
    "image_path": "",            # 画像フォルダのパス
    "interval": "3600",          # 画像の切り替え間隔(秒)
    "automatic_brightness": True,  # 時間帯に応じた自動明るさ調整
    "show_time": True,           # 時計を表示
    "show_weather": True,        # 天気を表示
    "show_train_schedule": True,  # 列車時刻表を表示
    "sound_path": "",            # BGM フォルダのパス
    "sound_mode": "0",           # "0":オフ "1":常時 "2":朝のみ
    # 勉強モード
    "study_file": "",            # 問題ファイル(.csv)のパス
    "answer_interval": "2",      # 答えが出るまでの時間(秒)
    "change_interval": "2",      # 次の問題に変わるまでの時間(秒)
}


def load_settings():
    """設定ファイルを読み込み、デフォルト値とマージした dict を返す。"""
    settings = dict(DEFAULT_SETTINGS)
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings.update(json.load(f))
        except json.JSONDecodeError:
            print("設定ファイルの読み込みに失敗しました。デフォルト設定を使用します。")
    return settings


def save_settings(**kwargs):
    """与えられたキー/値で設定を更新し、ファイルへ保存する。"""
    settings = load_settings()
    settings.update(kwargs)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)
