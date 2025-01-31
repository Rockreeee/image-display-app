import requests
from bs4 import BeautifulSoup
import re

def get_precipitation_forecast():
    try:
        # 気象情報サイトのURL
        url = "https://tenki.jp/forecast/5/26/5110/23230/"

        # HTTPリクエストを送信してページのHTMLを取得
        response = requests.get(url)
        response.raise_for_status()  # HTTPステータスコードを確認
        soup = BeautifulSoup(response.content, "html.parser")

        # 天気データ初期化
        today_probabilities = []
        today_and_tomorrow_weather_data = []
        nine_days_weather_data = []

        # 降水確率
        rain_probability_tr = soup.find('tr', class_='rain-probability')
        if rain_probability_tr:
            probability_tds = rain_probability_tr.find_all('td')
            for td in probability_tds:
                probability_value = td.text.strip().replace('%', '') if td.text.strip() else "--"
                today_probabilities.append(probability_value)

        # 今日と明日の天気
        forecast_wrap = soup.find('div', class_='forecast-days-wrap clearfix')
        if forecast_wrap:
            for section in forecast_wrap.find_all('section'):
                date = section.find('h3').text.strip() if section.find('h3') else "--"
                weekday = get_english_weekday(re.search(r'\((.*?)\)', date).group(1))
                weather = section.find('p', class_='weather-telop').text.strip() if section.find('p', class_='weather-telop') else "--"
                high_temp = section.find('dd', class_='high-temp temp').find('span', class_='value').text.strip() if section.find('dd', class_='high-temp temp') else "--"
                low_temp = section.find('dd', class_='low-temp temp').find('span', class_='value').text.strip() if section.find('dd', class_='low-temp temp') else "--"
                precip = section.find('tr', class_='rain-probability').find_all('td')[2].text.strip() if section.find('tr', class_='rain-probability') else "--"
                weather_icon = get_weather_icon(weather)

                today_and_tomorrow_weather_data.append({
                    'date': date,
                    'weekday': weekday,
                    'weather': weather,
                    'high_temp': high_temp,
                    'low_temp': low_temp,
                    'precip': precip,
                    'weather_icon': weather_icon
                })

        # 9日間の天気
        forecast_table = soup.find('table', class_='forecast-point-week forecast-days-long')
        if forecast_table:
            rows = forecast_table.find_all('tr')
            for i, row in enumerate(rows):
                if i == 0:  # 日付
                    dates = row.find_all('td', class_='cityday')
                    for j, date in enumerate(dates):
                        date_text = date.text.strip() if date else "--"
                        # 日付から曜日を抽出し英語に変換
                        match = re.search(r'\((.*?)\)', date_text)
                        weekday = get_english_weekday(match.group(1)) if match else "--"
                        nine_days_weather_data.append({'date': date_text, 'weekday': weekday})
                elif i == 1:  # 天気
                    weathers = row.find_all('td', class_='weather-icon')
                    for j, weather in enumerate(weathers):
                        weather_desc = weather.find('p').text.strip() if weather.find('p') else "--"
                        nine_days_weather_data[j]['weather'] = weather_desc
                        nine_days_weather_data[j]['weather_icon'] = get_weather_icon(weather_desc)
                elif i == 2:  # 気温
                    temperatures = row.find_all('td')
                    for j, temp in enumerate(temperatures):
                        high_temp = temp.find_all('p')[0].text.strip() if len(temp.find_all('p')) > 0 else "--"
                        low_temp = temp.find_all('p')[1].text.strip() if len(temp.find_all('p')) > 1 else "--"
                        nine_days_weather_data[j]['high_temp'] = high_temp
                        nine_days_weather_data[j]['low_temp'] = low_temp
                elif i == 3:  # 降水確率
                    precipitations = row.find_all('td')
                    for j, precip in enumerate(precipitations):
                        precip_text = precip.find('p').text.strip() if precip.find('p') else "--"
                        nine_days_weather_data[j]['precip'] = precip_text

        # print(
        #     "today_probabilities", today_probabilities,
        #     "weather_data", today_and_tomorrow_weather_data + nine_days_weather_data)

        return {
            "today_probabilities": today_probabilities,
            "weather_data": today_and_tomorrow_weather_data + nine_days_weather_data
        }

    except requests.exceptions.RequestException as e:
        print(f"HTTPリクエストエラー: {e}")
    except Exception as e:
        print(f"予期せぬエラー: {e}")

    return {
        None
    }

def get_weather_icon(weather_text):
    # 天気テキストと画像ファイル名の対応表
    weather_to_image_map = {
        "晴": "\u2600",

        "雨": "\u26C6",
        "曇一時雨": "\u26C6",
        "暴風雨": "\u26C6",
        "曇時々雨": "\u26C6",
        "曇のち雨": "\u26C6",

        "曇": "\u2601",
        "晴時々曇": "\u2601",
        "晴のち曇": "\u2601",
        "曇のち晴": "\u2601",
        "雨のち晴": "\u2601",
        "曇時々晴": "\u2601",
        "晴後雨": "\u2601",
        "晴時々雨": "\u2601",
        "晴一時雨": "\u2601",

        "雪": "\u2603",
        "暴風雪": "\u2603",
    }

    # 天気画像フォルダ内の対応する画像ファイル名を取得
    image_icon = weather_to_image_map.get(weather_text, None)
    if not image_icon:
        print(f"対応する天気画像が見つかりません: {weather_text}")
        return ""

    return image_icon

def get_english_weekday(japanese_weekday):
    # 日本語曜日と英語曜日の対応表
    japanese_to_english_map = {
        "日": "Sun.",
        "月": "Mon.",
        "火": "Tue.",
        "水": "Wed.",
        "木": "Thu.",
        "金": "Fri.",
        "土": "Sat.",
    }

    # 対応する英語の曜日を取得
    english_weekday = japanese_to_english_map.get(japanese_weekday)
    if not english_weekday:
        print(f"対応する曜日が見つかりません: {japanese_weekday}")
        english_weekday = japanese_weekday
    return english_weekday