import json
from datetime import datetime, time

# 電車の時刻表データ
DESTINATION = "For Nagoya"

TRAIN_SCHEDULE = {
    "weekday": [
        {"time": "05:45"},
        {"time": "06:10"},
        {"time": "06:33"},
        {"time": "06:47"},
        {"time": "06:57"},
        {"time": "07:06"},
        {"time": "07:19"},
        {"time": "07:28"},
        {"time": "07:36"},
        {"time": "07:42"},
        {"time": "07:51"},
        {"time": "07:59"},
        {"time": "08:09"},
        {"time": "08:18"},
        {"time": "08:27"},
        {"time": "08:36"},
        {"time": "08:49"},
        {"time": "09:00"},
        {"time": "09:13"},
        {"time": "09:22"},
        {"time": "09:38"},
        {"time": "09:54"},
        {"time": "10:09"},
        {"time": "10:21"},
        {"time": "10:39"},
        {"time": "10:51"},
        {"time": "11:09"},
        {"time": "11:21"},
        {"time": "11:39"},
        {"time": "11:51"},
        {"time": "12:09"},
        {"time": "12:21"},
        {"time": "12:39"},
        {"time": "12:51"},
        {"time": "13:09"},
        {"time": "13:21"},
        {"time": "13:39"},
        {"time": "13:51"},
        {"time": "14:09"},
        {"time": "14:21"},
        {"time": "14:39"},
        {"time": "14:55"},
        {"time": "15:10"},
        {"time": "15:23"},
        {"time": "15:40"},
        {"time": "15:53"},
        {"time": "16:10"},
        {"time": "16:23"},
        {"time": "16:40"},
        {"time": "16:53"},
        {"time": "17:10"},
        {"time": "17:23"},
        {"time": "17:40"},
        {"time": "17:53"},
        {"time": "18:10"},
        {"time": "18:23"},
        {"time": "18:40"},
        {"time": "18:53"},
        {"time": "19:06"},
        {"time": "19:20"},
        {"time": "19:34"},
        {"time": "19:43"},
        {"time": "19:54"},
        {"time": "20:12"},
        {"time": "20:24"},
        {"time": "20:42"},
        {"time": "20:54"},
        {"time": "21:12"},
        {"time": "21:24"},
        {"time": "21:35"},
        {"time": "21:56"},
        {"time": "22:09"},
        {"time": "22:22"},
        {"time": "22:35"},
        {"time": "22:56"},
        {"time": "23:09"},
        {"time": "23:26"},
        {"time": "23:41"},
        {"time": "23:51"}
    ],
    "weekend": [
        {"time": "05:45"},
        {"time": "06:07"},
        {"time": "06:28"},
        {"time": "06:45"},
        {"time": "07:00"},
        {"time": "07:15"},
        {"time": "07:28"},
        {"time": "07:43"},
        {"time": "07:59"},
        {"time": "08:08"},
        {"time": "08:23"},
        {"time": "08:38"},
        {"time": "08:52"},
        {"time": "09:03"},
        {"time": "09:22"},
        {"time": "09:33"},
        {"time": "09:52"},
        {"time": "10:03"},
        {"time": "10:21"},
        {"time": "10:39"},
        {"time": "10:51"},
        {"time": "11:09"},
        {"time": "11:21"},
        {"time": "11:39"},
        {"time": "11:51"},
        {"time": "12:09"},
        {"time": "12:21"},
        {"time": "12:39"},
        {"time": "12:51"},
        {"time": "13:09"},
        {"time": "13:21"},
        {"time": "13:39"},
        {"time": "13:51"},
        {"time": "14:09"},
        {"time": "14:21"},
        {"time": "14:39"},
        {"time": "14:51"},
        {"time": "15:09"},
        {"time": "15:21"},
        {"time": "15:39"},
        {"time": "15:51"},
        {"time": "16:09"},
        {"time": "16:21"},
        {"time": "16:39"},
        {"time": "16:51"},
        {"time": "17:09"},
        {"time": "17:21"},
        {"time": "17:39"},
        {"time": "17:51"},
        {"time": "18:09"},
        {"time": "18:21"},
        {"time": "18:39"},
        {"time": "18:51"},
        {"time": "19:09"},
        {"time": "19:21"},
        {"time": "19:39"},
        {"time": "19:51"},
        {"time": "20:09"},
        {"time": "20:21"},
        {"time": "20:39"},
        {"time": "20:51"},
        {"time": "21:10"},
        {"time": "21:22"},
        {"time": "21:35"},
        {"time": "21:56"},
        {"time": "22:09"},
        {"time": "22:22"},
        {"time": "22:35"},
        {"time": "22:56"},
        {"time": "23:09"},
        {"time": "23:41"}
    ]
}

def get_next_trains():
    """
    現在時刻から最も近い電車3つを返す
    
    Returns:
        list: 次の電車3つの情報を含むリスト
    """
    now = datetime.now()
    current_time = now.time()
    
    # 平日か休日かを判定
    is_weekday = now.weekday() < 5
    schedule = TRAIN_SCHEDULE["weekday"] if is_weekday else TRAIN_SCHEDULE["weekend"]
    
    # 現在時刻以降の電車をフィルタリング
    upcoming_trains = []
    for train in schedule:
        train_time = datetime.strptime(train["time"], "%H:%M").time()
        if train_time >= current_time:
            upcoming_trains.append(train)
    
    # 現在時刻以降の電車がない場合は翌日の最初の電車を追加
    if not upcoming_trains:
        upcoming_trains = schedule[:3]
    
    # 最大3つまでの電車を返す
    return upcoming_trains[:3]
