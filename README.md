# Image Display App
- 思い出の写真を飾る
- 好きなアーティストの絵画をランダムで飾る
- 時間を確かめる
- 毎日の天気、降水確率を見る

## Features

<img src="asset/1.jpg" alt="代替テキスト" width="200" height="200" />
<img src="asset/2.png" alt="代替テキスト" width="100" height="200" />
<img src="asset/3.png" alt="代替テキスト" width="100" height="200" />
<img src="asset/4.png" alt="代替テキスト" width="200" height="140" />

## Requirement

* python
* pillow
* tkinter

## Installation

pythonインストール方法
```zsh
brew install python
```

tkinterインストール方法
```zsh
brew install python-tk
```

pillowインストール方法
```zsh
pip install pillow
```

opencvインストール方法

```zsh
pip install opencv-python
```

beautifulsoup4インストール方法

```zsh
pip install beautifulsoup4
```

## Usage


```zsh
git clone https://github.com/hoge/~
cd ~
python main.py
```

# Image mode
## 設定変数
- Image Directory: 画像が保存されているディレクトリを選択してください
- Display Interval: 画像が切り替わるまでの時間
- Show Margin: 余白を表示するか否か
- Automatic Brightness: 明るさを自動調整するか否か（21:00に暗くなり、07:00に明るくなる）
- Show Clock: 時間を表示するか否か（Show Marginもonにする必要があります）
- Show Weather:天気を表示するか否か（Show Marginもonにする必要があります）(Net環境必要)

## キーバインド
- \<Escape key> or \<q key>: 終了する
- \<b key>: 周りの枠の明るさ調整
- \<i key>: imageの明るさ調整
- \<f key>: ウィンドウ大きさ変更
- \<h key>: カーソル表示切り替え
- \<v key>: 音量の調整
- \<m key>: ミュートの切り替え
- \<Space key>: 次の画像に移動する


# Movie mode
- 実装中


# Study mode
## 設定変数
- Study Directory: 問題が保存されているディレクトリを選択してください
- Answer Interval: 答えが出るまでの時間
- Change Interval: 問題が変わるまでの時間

## キーバインド
- \<Escape key> or \<q key>: 終了する
- \<Space key>: 暗記完了（ループから削除されて、もう表示されない）
- \<b key>: 明るさ調整


## Tips
Linux環境で動作させる場合以下のようなファイルを作成すれば毎度`python main.py`を入力しなくて済みます。
```image_display_app.desktop
[Desktop Entry]
Name=Image Display App
Exec=/usr/bin/python /path/to/main.py
Icon=/path/to/asset/icon.jpeg
Terminal=true
Type=Application
Categories=Utility;
```

おすすめ画像収集サイト：
https://www.pexels.com/ja-jp/search/%E9%A2%A8%E6%99%AF/


おすすめ絵画収集方法：
https://sleepygamersmemo.blogspot.com/2018/11/download-from-wikiart-with-tampermonkey.html

## Note

使用は自己責任です