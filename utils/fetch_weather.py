import requests
from bs4 import BeautifulSoup
import os
from PIL import Image

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
                weather = section.find('p', class_='weather-telop').text.strip() if section.find('p', class_='weather-telop') else "--"
                high_temp = section.find('dd', class_='high-temp temp').find('span', class_='value').text.strip() if section.find('dd', class_='high-temp temp') else "--"
                low_temp = section.find('dd', class_='low-temp temp').find('span', class_='value').text.strip() if section.find('dd', class_='low-temp temp') else "--"
                precip = section.find('tr', class_='rain-probability').find_all('td')[2].text.strip() if section.find('tr', class_='rain-probability') else "--"
                weather_image_path = get_weather_image(weather)

                today_and_tomorrow_weather_data.append({
                    'date': date,
                    'weather': weather,
                    'high_temp': high_temp,
                    'low_temp': low_temp,
                    'precip': precip,
                    'weather_image_path': weather_image_path
                })

        # 9日間の天気
        forecast_table = soup.find('table', class_='forecast-point-week forecast-days-long')
        if forecast_table:
            rows = forecast_table.find_all('tr')
            for i, row in enumerate(rows):
                if i == 0:  # 日付
                    dates = row.find_all('td', class_='cityday')
                    for date in dates:
                        date_text = date.text.strip() if date else "--"
                        nine_days_weather_data.append({'date': date_text})
                elif i == 1:  # 天気
                    weathers = row.find_all('td', class_='weather-icon')
                    for j, weather in enumerate(weathers):
                        weather_desc = weather.find('p').text.strip() if weather.find('p') else "--"
                        nine_days_weather_data[j]['weather'] = weather_desc
                        nine_days_weather_data[j]['weather_image_path'] = get_weather_image(weather_desc)
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

        print(
            "today_probabilities", today_probabilities,
            "weather_data", today_and_tomorrow_weather_data + nine_days_weather_data)

        return {
            "today_probabilities": today_probabilities,
            "weather_data": today_and_tomorrow_weather_data + nine_days_weather_data
        }

    except requests.exceptions.RequestException as e:
        print(f"HTTPリクエストエラー: {e}")
    except Exception as e:
        print(f"予期せぬエラー: {e}")

    return {
        "today_probabilities": ["--", "--", "--", "--"],
        "weather_data": []
    }

def get_weather_image(weather_text, image_folder="utils/weather_images"):
    # 天気テキストと画像ファイル名の対応表
    weather_to_image_map = {
        "晴": "sunny.png",
        "雨": "rainy.png",
        "曇": "cloudy.png",
        "雪": "snowy.png",
        "暴風雨": "storm.png",
        "暴風雪": "snowy.png",
        "晴後雨": "sunny_or_rainy.png",
        "晴時々曇": "sunny_or_rainy.png",
        "曇時々晴": "sunny_or_rainy.png",
    }

    # 天気画像フォルダ内の対応する画像ファイル名を取得
    image_file_name = weather_to_image_map.get(weather_text, None)
    if not image_file_name:
        print(f"対応する天気画像が見つかりません: {weather_text}")
        return ""

    # 画像ファイルの完全なパスを取得
    image_path = os.path.join(image_folder, image_file_name)

    return image_path