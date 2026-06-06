from datetime import datetime, time

def get_next_trains(train_schedule: dict):
    """
    現在時刻から最も近い電車3つを返す
    
    Returns:
        list: 次の電車3つの情報を含むリスト
    """
    now = datetime.now()
    current_time = now.time()
    
    # 平日か休日かを判定
    is_weekday = now.weekday() < 5
    schedule = train_schedule["weekday"] if is_weekday else train_schedule["weekend"]
    
    # 現在時刻以降の電車をフィルタリング
    upcoming_trains = []
    for train in schedule:
        train_time = datetime.strptime(train["time"], "%H:%M").time()
        if train_time >= current_time:
            upcoming_trains.append(train)
    
    # 現在時刻以降の電車がない場合は翌日の最初の電車を追加
    if not upcoming_trains:
        upcoming_trains = schedule[:3]
    
    # 必要な電車の数を計算
    needed_trains = 3 - len(upcoming_trains)
    
    # 足りない場合は翌日の電車を追加
    if needed_trains > 0:
        upcoming_trains.extend(schedule[:needed_trains])
    
    # 最大3つまでの電車を返す
    return upcoming_trains[:3]
