# VLC動画再生機能

## 概要
低スペック端末でも軽快に動作するVLCベースの動画再生機能です。

## 特徴
- **軽量**: VLCのハードウェアアクセラレーションを活用
- **高品質**: 元の動画の品質を維持
- **安定性**: プロの動画プレイヤーエンジンを使用
- **互換性**: ほとんどの動画形式に対応

## インストール

### 1. VLCメディアプレイヤーのインストール
- **macOS**: `brew install vlc` または [VLC公式サイト](https://www.videolan.org/vlc/)からダウンロード
- **Ubuntu/Debian**: `sudo apt install vlc`
- **Windows**: [VLC公式サイト](https://www.videolan.org/vlc/)からダウンロード

### 2. Pythonパッケージのインストール
```bash
pip install -r requirements_video.txt
```

## 使用方法

### 動画再生の開始
```python
from screens.video_mode_screen_vlc import create_screen
create_screen()
```

### キー操作
- `ESC` または `q`: 終了
- `f`: 全画面切り替え
- `h`: カーソル表示/非表示
- `v`: 音量調整
- `m`: ミュート
- `i`: 明るさ調整
- `Space`: 次の動画

## パフォーマンス比較

| 方式 | CPU使用率 | メモリ使用量 | 対応形式 | 安定性 |
|------|-----------|--------------|----------|--------|
| Pygame+OpenCV | 高 | 高 | 限定的 | 中 |
| **VLC** | **低** | **低** | **豊富** | **高** |
| Tkinter+OpenCV | 中 | 中 | 限定的 | 中 |

## 対応動画形式
- MP4, AVI, MOV, MKV, WMV, FLV
- その他VLCが対応する全形式

## トラブルシューティング

### VLCが見つからないエラー
```bash
# macOS
brew install vlc

# Ubuntu
sudo apt update && sudo apt install vlc

# パスが通っていない場合
export PATH="/Applications/VLC.app/Contents/MacOS:$PATH"  # macOS
```

### 動画が再生されない
1. VLCが正しくインストールされているか確認
2. 動画ファイルのパスが正しいか確認
3. 動画ファイルが破損していないか確認

## 設定
`utils/settings_manager.py`で以下の設定が可能：
- `video_path`: 動画ファイルのディレクトリ
- `interval`: 動画切り替え間隔（秒）
- `play_video_audio`: 動画音声の再生有無 