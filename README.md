音楽再生スケジューラ

※そのうち、ちゃんと作ります。


## 概要

指定したスケジュールに基づいて、MP3ファイルの再生やEXEファイルの実行を自動的に行うアプリケーションです。
祝日や特定の曜日を除外する設定も可能です。

## 機能

*   設定ファイル (`config.json`) に基づいた柔軟なスケジューリング
*   MP3ファイルの再生
*   EXEファイルの実行
*   祝日設定 (`holidays.csv`) による特定日の除外
*   曜日ごとの実行/非実行設定
*   指定期間におけるスケジュール自動生成
*   アプリケーションの二重起動防止
*   実行ログの記録 (`app.log`)

## 動作環境

*   Python 3.x
*   必要なライブラリ:
    *   `tendo` (二重起動防止用): `pip install tendo`
    *   `pygame` (MP3再生用): `pip install pygame`

## インストール方法

1.  リポジトリをクローンまたはダウンロードします。
    ```bash
    git clone https://github.com/your_username/your_repository_name.git
    cd your_repository_name
    ```
2.  必要なライブラリをインストールします。
    ```bash
    pip install tendo pygame
    ```
3.  設定ファイル `config.json` と祝日ファイル `holidays.csv` を適切に設定します。

## 使用方法

1.  `main_app.py` を直接実行するか、ビルドされた実行可能ファイルを実行します。
    ```bash
    python main_app.py
    ```
2.  アプリケーションは起動後、`config.json` の設定に従ってスケジュールタスクを監視・実行します。
3.  ログは `app.log` に出力されます。
4.  アプリケーションを終了する場合は、コンソールで `Ctrl+C` を押してください。

## 設定ファイル

### `config.json`

アプリケーションの動作を制御するためのJSON形式のファイルです。

*   `schedule_period`:
    *   `start_date`: スケジュール生成の開始日 (YYYY-MM-DD)
    *   `end_date`: スケジュール生成の終了日 (YYYY-MM-DD)
*   `daily_schedules`: 毎日の固定スケジュール
    *   `time`: 実行時刻 (HH:MM:SS)
    *   `task_type`: `play_mp3` または `run_exe`
    *   `task_path`: MP3ファイルまたはEXEファイルのパス
*   `weekly_exclusions`: 曜日ごとの除外設定
    *   `monday` ... `sunday`: `true` (実行しない) / `false` (実行する)
*   `holidays_file`: 祝日リストのファイル名 (例: `holidays.csv`)
*   `exclude_holidays`: `true` (祝日を除外) / `false` (祝日も実行)

### `holidays.csv`

祝日の日付を `YYYY-MM-DD` 形式で1行に1つ記述します。

例:
```csv
2024-01-01
2024-01-08
...
```

## ライセンス

このプロジェクトは [ライセンス名] のもとで公開されています。 (必要に応じて変更してください)

