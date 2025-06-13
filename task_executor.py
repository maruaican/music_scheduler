# task_executor.py

import os
import subprocess
import time

try:
    import pygame
except ImportError:
    pygame = None

def play_mp3_safely(file_path: str) -> (bool, str):
    if not pygame:
        return False, "Pygameライブラリがロードされていません。"
    if not os.path.exists(file_path):
        return False, f"再生対象のMP3ファイルが見つかりません: {file_path}"

    try:
        # --- 再生処理の初期化 ---
        # 毎回mixerを初期化することで、前回の影響をなくす
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        
        # --- 再生の開始と待機 ---
        pygame.mixer.music.play()
        
        # ★★★ 最重要：音楽が再生中である間、ここで処理を待機させる ★★★
        while pygame.mixer.music.get_busy():
            time.sleep(0.2) # CPU負荷を抑えつつ待機
        
        # --- 確実なリソース解放 ---
        # ループを抜けたら再生終了 or エラーなので、mixerを終了させる
        pygame.mixer.quit()
        
        return True, "再生が正常に完了しました。"
    except Exception as e:
        # エラーが発生した場合も、可能な限りリソースを解放する
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        return False, f"MP3再生中に予期せぬエラーが発生しました: {e}"

def run_exe(file_path: str) -> (bool, str):
    """
    指定されたEXEファイルを非同期で実行する。
    Returns:
        (bool, str): (成功/失敗, メッセージ) のタプル
    """
    if not os.path.exists(file_path):
        return False, f"実行対象のファイルが見つかりません: {file_path}"
    
    try:
        subprocess.Popen([file_path])
        return True, "プログラムの起動に成功しました。"
    except PermissionError:
        return False, f"ファイルの実行権限がありません: {file_path}"
    except Exception as e:
        return False, f"プログラム実行中に予期せぬエラーが発生しました: {e}"