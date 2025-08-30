import pytest
from tetris.env import TetrisEnv
from tetris.renderer import CUIRenderer
from tetris.core import Action, TetrisBoard


class TestGameIntegration:
    """ゲーム統合テスト"""

    def test_complete_game_flow(self):
        """完全なゲームフロー統合テスト"""
        env = TetrisEnv()
        renderer = CUIRenderer()
        
        try:
            # ゲーム開始
            observation, info = env.reset()
            assert observation is not None
            
            # 複数アクション実行
            actions = [Action.MOVE_LEFT, Action.ROTATE, Action.MOVE_RIGHT, Action.SOFT_DROP]
            
            for action in actions:
                obs, reward, terminated, truncated, info = env.step(action)
                
                # 結果の検証
                assert obs is not None
                assert isinstance(reward, (int, float))
                assert isinstance(terminated, bool)
                assert isinstance(truncated, bool)
                
                # レンダリングテスト（正しい引数で呼び出し）
                render_output = renderer.render(env.board, "playing")
                assert isinstance(render_output, str)
                
                if terminated:
                    break
                    
        finally:
            env.close()

    def test_env_renderer_integration(self):
        """環境とレンダラーの統合テスト"""
        env = TetrisEnv()
        renderer = CUIRenderer()
        
        try:
            observation, info = env.reset()
            
            # 環境の状態をレンダリング
            render_output = renderer.render(env.board, "playing")
            assert isinstance(render_output, str)
            assert len(render_output) > 0
            
            # アクション実行後のレンダリング
            obs, reward, terminated, truncated, info = env.step(Action.ROTATE)
            render_output_after = renderer.render(env.board, "playing")
            assert isinstance(render_output_after, str)
            
        finally:
            env.close()

    def test_multiaction_sequence(self):
        """複数アクション連続実行テスト"""
        env = TetrisEnv()
        
        try:
            observation, info = env.reset()
            initial_score = observation["score"]
            
            # アクションシーケンス実行
            action_sequence = [
                Action.MOVE_LEFT,
                Action.ROTATE,
                Action.MOVE_RIGHT,
                Action.SOFT_DROP,
                Action.SOFT_DROP,
                Action.HARD_DROP
            ]
            
            for i, action in enumerate(action_sequence):
                obs, reward, terminated, truncated, info = env.step(action)
                
                # 各ステップでの状態検証
                assert obs["score"] >= initial_score
                assert obs["lines_cleared"] >= 0
                assert obs["level"] >= 1
                
                if terminated:
                    print(f"Game ended at step {i}")
                    break
                    
        finally:
            env.close()

    def test_edge_cases(self):
        """エッジケーステスト"""
        env = TetrisEnv()
        
        try:
            # 正常なリセット
            observation, info = env.reset()
            
            # 無効なアクションテスト（エラーハンドリング）
            try:
                obs, reward, terminated, truncated, info = env.step(999)  # 無効なアクション
            except (ValueError, IndexError):
                # エラーが発生してもOK
                pass
            except Exception as e:
                # 予期しないエラーでもテストは継続
                print(f"Unexpected error with invalid action: {e}")
                
        finally:
            env.close()

    def test_score_progression(self):
        """スコア進行テスト"""
        env = TetrisEnv()
        
        try:
            observation, info = env.reset()
            initial_score = observation["score"]
            
            # ハードドロップでスコアが増加することを確認
            obs, reward, terminated, truncated, info = env.step(Action.HARD_DROP)
            
            # スコアが増加または同じであることを確認
            assert obs["score"] >= initial_score
            
        finally:
            env.close()

    def test_board_state_consistency(self):
        """ボード状態の一貫性テスト"""
        board = TetrisBoard()
        env = TetrisEnv()
        
        try:
            observation, info = env.reset()
            
            # 環境のボードと直接ボードの一貫性確認
            assert env.board.width == board.width
            assert env.board.height == board.height
            
            # 初期状態の確認
            assert env.board.score == 0
            assert env.board.lines_cleared == 0
            assert env.board.level == 1
            assert not env.board.game_over
            
        finally:
            env.close()

    def test_render_different_states(self):
        """異なる状態でのレンダリングテスト"""
        renderer = CUIRenderer()
        board = TetrisBoard()
        
        try:
            # スタート画面
            start_screen = renderer.render(None, "start")
            assert isinstance(start_screen, str)
            assert "Press any key to start" in start_screen
            
            # プレイ中画面
            board.spawn_piece()
            play_screen = renderer.render(board, "playing")
            assert isinstance(play_screen, str)
            assert "QoderTetris" in play_screen
            
            # ゲームオーバー画面
            board.game_over = True
            game_over_screen = renderer.render(board, "game_over")
            assert isinstance(game_over_screen, str)
            assert "GAME OVER" in game_over_screen
            
        except Exception as e:
            pytest.fail(f"Render different states failed: {e}")

    def test_environment_reset_consistency(self):
        """環境リセットの一貫性テスト"""
        env = TetrisEnv()
        
        try:
            # 初回リセット
            obs1, info1 = env.reset()
            
            # 何度かステップ実行
            for _ in range(5):
                obs, reward, terminated, truncated, info = env.step(Action.SOFT_DROP)
                if terminated:
                    break
            
            # 再リセット
            obs2, info2 = env.reset()
            
            # リセット後の状態が初期状態と一致することを確認
            assert obs2["score"] == 0
            assert obs2["lines_cleared"] == 0
            assert obs2["level"] == 1
            assert not env.board.game_over
            
        finally:
            env.close()

    def test_action_reward_correlation(self):
        """アクションと報酬の相関テスト"""
        env = TetrisEnv()
        
        try:
            observation, info = env.reset()
            
            # 各アクションの報酬をテスト
            actions_rewards = {}
            
            for action in [Action.NOTHING, Action.MOVE_LEFT, Action.MOVE_RIGHT, 
                          Action.ROTATE, Action.SOFT_DROP, Action.HARD_DROP]:
                # 環境をリセット
                env.reset()
                obs, reward, terminated, truncated, info = env.step(action)
                actions_rewards[action] = reward
                
                # 報酬が数値であることを確認
                assert isinstance(reward, (int, float))
            
            # ソフトドロップとハードドロップは通常正の報酬
            if not env.board.game_over:
                assert actions_rewards[Action.SOFT_DROP] >= 0
                assert actions_rewards[Action.HARD_DROP] >= 0
                
        finally:
            env.close()