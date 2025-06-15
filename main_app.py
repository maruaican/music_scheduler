# main_app.py

import logging
import os
import sys
import time
from datetime import datetime, date, timedelta
import threading
import copy

# --- ★★★ アプリケーションの二重起動を防止するためのライブラリ ★★★ ---
try:
    from tendo import singleton
except ImportError:
    print("エラー: tendoライブラリが必要です。コマンドプロンプトで 'pip install tendo' を実行してください。")
    sys.exit(1)

# ★★★ この一行で、アプリケーションのインスタンスが一つであることを保証する ★★★
# もし既に起動している場合、ここでプログラムは例外を発生させて終了する。
me = singleton.SingleInstance()


# --- 自作モジュール（task_executorは新しいものをインポート） ---
try:
    from config_loader import load_config
    from schedule_calculator import calculate_schedule
    from task_executor import play_mp3_safely, run_exe
except ImportError as e:
    print(f"エラー: 必要なモジュールファイルが見つかりません: {e.name}.py")
    sys.exit(1)

# --- グローバル変数と状態管理 ---
APP_STATUS = { "status": "初期化中...", "config": {}, "full_schedule_for_ui": [], "log_file_path": "", "next_task_time": "N/A", "pending_task_count": 0 }
status_lock = threading.Lock()

def setup_logging(base_path: str):
    log_file_path = os.path.join(base_path, 'app.log')
    with status_lock:
        APP_STATUS["log_file_path"] = log_file_path
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', handlers=[logging.FileHandler(log_file_path, encoding='utf-8'), logging.StreamHandler(sys.stdout)])
# --- スケジューラループ ---
def scheduler_loop(config, base_path):
    last_checked_date = None
    last_schedule_display_date = None # スケジュール表示の最終日付
    tasks_for_today = []

    while True:
        try:
            now = datetime.now()
            current_date = now.date()
            current_time = now.time()

            # 毎朝8:00に今後のスケジュールを表示
            if current_time >= datetime.strptime("08:00:00", "%H:%M:%S").time() and \
               (last_schedule_display_date is None or current_date > last_schedule_display_date):
                
                logging.info("========================================")
                logging.info("今後のスケジュールを表示します。")
                logging.info("========================================")

                # 今後1年間のスケジュールを計算
                temp_config_for_future = copy.deepcopy(config)
                temp_config_for_future['schedule_period']['start_date'] = current_date.strftime('%Y-%m-%d')
                original_end_date_str = config['schedule_period']['end_date']
                original_end_date = datetime.strptime(original_end_date_str, '%Y-%m-%d').date()
                one_year_later_date = current_date + timedelta(days=365)
                display_end_date = min(original_end_date, one_year_later_date)
                temp_config_for_future['schedule_period']['end_date'] = display_end_date.strftime('%Y-%m-%d')
                
                future_schedule = calculate_schedule(temp_config_for_future, base_path)
                future_schedule.sort(key=lambda x: x['datetime'])
                
                # 現在時刻より後のタスクのみを抽出し、最大30件表示
                upcoming_tasks = [t for t in future_schedule if t['datetime'] > now][:30]

                if upcoming_tasks:
                    logging.info("--- 今後のタスク (最大30件を表示) ---")
                    for i, task in enumerate(upcoming_tasks):
                        logging.info(f"  {i+1:02d}. {task['datetime'].strftime('%Y-%m-%d %H:%M:%S (%a)')} - {task['task_type']}: {task['task_path']}")
                    logging.info("-----------------------------------------")
                else:
                    logging.info("今後のタスクはありません。")
                
                last_schedule_display_date = current_date

            if last_checked_date is None or current_date > last_checked_date:
                logging.info(f"新しい日 ({current_date}) のスケジュールを計算します。")
                
                temp_config = copy.deepcopy(config)
                temp_config['schedule_period']['start_date'] = current_date.strftime('%Y-%m-%d')
                temp_config['schedule_period']['end_date'] = current_date.strftime('%Y-%m-%d')
                
                tasks_for_today = calculate_schedule(temp_config, base_path)
                tasks_for_today.sort(key=lambda x: x['datetime'])
                
                tasks_for_today = [t for t in tasks_for_today if t['datetime'] > now]

                # ログ出力の前に、未実行タスクの件数を更新
                with status_lock:
                    APP_STATUS["full_schedule_for_ui"] = copy.deepcopy(tasks_for_today)
                    APP_STATUS["status"] = "監視中"
                    APP_STATUS["pending_task_count"] = len(tasks_for_today)
                    APP_STATUS["next_task_time"] = tasks_for_today[0]['datetime'].strftime('%Y-%m-%d %H:%M:%S (%a)') if tasks_for_today else "なし"
    
                logging.info(f"本日 ({current_date}) の未実行タスク: {len(tasks_for_today)}件。")
                if tasks_for_today:
                    next_task_info = tasks_for_today[0]
                    logging.info(f"  次のタスク: {next_task_info['datetime'].strftime('%Y-%m-%d %H:%M:%S (%a)')} - {next_task_info['task_type']}: {next_task_info['task_path']}")
                # tasks_for_todayが空の場合、「タスクはありません」というログは件数0のログでカバーされるため、ここでは追加しない。
                last_checked_date = current_date

            if not tasks_for_today:
                with status_lock:
                    APP_STATUS["status"] = "本日のタスク完了、待機中"
                logging.info("========================================")
                logging.info("本日のスケジュールは、終了しました。")
                logging.info("明日のスケジュールまでこのまま待機します。")
                logging.info("========================================")
                time.sleep(60) # 1分間待機してループを継続
                continue
            
            next_task = tasks_for_today[0]
            
            if now < next_task['datetime']:
                time.sleep(1)
                continue

            # --- 実行時刻に到達 ---
            with status_lock:
                APP_STATUS["status"] = f"実行中: {next_task['task_type']}"
            logging.info(f"実行時刻です。タスクを実行 -> [{next_task['task_type']}] {next_task['task_path']}")
            
            executed_task = tasks_for_today.pop(0) # 実行したタスクをリストから削除
            
            success, message = False, ""
            if executed_task['task_type'] == 'play_mp3':
                success, message = play_mp3_safely(executed_task['task_path'])
            elif executed_task['task_type'] == 'run_exe':
                success, message = run_exe(executed_task['task_path'])
            
            logging.info(f"タスク実行結果: {message}")
            if not success:
                logging.error("タスク実行でエラーが発生しました。")

            # --- 実行後処理 ---
            with status_lock:
                APP_STATUS["pending_task_count"] = len(tasks_for_today)
                APP_STATUS["next_task_time"] = tasks_for_today[0]['datetime'].strftime('%Y-%m-%d %H:%M:%S (%a)') if tasks_for_today else "なし"
                APP_STATUS["status"] = "監視中"
            
            if tasks_for_today:
                next_upcoming_task = tasks_for_today[0]
                logging.info(f"次回のスケジュール: {next_upcoming_task['datetime'].strftime('%Y-%m-%d %H:%M:%S (%a)')} - {next_upcoming_task['task_type']}: {next_upcoming_task['task_path']}")
            else:
                logging.info("本日の残りのスケジュールはありません。")
        
        except Exception as e:
            logging.critical(f"ループで致命的エラー: {e}", exc_info=True)
            with status_lock:
                APP_STATUS["status"] = "エラー発生"
            time.sleep(5)

# --- メイン実行ブロック ---
if __name__ == '__main__':
    base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    setup_logging(base_path)
    logging.info("========================================")
    logging.info("音楽再生スケジューラを開始します。")
    logging.info("========================================")

    config = load_config(os.path.join(base_path, 'config.json'))
    if not config:
        logging.error("設定読込失敗。終了します。")
        sys.exit(1)
    else:
        logging.info("設定読込成功。")
        logging.info(f"  開始年月日: {config['schedule_period']['start_date']}")
        logging.info(f"  終了年月日: {config['schedule_period']['end_date']}")
        logging.info("  毎日のスケジュール:")
        for schedule in config['daily_schedules']:
            logging.info(f"    - 時刻: {schedule['time']}, タスクタイプ: {schedule['task_type']}, タスクパス: {schedule['task_path']}")
    
    # configのstart_dateが過去の場合の処理
    config_start_date = datetime.strptime(config['schedule_period']['start_date'], '%Y-%m-%d').date()
    today = date.today()
    
    if config_start_date < today:
        logging.warning(f"設定の開始年月日 ({config_start_date}) が過去の日付です。")
        logging.warning(f"これを無視して、本日 ({today}) からのスケジュールを実行します。")
        config['schedule_period']['start_date'] = today.strftime('%Y-%m-%d')
    
    future_schedule = calculate_schedule(config, base_path)
    with status_lock:
        APP_STATUS["config"] = config
        APP_STATUS["full_schedule_for_ui"] = copy.deepcopy(future_schedule)

    scheduler_thread = threading.Thread(target=scheduler_loop, args=(config, base_path,), daemon=True)
    scheduler_thread.start()

    try:
        while scheduler_thread.is_alive():
            scheduler_thread.join(timeout=1.0)
    except KeyboardInterrupt:
        logging.info("アプリケーションを終了します。")