"""アプリ全体の調整値・地域固有データを集約するモジュール。

フォントサイズや明るさのスケジュール、天気の予報地点、列車時刻表の
ファイルパスや路線名など「環境やコードロジックから切り離したい設定」を
ここに集める。地域や好みに合わせて変更する場合は基本的にこのファイルだけ
を編集すればよい。
"""

import os

# プロジェクトのルートディレクトリ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- 画像 ---
# スライドショーで表示対象とする拡張子
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")

# --- 表示フォントサイズ ---
DATE_FONT_SIZE = 28
TIME_FONT_SIZE = 70
WEATHER_FONT_SIZE = 20

# --- 自動明るさ調整(24時間表記) ---
DAY_START_HOUR = 9       # ここから昼(最大の明るさ)
DAY_END_HOUR = 17        # ここまで昼
NIGHT_START_HOUR = 21    # ここから夜(最小の明るさ)
NIGHT_END_HOUR = 5       # ここまで夜(翌朝5時)
DAY_BRIGHTNESS = 1.0
NIGHT_BRIGHTNESS = 0.2

# --- BGM(朝のみモード) ---
MORNING_SOUND_HOUR = 7    # 朝の BGM を流し始める時刻
MORNING_SOUND_MINUTE = 0
MUSIC_STOP_MINUTES = 10   # 朝の BGM を流す長さ(分)

# --- 天気 ---
# tenki.jp の予報地点ページ URL。末尾が地域コード。
# 別地域に変える場合は tenki.jp の該当ページの URL に差し替える。
# 下記は「愛知県名古屋市中区」。
WEATHER_FORECAST_URL = "https://tenki.jp/forecast/5/26/5110/23103/"

# --- 列車時刻表 ---
TRAIN_SCHEDULE_FILE_A = os.path.join(BASE_DIR, "data", "train_schedule_a.json")
TRAIN_SCHEDULE_FILE_B = os.path.join(BASE_DIR, "data", "train_schedule_b.json")
TRAIN_SCHEDULE_FILE_C = os.path.join(BASE_DIR, "data", "train_schedule_c.json")
# 表示する路線見出し(A/B は同一路線の上下方向、C は別路線という構成)
TRAIN_LINE_AB_NAME = "名城線"
TRAIN_LINE_C_NAME = "上飯田線"

# --- 画像自動取得(Pexels) ---
PEXELS_IMAGE_URL = "https://images.pexels.com/photos/{}/pexels-photo-{}.jpeg"
PEXELS_MIN_ID = 0
PEXELS_MAX_ID = 18200000
