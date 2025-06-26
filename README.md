# Music Scheduler

定期的に音楽を自動再生するスケジューラーアプリケーションです。

## 概要

Music Schedulerは、設定された期間中に、指定された日を除き（例：土日祝日など）、指定した時刻でMP3ファイルの再生やEXEファイルの実行を自動で行うコマンドライン（CLI）アプリケーションです。一般ユーザーから自治体や学校の職員まで、定期的な音楽再生が必要な環境で活用いただけます。

あらかじめ第４８回全国育樹祭のイメージソング「緑のたましい」が音源として含まれていますが、設定の変更により、他の音源の利用も可能です。

## 主な機能

- **定期自動再生**: 設定した時刻に自動でMP3ファイルを再生
- **スケジュール管理**: 開始日・終了日を指定した期間内での自動実行
- **平日限定実行**: 土日及び指定した休日を自動的に除外
- **複数タスク対応**: １日に複数の時刻でタスクを実行可能
- **MP3再生**: 指定したMP3ファイルの自動再生
- **EXE実行**: 外部プログラムの自動起動
- **二重起動防止**: アプリケーションの重複実行を防止
- **詳細ログ**: 実行状況を詳細にログファイルに記録
- **コマンドライン動作**: CLIによるシンプルな動作

## 必要要件

- **OS**: Windows １１（他のWindowsバージョンでも動作する可能性があります）
- **Python**: ３.６以上
- **必要ライブラリ**:
  - pygame
  - tendo

## インストール

１. このリポジトリをクローンまたはダウンロードします
```bash
git clone [リポジトリURL]
cd music-scheduler
```

２. 必要なライブラリをインストールします
```bash
pip install pygame tendo
```

## 設定ファイル

### config.json
アプリケーションの動作設定を行います。

```json
{
  "schedule_period": {
    "start_date": "2025-06-13",
    "end_date": "2025-10-03"
  },
  "holiday_list_path": "holidays.csv",
  "daily_schedules": [
    {
      "time": "08:20:00",
      "task_type": "play_mp3",
      "task_path": "ikuju.mp3"
    },
    {
      "time": "12:20:00",
      "task_type": "play_mp3",
      "task_path": "ikuju.mp3"
    },
    {
      "time": "17:15:00",
      "task_type": "play_mp3",
      "task_path": "ikuju.mp3"
    }
  ]
}
```

#### 設定項目説明

- **schedule_period**: スケジュール実行期間
  - `start_date`: 開始日（YYYY-MM-DD形式）
  - `end_date`: 終了日（YYYY-MM-DD形式）
- **holiday_list_path**: 休日リストCSVファイルのパス
- **daily_schedules**: 毎日実行するタスクのリスト
  - `time`: 実行時刻（HH:MM:SS形式）
  - `task_type`: タスクタイプ（`play_mp3` または `run_exe`）
  - `task_path`: 実行対象ファイルのパス（相対パスまたは絶対パス）

### holidays.csv
実行を除外する休日を指定します。土日祝日など、音楽を再生したくない日を設定できます。

```csv
2025-06-14
2025-06-15
2025-06-21
2025-06-22
```

各行に YYYY-MM-DD 形式で日付を記載してください。土日以外の祝日や特別休業日を指定できます。

## 使用方法

１. 設定ファイル（config.json、holidays.csv）を適切に設定します

２. 再生したいMP3ファイルをアプリケーションと同じフォルダに配置します
   （デフォルトで「緑のたましい」（ikuju.mp3）が含まれています）

３. アプリケーションを実行します
```bash
python main_app.py
```

４. アプリケーションが起動すると、コンソールに以下の情報が表示されます：
   - 設定内容の確認
   - 今後のスケジュール（最大３０件）
   - 次回実行予定

５. 指定した時刻になると自動でタスクが実行されます

６. すべてのスケジュールが完了すると、アプリケーションは自動的に終了します

## システム設定上の注意

**重要**: Music Schedulerを利用いただく際には、以下のシステム設定を行ってください。

### 必須設定
- **電源管理**: すべてのスケジュールが終了するまで電源を入れっぱなしにする
- **スリープ設定**: システムがスリープモードに入らないよう設定する
- **シャットダウン防止**: 自動シャットダウンを無効にする

### 推奨設定
- **モニタースリープ**: モニター（ディスプレイ）のスリープは有効にする
  - **理由**: 画面を閉じた状態で長時間運用する場合、熱がこもり熱暴走の恐れがあるため
  - モニターのスリープは音楽再生に影響しません

### Windows設定例
```
コントロールパネル > 電源オプション > プラン設定の変更
・コンピューターをスリープ状態にする: なし
・ディスプレイの電源を切る: １５分（推奨）
```

## ログファイル

アプリケーションの実行状況は `app.log` ファイルに記録されます。以下の情報が含まれます：

- アプリケーションの開始・終了
- 設定ファイルの読み込み状況
- スケジュールの計算結果
- タスクの実行結果
- エラー情報

## ファイル構成

```
music-scheduler/
├── main_app.py              # メインアプリケーション
├── config_loader.py         # 設定ファイル読み込み
├── schedule_calculator.py   # スケジュール計算
├── task_executor.py         # タスク実行
├── config.json             # 設定ファイル
├── holidays.csv            # 休日リスト
├── ikuju.mp3              # 「緑のたましい」音源ファイル
├── app.log                # ログファイル（実行時に生成）
├── LICENSE                # MITライセンス
└── README.md              # このファイル
```

## 同梱音源について

このアプリケーションには、第４８回全国育樹祭のイメージソング「緑のたましい」（ikuju.mp3）があらかじめ含まれています。設定を変更することで、お好みの音楽ファイルに変更することも可能です。

## 使用場面

- **合同庁舎**: 定期的な時報や案内音楽の再生
- **オフィス**: 休憩時間の案内音楽
- **学校・公共施設**: チャイムや案内音の自動再生
- **個人利用**: 生活リズムの管理やリマインダー

## 注意事項

１. **二重起動防止**: アプリケーションは同時に１つしか起動できません

２. **ファイルパス**: MP3ファイルやEXEファイルのパスは、相対パス（アプリケーションフォルダからの相対）または絶対パスで指定できます

３. **文字コード**: 休日リストCSVファイルはUTF-８またはShift_JISに対応しています

４. **音楽再生**: MP3再生中はアプリケーションが待機し、再生完了後に次の処理に進みます

５. **エラー処理**: タスク実行に失敗してもアプリケーションは継続して動作します

６. **長期運用**: 熱暴走を防ぐため、モニタースリープの設定を推奨します

## トラブルシューティング

### よくある問題

**Q: アプリケーションが起動しない**
A: 必要なライブラリ（pygame、tendo）がインストールされているか確認してください。

**Q: MP3ファイルが再生されない**
A: ファイルパスが正しいか、ファイルが存在するか確認してください。

**Q: スケジュールが実行されない**
A: 現在の日付が設定した期間内にあるか、休日設定が正しいか確認してください。

**Q: 「アプリケーションが既に起動しています」というエラーが出る**
A: タスクマネージャーで既存のプロセスを終了してから再実行してください。

**Q: 長時間運用していると動作が不安定になる**
A: システムの電源設定を確認し、モニタースリープが有効になっているか確認してください。

### ログの確認

問題が発生した場合は、`app.log` ファイルを確認してください。詳細なエラー情報が記録されています。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

```
MIT License

Copyright (c) 2025 maruaican

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```