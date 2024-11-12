# Image Display App
**思い出の写真を飾り、好きなアートを楽しみながら、日々の時間と天気を確認できるインターフェース**

<div style="display: flex; gap: 10px;">
    <img src="asset/9.jpg" alt="代替テキスト" width="250" height="380" />
    <img src="asset/8.jpg" alt="代替テキスト" width="250" height="380" />
    <img src="asset/13.jpg" alt="代替テキスト" width="250" height="380" />
    <img src="asset/14.jpg" alt="代替テキスト" width="250" height="380" />
</div>

# 📋主な機能
- 画像表示：写真やアートをランダムに表示
- 時計表示：シンプルな時計を画面に
- 天気と降水確率の確認：日々の天気
- 自動調整：1時間ごとの明るさ調整
- 単語学習：単語を自動表示し、日々の学習に

# 🌄 イメージ
<div style="display: flex; gap: 10px;">
    <img src="asset/2.png" alt="代替テキスト" width="150" height="300" />
    <img src="asset/3.png" alt="代替テキスト" width="150" height="300" />
</div>

**日付時間 + 天気予報 + ランダム画像**  
（左）**昼間**：明るさが最大に設定  
（右）**夜間**：画面が暗くなり、眩しくない

<img src="https://github.com/Rockreeee/image-display-app/raw/main/asset/1.jpg" alt="代替テキスト" width="200" height="200" />

**画像表示モード**: アート作品や写真を飾るイメージ。

<img src="https://github.com/Rockreeee/image-display-app/raw/main/asset/4.png" alt="代替テキスト" width="200" height="130" />

**勉強モード**: 暗記として使える機能。時間とともに覚えたい単語を表示

# 🖥️ システム要件

* **python**
* パッケージ:
    - **pillow** (画像処理)
    - **tkinter** (UI構築)
    - **opencv-python** (動画サポートのため)
    - **beautifulsoup4** (ウェブデータ取得用)

# 🚀インストール手順

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

# 📓利用方法
```zsh
python main.py
```
# 👏 動作画面の様子
<img src="https://github.com/Rockreeee/image-display-app/raw/main/asset/7.png" width="200" height="230" /> 

２つのモードがあります
- 画像表示モード
- 勉強モード

## 🖼 Image Mode
<img src="asset/5.png"/>

### - 設定

- Image Path: 画像フォルダのパス
- Image Display Interval: 画像が切り替わるまでの時間
- Image With Margin: 画像の周りに余白を表示するか否か
- Automatic Brightness Adjustment: 明るさを自動調整するか否か
- Show Clock: 時間を表示するか否か
- Show Weather: 天気を表示するか否か
- Sound Path: 音楽フォルダのパス
- Sound Off: 音楽オフ
- Sound On: 音楽オン
- Morning Sound Only: 朝の10分間音楽を流す

### - キーバインド
- \<Escape key> or \<q key>: 終了する
- \<b key>: 周りの枠の明るさ調整
- \<i key>: 画像の明るさ調整
- \<f key>: ウィンドウ大きさ変更
- \<h key>: カーソル表示切り替え
- \<v key>: 音量の調整
- \<m key>: ミュートの切り替え
- \<Space key>: 次の画像に移動する


## 📺 Movie Mode
- 実装中


## 🧠 Study Mode
<img src="asset/6.png"/>

### - 設定

- Study Directory: 問題が保存されているディレクトリ
- Answer Interval: 答えが出るまでの時間
- Change Interval: 問題が変わるまでの時間

### - キーバインド
- \<Escape key> or \<q key>: 終了する
- \<Space key>: 暗記完了（ループから削除されて、もう表示されない）
- \<b key>: 明るさ調整


# 💡 Tips
Linux環境で動作させる場合以下のようなファイルを作成すれば、毎度`python main.py`を入力しなくて済み、ファイルをクリックするだけでプログラムが実行されます。
```image_display_app.desktop
[Desktop Entry]
Name=Image Display App
Exec=/usr/bin/python /path/to/main.py
Icon=/path/to/asset/icon.jpeg
Terminal=true
Type=Application
Categories=Utility;
```

## 🌐 おすすめ画像収集サイト
画像収集サイト：
https://www.pexels.com/ja-jp/search/%E9%A2%A8%E6%99%AF/


絵画収集方法：
https://sleepygamersmemo.blogspot.com/2018/11/download-from-wikiart-with-tampermonkey.html

# ❗️注意
使用は自己責任です