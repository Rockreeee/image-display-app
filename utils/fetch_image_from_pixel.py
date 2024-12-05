import requests
import random
from PIL import Image
from io import BytesIO

# ベースURL
base_url = "https://images.pexels.com/photos/{}/pexels-photo-{}.jpeg"

# ランダムIDの範囲
min_id = 0
max_id = 18200000

def find_existing_image():
    while True:
        # ランダムなIDを生成
        random_id = random.randint(min_id, max_id)
        # 完全なURLを生成
        image_url = base_url.format(random_id, random_id)
        
        try:
            # URLの存在確認
            response = requests.head(image_url)
            if response.status_code == 200:
                print(f"画像が見つかりました: {image_url}")
                return image_url
            else:
                print(f"画像が見つかりませんでした: {image_url}")
        except requests.exceptions.RequestException as e:
            print(f"エラーが発生しました: {e}")



def fetch_image_from_url():
    response = requests.get(find_existing_image())
    response.raise_for_status()  # HTTPエラーがあれば例外をスロー
    return Image.open(BytesIO(response.content))
