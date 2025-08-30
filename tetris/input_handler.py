"""
人間による手動プレイ用の入力処理システム
"""

import sys
import threading
import time
from queue import Queue, Empty
from typing import Optional, Callable
from .core import Action

# プラットフォーム別のキー入力処理
if sys.platform.startswith('win'):
    import msvcrt
    select = None
    termios = None
    tty = None
else:
    import select
    import termios
    import tty
    msvcrt = None

def get_char():
    """プラットフォームに応じてキー入力を取得"""
    if sys.platform.startswith('win') and msvcrt is not None:
        # Windows用の処理
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch == b'\x00' or ch == b'\xe0':  # 特殊キー
                ch2 = msvcrt.getch()
                return f'SPECIAL_{ord(ch2)}'
            return ch.decode('utf-8', errors='ignore')
        return None
    elif select is not None:
        # Unix/Linux用の処理
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            return sys.stdin.read(1)
        return None
    else:
        return None


class InputHandler:
    """キー入力を処理するクラス"""
    
    def __init__(self):
        self.input_queue = Queue()
        self.running = False
        self.input_thread = None
        self.old_settings = None
        
        # キーマッピング
        self.key_mapping = {
            # 移動キー
            'a': Action.MOVE_LEFT,
            'A': Action.MOVE_LEFT,
            'd': Action.MOVE_RIGHT,
            'D': Action.MOVE_RIGHT,
            'SPECIAL_75': Action.MOVE_LEFT,  # Windows左矢印
            'SPECIAL_77': Action.MOVE_RIGHT,  # Windows右矢印
            '\x1b[D': Action.MOVE_LEFT,  # Unix左矢印
            '\x1b[C': Action.MOVE_RIGHT,  # Unix右矢印
            
            # 回転キー
            'w': Action.ROTATE,
            'W': Action.ROTATE,
            'SPECIAL_72': Action.ROTATE,  # Windows上矢印
            '\x1b[A': Action.ROTATE,  # Unix上矢印
            
            # ドロップキー
            's': Action.SOFT_DROP,
            'S': Action.SOFT_DROP,
            'SPECIAL_80': Action.SOFT_DROP,  # Windows下矢印
            '\x1b[B': Action.SOFT_DROP,  # Unix下矢印
            
            # ハードドロップ
            ' ': Action.HARD_DROP,
        }
        
        # 特殊キー（ゲーム制御）
        self.control_keys = {
            'q': 'quit',
            'Q': 'quit',
            'r': 'restart',
            'R': 'restart',
            '\x1b': 'quit',  # ESCキー
        }
    
    def start(self):
        """入力処理開始"""
        if self.running:
            return
        
        self.running = True
        
        # Unix系の場合は端末設定を変更
        if not sys.platform.startswith('win') and termios is not None and tty is not None:
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
        
        # 入力スレッド開始
        self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self.input_thread.start()
    
    def stop(self):
        """入力処理停止"""
        if not self.running:
            return
        
        self.running = False
        
        # Unix系の場合は端末設定を復元
        if not sys.platform.startswith('win') and self.old_settings and termios is not None:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
        
        # スレッド終了待機
        if self.input_thread:
            self.input_thread.join(timeout=1.0)
    
    def _input_loop(self):
        """入力処理ループ"""
        arrow_sequence = ""
        
        while self.running:
            try:
                char = get_char()
                
                if char is None:
                    time.sleep(0.005)  # CPU使用率を下げる（5msに減らして応答性向上）
                    continue
                
                # Unix系での矢印キー処理
                if not sys.platform.startswith('win') and char == '\x1b':
                    # ESCシーケンス開始
                    arrow_sequence = char
                    continue
                elif arrow_sequence:
                    arrow_sequence += char
                    if len(arrow_sequence) >= 3:
                        # 矢印キーシーケンス完了
                        self.input_queue.put(arrow_sequence)
                        arrow_sequence = ""
                    continue
                
                # 通常のキー処理
                if char:
                    self.input_queue.put(char)
                
            except Exception as e:
                # エラーが発生した場合はループを継続
                time.sleep(0.01)
    
    def get_input(self) -> Optional[str]:
        """キューから入力を取得し、アクションまたはコマンドを返す"""
        try:
            return self.input_queue.get_nowait()
        except Empty:
            return None
    
    def clear_input_buffer(self):
        """入力バッファをクリア"""
        while True:
            try:
                self.input_queue.get_nowait()
            except Empty:
                break


class GameController:
    """ゲーム制御クラス（入力とアクションの橋渡し）"""
    
    def __init__(self):
        self.input_handler = InputHandler()
        self.last_action_time = 0
        self.action_delay = 0.1  # アクション間の最小間隔（100ms）- リピートを防ぐ
        
        # キーリピートは無効化
        self.held_keys = {}
        self.key_repeat_times = {}
    
    def start(self):
        """コントローラー開始"""
        self.input_handler.start()
    
    def stop(self):
        """コントローラー停止"""
        self.input_handler.stop()
    
    def get_action_or_command(self) -> tuple:
        """入力を取得し、アクションまたはコマンドを返す（シンプルワンショット）"""
        current_time = time.time()
        
        # 新しいキー入力をチェック
        key = self.input_handler.get_input()
        if key:
            # 制御コマンドかチェック
            command = self.input_handler.control_keys.get(key)
            if command:
                return None, command
            
            # アクションかチェック
            action = self.input_handler.key_mapping.get(key)
            if action:
                # 最後のアクションから十分時間が経過している場合のみ実行
                if current_time - self.last_action_time >= self.action_delay:
                    self.last_action_time = current_time
                    return action, None
        
        return None, None
    
    def get_any_input(self) -> Optional[str]:
        """任意の入力を取得（スタート画面等で使用）"""
        return self.input_handler.get_input()
    
    def get_start_input(self) -> tuple:
        """スタート画面用の入力処理（シンプル）"""
        key = self.input_handler.get_input()
        if key:
            # 終了コマンドかチェック
            if key in ['q', 'Q']:
                return None, 'quit'
            # その他のキーはゲーム開始
            else:
                return key, 'start'
        return None, None
    
    def clear_held_keys(self):
        """保持キー状態をクリア（簡略化されているため何もしない）"""
        pass


# 使用例とテスト用の関数
def test_input_handler():
    """入力ハンドラーのテスト"""
    print("Input Handler Test - Press keys (Q to quit):")
    
    controller = GameController()
    controller.start()
    
    try:
        while True:
            action, command = controller.get_action_or_command()
            if action:
                print(f"Action: {action}")
            
            if command:
                print(f"Command: {command}")
                if command == 'quit':
                    break
            
            time.sleep(0.01)
    
    finally:
        controller.stop()
        print("Input handler test completed.")


if __name__ == "__main__":
    test_input_handler()