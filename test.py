#!/usr/bin/env python3
"""
QoderTetris テストスクリプト
"""

import sys
import time
import traceback
from tetris.env import TetrisEnv
from tetris.core import Action, TetrisBoard
from tetris.renderer import CUIRenderer


def test_core_functionality():
    """コア機能のテスト"""
    print("=== コア機能テスト ===")
    
    try:
        # ボード作成テスト
        board = TetrisBoard()
        print("✓ TetrisBoardの作成: 成功")
        
        # ピース生成テスト
        board.spawn_piece()
        print("✓ ピース生成: 成功")
        
        # アクション実行テスト
        board.apply_action(Action.MOVE_LEFT)
        board.apply_action(Action.ROTATE)
        print("✓ アクション実行: 成功")
        
        # ステップ実行テスト
        board.step()
        print("✓ ステップ実行: 成功")
        
        print("コア機能テスト: 全て成功!\n")
        return True
        
    except Exception as e:
        print(f"✗ コア機能テスト失敗: {e}")
        traceback.print_exc()
        return False


def test_gymnasium_env():
    """Gymnasium環境のテスト"""
    print("=== Gymnasium環境テスト ===")
    
    try:
        # 環境作成テスト
        env = TetrisEnv()
        print("✓ TetrisEnv作成: 成功")
        
        # リセットテスト
        observation, info = env.reset()
        print("✓ 環境リセット: 成功")
        print(f"  観測空間タイプ: {type(observation)}")
        
        # ステップ実行テスト
        for action in [Action.MOVE_LEFT, Action.ROTATE, Action.SOFT_DROP]:
            obs, reward, terminated, truncated, info = env.step(action)
            print(f"✓ アクション {action}: reward={reward}, terminated={terminated}")
            
            if terminated:
                break
        
        # レンダリングテスト
        render_output = env.render()
        if render_output:
            print("✓ レンダリング: 成功")
        
        env.close()
        print("✓ 環境クローズ: 成功")
        
        print("Gymnasium環境テスト: 全て成功!\n")
        return True
        
    except Exception as e:
        print(f"✗ Gymnasium環境テスト失敗: {e}")
        traceback.print_exc()
        return False


def test_renderer():
    """レンダラーのテスト"""
    print("=== レンダラーテスト ===")
    
    try:
        renderer = CUIRenderer()
        board = TetrisBoard()
        board.spawn_piece()
        
        # 各種画面のテスト
        start_screen = renderer.render_start_screen()
        print("✓ スタート画面レンダリング: 成功")
        
        board_render = renderer.render_board(board)
        print("✓ ボード画面レンダリング: 成功")
        
        board.game_over = True
        game_over_screen = renderer.render_game_over(board)
        print("✓ ゲームオーバー画面レンダリング: 成功")
        
        print("レンダラーテスト: 全て成功!\n")
        return True
        
    except Exception as e:
        print(f"✗ レンダラーテスト失敗: {e}")
        traceback.print_exc()
        return False


def test_basic_gameplay():
    """基本ゲームプレイのテスト"""
    print("=== 基本ゲームプレイテスト ===")
    
    try:
        env = TetrisEnv()
        renderer = CUIRenderer()
        
        # ゲーム開始
        observation, info = env.reset()
        print("✓ ゲーム開始: 成功")
        
        # 数ステップ実行
        actions = [Action.MOVE_LEFT, Action.ROTATE, Action.MOVE_RIGHT, 
                  Action.SOFT_DROP, Action.SOFT_DROP, Action.HARD_DROP]
        
        for i, action in enumerate(actions):
            obs, reward, terminated, truncated, info = env.step(action)
            print(f"ステップ {i+1}: アクション={action}, 報酬={reward}")
            
            if terminated:
                print("ゲーム終了")
                break
        
        # 最終画面表示テスト
        final_render = renderer.render(env.board)
        print("✓ 最終画面レンダリング: 成功")
        
        env.close()
        print("基本ゲームプレイテスト: 成功!\n")
        return True
        
    except Exception as e:
        print(f"✗ 基本ゲームプレイテスト失敗: {e}")
        traceback.print_exc()
        return False


def show_demo_game():
    """デモゲーム表示"""
    print("=== デモゲーム表示 ===")
    
    try:
        env = TetrisEnv()
        renderer = CUIRenderer()
        renderer.initialize_display()
        
        observation, info = env.reset()
        
        # 簡単な自動プレイデモ
        actions = [Action.MOVE_LEFT, Action.ROTATE, Action.MOVE_RIGHT] * 5
        actions.extend([Action.SOFT_DROP] * 10)
        
        for action in actions:
            renderer.clear_screen()
            
            obs, reward, terminated, truncated, info = env.step(action)
            
            content = renderer.render(env.board)
            print(content)
            print(f"Action: {action}, Reward: {reward}")
            
            if terminated:
                print("ゲーム終了!")
                break
            
            time.sleep(0.3)  # 見やすくするために少し待機
        
        renderer.cleanup_display()
        env.close()
        
        print("\nデモゲーム表示: 完了!")
        return True
        
    except Exception as e:
        print(f"✗ デモゲーム表示失敗: {e}")
        traceback.print_exc()
        return False


def main():
    """メインテスト関数"""
    print("QoderTetris - テストスイート開始\n")
    
    test_results = []
    
    # 各テストを実行
    test_results.append(("コア機能", test_core_functionality()))
    test_results.append(("Gymnasium環境", test_gymnasium_env()))
    test_results.append(("レンダラー", test_renderer()))
    test_results.append(("基本ゲームプレイ", test_basic_gameplay()))
    
    # 結果サマリー
    print("=" * 50)
    print("テスト結果サマリー:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in test_results:
        status = "✓ 成功" if result else "✗ 失敗"
        print(f"{test_name:<20}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("全てのテストが成功しました!")
        print("\nデモゲームを表示しますか? (y/N): ", end="")
        
        try:
            response = input().strip().lower()
            if response in ['y', 'yes']:
                show_demo_game()
        except KeyboardInterrupt:
            print("\n中断されました。")
        
        print("\nゲームをプレイするには以下を実行してください:")
        print("python play.py")
        return 0
    else:
        print("一部のテストが失敗しました。コードを確認してください。")
        return 1


if __name__ == "__main__":
    sys.exit(main())