import json
import os
import sys


def load_config(config_file_path: str):
    """
    指定されたパスから設定ファイル(config.json)を読み込み、内容を辞書として返す。

    Args:
        config_file_path (str): config.jsonのフルパス

    Returns:
        dict: 読み込まれた設定データ
        None: エラーが発生した場合
    """
    # print()はテスト段階での表示なので、loggingに置き換えるのが望ましいが、
    # このモジュールはlogging設定前に呼ばれる可能性があるのでprintのままにしておく。
    print(f"情報: 設定ファイル '{config_file_path}' を読み込んでいます。")

    if not os.path.exists(config_file_path):
        print("エラー: 設定ファイルが見つかりません。")
        print(f"パス: {config_file_path}")
        return None

    try:
        # 文字コード 'utf-8-sig' は、BOM付きUTF-8ファイルにも対応可能
        with open(config_file_path, "r", encoding="utf-8-sig") as f:
            config = json.load(f)
        print("情報: 設定ファイルの読み込みに成功しました。")
        return config
    except json.JSONDecodeError as e:
        print("エラー: 設定ファイルの書式がJSONとして正しくありません。")
        print(f"エラー箇所: {e}")
        return None
    except Exception as e:
        print("エラー: 設定ファイルの読み込み中に予期せぬエラーが発生しました。")
        print(f"エラー詳細: {e}")
        return None


# --- このファイル単体で実行した際の動作確認 ---
if __name__ == "__main__":
    base_path = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(__file__)
    config_path = os.path.join(base_path, "config.json")

    dummy_config_data = {
        "schedule_period": {"start_date": "2025-06-16", "end_date": "2025-09-15"},
        "holiday_list_path": "holidays.csv",
        "daily_schedules": [
            {
                "time": "08:30:00",
                "task_type": "play_mp3",
                "task_path": "C:\\MyApp\\Music\\morning.mp3",
            }
        ],
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(dummy_config_data, f, indent=2, ensure_ascii=False)

    config_data = load_config(config_path)

    if config_data:
        print("\n--- 読み込まれた設定内容 ---")
        print(json.dumps(config_data, indent=2, ensure_ascii=False))
        print("--------------------------")
    else:
        print("\n設定の読み込みに失敗したため、処理を中断します。")
