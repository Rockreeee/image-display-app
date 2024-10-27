import os
import json

SETTINGS_FILE = ".settings.json"

# 設定ファイルから全設定を読み込む関数
def load_settings():
    # デフォルト値
    default_settings = {
        "mode": "Image",
        "image_path": "",
        "interval": "3600",
        "show_margin": False,
        "automatic_brightness": False,
        "show_time": False,
        "show_weather": False,
        "sound_path": "",
        "sound_mode": "0",
        "video_directory": "",
        "video_interval": "60",
        "study_file": "",
        "study_answer_interval": "2",
        "study_change_interval": "2"
    }

    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            try:
                # JSON形式で設定を読み込む
                settings = json.load(f)
                # デフォルト設定を上書きする
                default_settings.update(settings)
            except json.JSONDecodeError:
                print("Error reading JSON file. Using default settings.")
    
    return default_settings

# 設定を設定ファイルに保存する関数
def save_settings(**kwargs):
    # 現在の設定を取得
    settings = load_settings()
    # 引数で与えられた新しい設定値で上書き
    settings.update(kwargs)

    with open(SETTINGS_FILE, "w") as f:
        # JSON形式で書き込む
        json.dump(settings, f, indent=4)