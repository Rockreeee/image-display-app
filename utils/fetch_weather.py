import requests
from bs4 import BeautifulSoup
import re

def get_precipitation_forecast():

    try:
        # 気象情報サイトのURL
        url = f"https://tenki.jp/forecast/5/26/5110/23230/"

        # HTTPリクエストを送信してページのHTMLを取得
        response = requests.get(url)
        if response.status_code == 200:

            # HTMLをパースしてBeautifulSoupオブジェクトを作成
            soup = BeautifulSoup(response.content, "html.parser")

            # 天気
            weather_text = ""
            # 最高気温
            high_temperature_value = ""
            # 降水確率を格納するリスト
            probabilities = []

            # classがweather-telopのp要素を取得
            weather_telop = soup.find('p', class_='weather-telop')

            # テキストを取得
            if weather_telop:
                weather_text = weather_telop.text
            else:
                weather_text = "--"


            # classがhigh-temp tempのdd要素を取得
            temperature_dd = soup.find('dd', class_='high-temp temp')

            # 最高温度を取得
            if temperature_dd:
                temperature_span = temperature_dd.find('span', class_='value')
                if temperature_span:
                    high_temperature_value = temperature_span.text
                else:
                    high_temperature_value = "--"
            else:
                print("要素が見つかりませんでした")
            

            # classがlow-temp tempのdd要素を取得
            temperature_dd = soup.find('dd', class_='low-temp temp')

            # 最高温度を取得
            if temperature_dd:
                temperature_span = temperature_dd.find('span', class_='value')
                if temperature_span:
                    low_temperature_value = temperature_span.text
                else:
                    low_temperature_value = "--"
            else:
                print("要素が見つかりませんでした")


            # classがrain-probabilityのtr要素を取得
            rain_probability_tr = soup.find('tr', class_='rain-probability')

            # 降水確率を取得
            if rain_probability_tr:
                probability_tds = rain_probability_tr.find_all('td')  # 全てのtd要素を取得
                for td in probability_tds:
                    probability_span = td.find('span', class_='unit')
                    if probability_span:
                        probability_value = td.text.replace('%', '')  # %を削除して数値のみを取得
                        probabilities.append(probability_value)
                    else:
                        probabilities.append("--")  # 確率が見つからない場合はNoneを追加
            else:
                print("要素が見つかりませんでした")

            
            # 今日と明日の天気を取得
            # 天気データを格納するリスト
            today_and_tomorrow_weather_data = []
            # forecast-days-wrap clearfixの中のみを対象にする
            forecast_wrap = soup.find('div', class_='forecast-days-wrap clearfix')
            for section in forecast_wrap.find_all('section'):
                date = section.find('h3').get_text().strip()  # 日付と曜日
                
                # 正規表現を使って「11月17日(日)」のように抽出
                date_match = re.search(r'(\d{1,2}月\d{1,2}日)\((.*?)\)', date)
                if date_match:
                    date = f"{date_match.group(1)}({date_match.group(2)})"  # 日付と曜日のフォーマットを整える

                weather = section.find('p', class_='weather-telop').get_text().strip()  # 天気
                high_temp = section.find('dd', class_='high-temp temp').find('span', class_='value').get_text().strip()  # 最高気温
                low_temp = section.find('dd', class_='low-temp temp').find('span', class_='value').get_text().strip()  # 最低気温
                precip = section.find('tr', class_='rain-probability').find_all('td')[2].get_text().strip()  # 降水確率

                # 抽出したデータを辞書形式で格納
                today_and_tomorrow_weather_data.append({
                    'date': date,
                    'weather': weather,
                    'high_temp': high_temp,
                    'low_temp': low_temp,
                    'precip': precip
                })
            

            # ９日間の天気を取得
            # 天気テーブルを抽出
            forecast_table = soup.find('table', class_='forecast-point-week forecast-days-long')
            # 各日の天気情報を格納するリスト
            nine_days_weather_data = []
            # 各行を取得
            days = forecast_table.find_all('tr')

            # 日付、天気、気温、降水確率を抽出
            for i, day in enumerate(days):
                # 日付と曜日
                if i == 0:
                    dates = day.find_all('td', class_='cityday')
                    for date in dates:
                        date_text = date.get_text(strip=True)
                        nine_days_weather_data.append({'date': date_text})
                
                # 天気情報
                elif i == 1:
                    weathers = day.find_all('td', class_='weather-icon')
                    for j, weather in enumerate(weathers):
                        weather_desc = weather.find('p').get_text(strip=True)
                        nine_days_weather_data[j]['weather'] = weather_desc
                
                # 気温情報
                elif i == 2:
                    temperatures = day.find_all('td')
                    for j, temp in enumerate(temperatures):  # 最初のtdは日付なのでスキップ
                        high_temp = temp.find_all('p')[0].get_text(strip=True)
                        low_temp = temp.find_all('p')[1].get_text(strip=True)
                        nine_days_weather_data[j]['high_temp'] = high_temp
                        nine_days_weather_data[j]['low_temp'] = low_temp
                
                # 降水確率情報
                elif i == 3:
                    precipitations = day.find_all('td')
                    for j, precip in enumerate(precipitations):  # 最初のtdは日付なのでスキップ
                        precip = precip.find('p').get_text(strip=True)
                        nine_days_weather_data[j]['precip'] = precip

            return {
                "weather": weather_text,
                "high_temperature_value": high_temperature_value,
                "low_temperature_value": low_temperature_value,
                "probabilities": probabilities,
                "weather_data": today_and_tomorrow_weather_data + nine_days_weather_data
            }
        
    except requests.exceptions.RequestException as e:
        # リクエストが失敗した場合の処理
        print("天気取得でエラーが発生しました:")

        return {
            "weather": "--",
            "high_temperature_value": "--",
            "low_temperature_value": "--",
            "probabilities": ["--", "--", "--", "--"],
            "weather_data": []
        }
    
    else:
        return "サーバーからデータを取得できませんでした。"

