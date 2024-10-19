import os

SETTINGS_FILE = ".settings"

# 設定ファイルから設定を読み込む関数
def load_settings(column = int):

    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            lines = f.readlines()
            
            # mode
            if column == 0:
                try:
                    return lines[0].strip()
                except IndexError:
                    return "Image"
            
            # image_path
            if column == 1:
                try:
                    return lines[1].strip()
                except IndexError:
                    return ""
            
            # image_interval
            if column == 2:
                try:
                    return lines[2].strip()
                except IndexError:
                    return "3600"
            
            # margin
            if column == 3:
                try:
                    return lines[3].strip()
                except IndexError:
                    return False
            
            # automatic brightness
            if column == 4:
                try:
                    return lines[4].strip()
                except IndexError:
                    return False
            
            # time
            if column == 5:
                try:
                    return lines[5].strip()
                except IndexError:
                    return False
            
            # weather
            if column == 6:
                try:
                    return lines[6].strip()
                except IndexError:
                    return False
            
            # sound_path
            if column == 7:
                try:
                    return lines[7].strip()
                except IndexError:
                    return ""
            
            # sound
            if column == 8:
                try:
                    return lines[8].strip()
                except IndexError:
                    return False
            
            # morning_sound_mode
            if column == 9:
                try:
                    return lines[9].strip()
                except IndexError:
                    return False
            
            # video_interval
            if column == 10:
                try:
                    return lines[10].strip()
                except IndexError:
                    return "60"
            
            # video_interval
            if column == 11:
                try:
                    return lines[11].strip()
                except IndexError:
                    return "60"
            
            # study_path
            if column == 20:
                try:
                    return lines[20].strip()
                except IndexError:
                    return ""
            
            # study_answer_interval
            if column == 21:
                try:
                    return lines[21].strip()
                except IndexError:
                    return "2"
            
            # study_change_interval
            if column == 22:
                try:
                    return lines[22].strip()
                except IndexError:
                    return "5"

    else:
        # デフォルトの値
        if column == 0:
            return "Image"
        if column == 1:
            return ""
        if column == 2:
            return "3600"
        if column == 3:
            return False
        if column == 4:
            return False
        if column == 5:
            return False
        if column == 6:
            return False
        if column == 7:
            return ""
        if column == 8:
            return False
        if column == 9:
            return False
        if column == 10:
            return ""
        if column == 11:
            return "60"
        if column == 20:
            return ""
        if column == 21:
            return "2"
        if column == 22:
            return "5"

# 設定を設定ファイルに保存する関数
def save_settings(mode=None, 
                image_path=None,
                image_interval=None, 
                show_margin=None, 
                automatic_brightness=None, 
                show_time=None, 
                show_weather=None, 
                sound_path=None,
                sound_mode=None,
                morning_sound_mode=None,
                video_directory=None, 
                video_interval=None,
                study_file=None, 
                study_answer_interval=None, 
                study_change_interval=None):
    
    if mode == None:
        mode = load_settings(column=0)

    if image_path == None:
        image_path = load_settings(column=1)

    if image_interval == None:
        image_interval = load_settings(column=2)

    if show_margin == None:
        show_margin = load_settings(column=3)

    if automatic_brightness == None:
        automatic_brightness = load_settings(column=4)

    if show_time == None:
        show_time = load_settings(column=5)

    if show_weather == None:
        show_weather = load_settings(column=6)

    if sound_path == None:
        sound_path = load_settings(column=7)

    if sound_mode == None:
        sound_mode = load_settings(column=8)

    if morning_sound_mode == None:
        morning_sound_mode = load_settings(column=9)

    if video_directory == None:
        video_directory = load_settings(column=10)

    if video_interval == None:
        video_interval = load_settings(column=11)

    if study_file == None:
        study_file = load_settings(column=20)

    if study_answer_interval == None:
        study_answer_interval = load_settings(column=21)

    if study_change_interval == None:
        study_change_interval = load_settings(column=22)

    with open(SETTINGS_FILE, "w") as f:
        # 書き込む
        f.write(mode + "\n")
        f.write(image_path + "\n")
        f.write(image_interval + "\n")
        f.write(str(show_margin) + "\n")
        f.write(str(automatic_brightness) + "\n")
        f.write(str(show_time) + "\n")
        f.write(str(show_weather) + "\n")
        f.write(sound_path + "\n")
        f.write(str(sound_mode) + "\n")
        f.write(str(morning_sound_mode) + "\n")
        f.write(video_directory + "\n")
        f.write(video_interval + "\n")
        f.write("\n")
        f.write("\n")
        f.write("\n")
        f.write("\n")
        f.write("\n")
        f.write("\n")
        f.write("\n")
        f.write("\n")
        f.write(study_file + "\n")
        f.write(str(study_answer_interval) + "\n")
        f.write(str(study_change_interval) + "\n")
