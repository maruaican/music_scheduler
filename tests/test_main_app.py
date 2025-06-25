import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# モジュール検索パスにプロジェクトルートを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# main_app をインポートする前に、一部の重いライブラリをモック
# これらは main_app インポート時に読み込まれるため、グローバルにモックする
sys.modules['tendo'] = MagicMock()
sys.modules['pygame'] = MagicMock()

import main_app  # noqa: E402

# --- テストケース ---

@patch('main_app.threading.Thread')
@patch('main_app.scheduler_loop')
@patch('main_app.setup_logging')
@patch('main_app.calculate_schedule')
@patch('main_app.load_config')
@patch('main_app.singleton')
def test_main_app_starts_successfully(mock_singleton, mock_load_config, mock_calculate_schedule, mock_setup_logging, mock_scheduler_loop, mock_thread):
    """
    設定が正常に読み込めた場合に、スケジューラスレッドが正常に起動することを確認するテスト
    """
    # モックの設定
    mock_load_config.return_value = {
        "schedule_period": {"start_date": "2025-01-01", "end_date": "2025-01-01"},
        "holiday_list_path": "holidays.csv",
        "daily_schedules": []
    }
    mock_calculate_schedule.return_value = []
    
    # スレッドの is_alive と join の振る舞いを設定
    mock_thread.return_value.is_alive.side_effect = [True, False]
    mock_thread.return_value.join.return_value = None

    # main関数を実行
    main_app.main()

    # 各コンポーネントが期待通りに呼び出されたか検証
    mock_singleton.SingleInstance.assert_called_once()
    mock_setup_logging.assert_called_once()
    mock_load_config.assert_called_once()
    mock_calculate_schedule.assert_called_once()
    
    # スレッドが正しい引数で起動されたか確認
    mock_thread.assert_called_once()
    mock_thread.return_value.start.assert_called_once()
    mock_thread.return_value.join.assert_called()

@patch('main_app.threading.Thread')
@patch('main_app.scheduler_loop')
@patch('main_app.setup_logging')
@patch('main_app.calculate_schedule')
@patch('main_app.load_config')
@patch('main_app.singleton')
def test_main_app_exits_on_config_failure(mock_singleton, mock_load_config, mock_calculate_schedule, mock_setup_logging, mock_scheduler_loop, mock_thread):
    """
    設定の読み込みに失敗した場合に、アプリケーションがsys.exit(1)で終了することを確認するテスト
    """
    # モックの設定: config_loaderがNoneを返すようにする
    mock_load_config.return_value = None

    # main関数を実行し、SystemExitが発生することを確認
    with pytest.raises(SystemExit) as excinfo:
        main_app.main()

    # 終了コードが1であることを検証
    assert excinfo.value.code == 1

    # 各コンポーネントの呼び出しを検証
    mock_singleton.SingleInstance.assert_called_once()
    mock_setup_logging.assert_called_once()
    mock_load_config.assert_called_once()
    
    # これらの関数は呼び出されないはず
    mock_calculate_schedule.assert_not_called()
    mock_scheduler_loop.assert_not_called()
    mock_thread.assert_not_called()