#!/usr/bin/env python3
"""
QoderTetris - メインプレイスクリプト

Gymnasium準拠のテトリス環境で人間がプレイできるインターフェース
"""

import sys
import time
import signal
from typing import Optional

from tetris.env import TetrisEnv
from tetris.renderer import CUIRenderer
from tetris.input_handler import GameController
from tetris.core import Action


class TetrisGame:
    """テトリスゲームのメインクラス"""
    
    def __init__(self):
        self.env = TetrisEnv(render_mode="human")
        self.renderer = CUIRenderer(use_color=True)
        self.controller = GameController()
        self.running = False
        self.game_state = "start"  # "start", "playing", "game_over", "paused"
        
        # シグナルハンドラー設定（Ctrl+C対応）
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """シグナル処理（Ctrl+C等）"""
        print("\n\nゲームを終了しています...")
        self.quit_game()
        sys.exit(0)
    
    def start_game(self):
        """ゲーム開始"""
        try:
            self.renderer.initialize_display()
            self.controller.start()
            self.running = True
            
            # スタート画面表示
            self._show_start_screen()
            
            # メインゲームループ
            self._main_loop()
            
        except KeyboardInterrupt:
            print("\n\nゲームが中断されました。")
        except Exception as e:
            print(f"\nエラーが発生しました: {e}")
        finally:
            self.quit_game()
    
    def _show_start_screen(self):
        """スタート画面表示"""
        self.game_state = "start"
        
        while self.running and self.game_state == "start":
            # スタート画面描画
            content = self.renderer.render(game_state="start")
            self.renderer.update_display(content)
            
            # キー入力待機（シンプル化）
            key, action_type = self.controller.get_start_input()
            
            if action_type == 'quit':
                self.running = False
                return
            elif action_type == 'start':
                # ゲーム開始
                self.game_state = "playing"
                self._start_new_game()
            
            time.sleep(0.01)
    
    def _start_new_game(self):
        """新しいゲーム開始"""
        # 環境リセット
        observation, info = self.env.reset()
        self.controller.clear_held_keys()
        print("新しいゲームを開始しました！")
    
    def _main_loop(self):
        """メインゲームループ"""
        last_fall_time = time.time()
        
        while self.running:
            current_time = time.time()
            
            if self.game_state == "start":
                self._show_start_screen()
                continue
            
            elif self.game_state == "playing":
                # プレイ中の処理
                self._handle_playing_state(current_time, last_fall_time)
                
            elif self.game_state == "game_over":
                # ゲームオーバー処理
                self._handle_game_over_state()
            
            # フレーム制御
            time.sleep(0.016)  # 約60FPS
    
    def _handle_playing_state(self, current_time: float, last_fall_time: float):
        """プレイ中の状態処理"""
        action_performed = False
        
        # アクションとコマンドを統一して処理
        action, command = self.controller.get_action_or_command()
        
        # 制御コマンド処理
        if command == 'quit':
            self.running = False
            return
        elif command == 'restart':
            self._start_new_game()
            return
        
        # アクション処理
        if action is not None:
            observation, reward, terminated, truncated, info = self.env.step(action)
            action_performed = True
            
            if terminated:
                self.game_state = "game_over"
                return
        
        # 定期的な自然落下（アクションが実行されなかった場合）
        if not action_performed:
            # 何もアクションがない場合のステップ
            observation, reward, terminated, truncated, info = self.env.step(Action.NOTHING)
            
            if terminated:
                self.game_state = "game_over"
                return
        
        # 画面更新
        self._update_display()
    
    def _handle_game_over_state(self):
        """ゲームオーバー状態処理"""
        # ゲームオーバー画面描画
        content = self.renderer.render(self.env.board, game_state="game_over")
        self.renderer.update_display(content)
        
        # 入力待機
        action, command = self.controller.get_action_or_command()
        any_key = self.controller.get_any_input()
        
        if command == 'quit' or any_key in ['q', 'Q']:
            self.running = False
        elif command == 'restart' or any_key in ['r', 'R']:
            self.game_state = "playing"
            self._start_new_game()
        
        time.sleep(0.01)
    
    def _update_display(self):
        """画面更新"""
        content = self.renderer.render(self.env.board, game_state=self.game_state)
        self.renderer.update_display(content)
    
    def quit_game(self):
        """ゲーム終了処理"""
        if hasattr(self, 'controller'):
            self.controller.stop()
        
        if hasattr(self, 'renderer'):
            self.renderer.cleanup_display()
        
        if hasattr(self, 'env'):
            self.env.close()
        
        self.running = False


def main():
    """メイン関数"""
    print("QoderTetris - Gymnasium準拠テトリス環境")
    print("準備中...")
    
    try:
        game = TetrisGame()
        game.start_game()
    except Exception as e:
        print(f"ゲームの初期化に失敗しました: {e}")
        return 1
    
    print("ゲームを終了しました。ありがとうございました！")
    return 0


if __name__ == "__main__":
    sys.exit(main())