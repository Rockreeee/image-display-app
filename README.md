# Image Display App
- 思い出の写真を飾る
- 好きなアーティストの絵画をランダムで飾る
- 時間を確かめる
- 毎日の天気、降水確率を見る

## Features
![Alt text](/image/1.jpg)
![Alt text](/image/2.png) 
![Alt text](/image/3.png) 

## Requirement

* python
* pillow
* tkinter

## Installation

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
python start.py
```

# Image mode
- Image Directory: 画像が保存されているディレクトリを選択してください
- Display Interval: 画像が切り替わるまでの時間
- Show Margin: 余白を表示するか否か
- Automatic Brightness: 明るさを自動調整するか否か（21:00に暗くなり、07:00に明るくなる）
- Show Clock: 時間を表示するか否か（Show Marginもonにする必要があります）
- Show Weather:天気を表示するか否か（Show Marginもonにする必要があります）(Net環境必要)

- \<Escape key>: 終了する
- \<Space key>: 次の画像に移動する
- \<b key>: 周りの枠の明るさ調整
- \<v key>: imageの明るさ調整
- \<f key>: ウィンドウ大きさ変更
- \<h key>: カーソル表示切り替え

# Movie mode
- 実装中

# Study mode
- Study Directory: 画像が保存されているディレクトリを選択してください
- Answer Interval: 答えが出るまでの時間
- Change Interval: 問題が変わるまでの時間

- \<Escape key>: 終了する
- \<Space key>: 暗記完了（ループから削除されて、もう表示されない）
- \<b key>: 明るさ調整

## Tips

おすすめ画像収集サイト：
https://www.pexels.com/ja-jp/search/%E9%A2%A8%E6%99%AF/


おすすめ絵画収集方法：
https://sleepygamersmemo.blogspot.com/2018/11/download-from-wikiart-with-tampermonkey.html

## Note

使用は自己責任です

<!-- # Author

作成情報を列挙する

* 作成者
* 所属
* E-mail

# License
ライセンスを明示する

"hoge" is under [MIT license](https://en.wikipedia.org/wiki/MIT_License). -->
