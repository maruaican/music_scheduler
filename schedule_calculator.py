import csv
from datetime import datetime, timedelta
import os
import json  # テストコード用にインポート


def read_holidays(holiday_file_path: str) -> set:
    """
    休日リストCSVファイルを読み込み、日付文字列（'YYYY-MM-DD'）のセットを返す。
    UTF-8とShift_JISの文字コードに両対応する。
    """
    holidays = set()
    if not os.path.exists(holiday_file_path):
        print(f"警告: 休日リストファイル '{holiday_file_path}' が見つかりません。")
        return holidays

    try:
        with open(holiday_file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    holidays.add(row[0].strip())
        print("情報: 休日リストをUTF-8で読み込みました。")
        return holidays
    except UnicodeDecodeError:
        print("情報: 休日リストのUTF-8での読み込みに失敗、Shift_JISで再試行します。")
        try:
            with open(
                holiday_file_path, "r", encoding="shift_jis", newline=""
            ) as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        holidays.add(row[0].strip())
            print("情報: 休日リストをShift_JISで読み込みました。")
            return holidays
        except Exception as e:
            print(f"エラー: Shift_JISでの休日リスト読み込みに失敗しました。: {e}")
            return set()
    except Exception as e:
        print(f"エラー: 休日リストの読み込み中に予期せぬエラーが発生しました。: {e}")
        return set()


def calculate_schedule(config: dict, base_path: str) -> list:
    """
    設定情報に基づき、実行すべき全タスクのリスト（日時とタスク内容）を生成する。
    """
    schedule_list = []

    try:
        start_date = datetime.strptime(
            config["schedule_period"]["start_date"], "%Y-%m-%d"
        ).date()
        end_date = datetime.strptime(
            config["schedule_period"]["end_date"], "%Y-%m-%d"
        ).date()
        holiday_path = os.path.join(base_path, config["holiday_list_path"])
    except (KeyError, ValueError) as e:
        print(f"エラー: 設定ファイルの期間指定('start_date', 'end_date')が不正です。: {e}")
        return []

    holidays = read_holidays(holiday_path)

    current_date = start_date
    while current_date <= end_date:
        is_not_holiday = current_date.strftime("%Y-%m-%d") not in holidays

        if is_not_holiday:
            for daily_task in config.get("daily_schedules", []):
                try:
                    task_time = datetime.strptime(
                        daily_task["time"], "%H:%M:%S"
                    ).time()
                    task_datetime = datetime.combine(current_date, task_time)

                    schedule_list.append(
                        {
                            "datetime": task_datetime,
                            "task_type": daily_task["task_type"],
                            "task_path": daily_task["task_path"],
                        }
                    )
                except (KeyError, ValueError) as e:
                    print(
                        f"警告: daily_schedules内のタスク定義が不正なためスキップします。: "
                        f"{daily_task} - {e}"
                    )

        current_date += timedelta(days=1)

    schedule_list.sort(key=lambda x: x["datetime"])

    print(
        f"情報: {start_date} から {end_date} までの期間で、"
        f"{len(schedule_list)}件のタスクをスケジュールしました。"
    )
    return schedule_list


# --- このファイル単体で実行した際の動作確認 ---
if __name__ == "__main__":
    # 循環インポートを避けるため、ここでは config_loader を直接インポートしない
    # 代わりに、このファイルが直接実行されたときだけ動作する簡易的なローダーを使う
    def _load_config_for_test(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    base_path = os.path.dirname(__file__)
    config_path = os.path.join(base_path, "config.json")

    dummy_config = {
        "schedule_period": {
            "start_date": "2025-06-09",
            "end_date": "2025-06-13"
        },
        "holiday_list_path": "holidays_test.csv",
        "daily_schedules": [
            {"time": "09:00:00", "task_type": "test", "task_path": "test.exe"}
        ],
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(
            dummy_config, f, indent=2
        )
    holidays_test_path = os.path.join(base_path, "holidays_test.csv")
    with open(holidays_test_path, "w", encoding="shift_jis") as f:
        f.write("2025-06-10")

    config_data = _load_config_for_test(config_path)
    if config_data:
        full_schedule = calculate_schedule(config_data, base_path)

        print("\n--- 生成されたスケジュール（最初の5件） ---")
        for task in full_schedule[:5]:
            print(
                f"{task['datetime'].strftime('%Y-%m-%d %H:%M:%S (%a)')} - "
                f"{task['task_type']}: {task['task_path']}"
            )
        print("-----------------------------------------")
