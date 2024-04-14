import requests
from bs4 import BeautifulSoup

def get_precipitation_forecast():

    try:

        # 気象情報サイトのURL
        url = f"https://tenki.jp/forecast/5/26/5110/23211/"

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

            return {
                "weather": weather_text,
                "high_temperature_value": high_temperature_value,
                "low_temperature_value": low_temperature_value,
                "probabilities": probabilities
            }
    except requests.exceptions.RequestException as e:
        # リクエストが失敗した場合の処理
        print("天気取得でエラーが発生しました:")

        return {
            "weather": "--",
            "high_temperature_value": "--",
            "low_temperature_value": "--",
            "probabilities": ["--", "--", "--", "--"]
        }
    


    else:
        return "サーバーからデータを取得できませんでした。"

