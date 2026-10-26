# 日本語のお願いで動く猫型ロボット「ムム君」

## 概要
ローカルLLMで日本語の指示を解釈し、Gazebo内の猫型ロボットを
ROS 2経由で操作する。前進・左旋回・右旋回に対応する。
AIの判断を表示し、利用者が y を入力すると動作する。

## 動作確認環境
- Ubuntu 24.04.3 LTS
- ROS 2 Jazzy
- Gazebo Harmonic / Gazebo Sim 8.15.0
- Python 3.12.3
- OllamaとQwen3 4B（モデル名：qwen3:4b）

## ファイル
- mumu.py：日本語入力、LLMへの問い合わせ、動作の選択と実行
- move_forward.sh：前進後に停止
- turn_left.sh：左旋回後に停止
- turn_right.sh：右旋回後に停止
- mumu_world.sdf：猫型ロボットと実験場

## 準備
ROS 2 Jazzy、Gazebo Harmonic、ros_gz_bridge、Python 3、
Ollamaを導入しておく。

Ollama公式：https://docs.ollama.com/linux

モデルを取得する：
```bash
ollama pull qwen3:4b
```

Ollamaが起動していない場合は、別の端末で実行する：
```bash
ollama serve
```

以下の操作は、各端末でこのREADMEと同じフォルダーに移動して行う。
ROS 2の設定を自動で読み込んでいない場合は、各端末で実行する：
```bash
source /opt/ros/jazzy/setup.bash
```

## 起動手順
### 端末1：Gazebo
```bash
gz sim mumu_world.sdf
```
画面左下の再生ボタンを押す。

### 端末2：ROS 2とGazeboの橋渡し
```bash
ros2 run ros_gz_bridge parameter_bridge '/model/vehicle_blue/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'
```

### 端末3：操作プログラム
```bash
python3 mumu.py
```

## 操作
「少し前へ進んで」「左を向いて」「右を向いて」などを入力する。
AIの判断を確認し、y を入力すると実行する。
それ以外の入力では実行を取りやめる。
「終了」でプログラムを終了する。

## 動作の設定
- 前進：0.1 m/s
- 左旋回：0.3 rad/s
- 右旋回：-0.3 rad/s

動作指令の送信処理後、2秒待って停止指令を送る。
通信や処理の待ち時間を含むため、
動作時間・移動距離・回転角度を厳密に保証するものではない。

## AIと補助ルールの役割
Qwen3 4Bが指示を forward・left・right・none に分類する。
AIが出力した文章を任意のコマンドとして実行せず、
用意した3つの動作ファイルだけを呼び出す。

否定・停止の表現は、AIへの問い合わせ前に文字照合で検出し、
動作を見送る。これはAIによる意味理解とは別の補助ルールである。

## 確認した結果
- 「少し前へ進んで」：前進して自動停止
- 「左を向いて」：左旋回して自動停止
- 「右を向いて」：右旋回して自動停止
- 「左に曲がらないで」：補助ルールで動作を見送り
- 「こんにちは」：AIが動かないと判断

初期に使用したQwen3 1.7Bでは、否定表現の誤分類を確認した。
そのため、補助ルールと利用者による実行確認を導入した。
4Bモデルへの変更で否定表現全般の精度が改善したかは未検証。

## 制限
- 補助ルールは文字照合のため、誤検出や見逃しがある。
- 動作中は次の指示を受け付けず、自然言語での緊急停止はできない。
- 必要に応じてGazeboの一時停止ボタンでシミュレーションを止める。
- 障害物回避、目的地への自律移動、音声入力には対応していない。
- 外見の形状と物理計算用の当たり判定は一致していない。
- 応答速度はPCの性能に依存する。

## 参考元と追加した部分
学習の参考：
「gazeboとROS2を連携してロボットを操作する」
https://qiita.com/N622/items/9d89f77d85d9da0af29e

ロボットの物理モデルと駆動設定のベース：
Gazebo公式のdiff_drive.sdf
https://github.com/gazebosim/gz-sim/blob/gz-sim8/examples/worlds/diff_drive.sdf

追加・変更した部分：
- ローカルLLMによる日本語指示の分類
- 分類結果とROS 2動作の接続
- 否定・停止表現を検出する補助ルール
- 実行前の利用者確認
- 猫型の外見、初期位置と向きの変更、緑の車両の削除

制作時には生成AIを説明・コード作成・修正の補助に使用し、
利用者が実行、動作確認、デザインの選択を行った。
