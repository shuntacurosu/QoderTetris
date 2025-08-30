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
                
                # レンダリングテスト
                render_output = renderer.render(env.board)
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
            render_output = renderer.render(env.board)
            assert isinstance(render_output, str)
            assert len(render_output) > 0
            
            # アクション実行後のレンダリング
            obs, reward, terminated, truncated, info = env.step(Action.ROTATE)
            render_output_after = renderer.render(env.board)
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
            # リセットなしでstep実行（エラーハンドリングテスト）
            try:
                obs, reward, terminated, truncated, info = env.step(Action.NOTHING)
                # エラーが発生しなければ継続
            except Exception:
                # エラーが発生してもOK
                pass
            
            # 正常なリセット
            observation, info = env.reset()
            
            # 無効なアクションテスト（エラーハンドリング）
            try:
                obs, reward, terminated, truncated, info = env.step(999)  # 無効なアクション
            except Exception:
                # エラーが発生してもOK
                pass
                
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