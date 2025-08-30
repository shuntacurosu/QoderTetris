import pytest
import numpy as np
from gymnasium import spaces
from tetris.env import TetrisEnv
from tetris.core import Action


class TestTetrisEnv:
    """TetrisEnvクラスのテスト"""

    def test_env_initialization(self, tetris_env):
        """環境初期化テスト"""
        assert tetris_env.action_space == spaces.Discrete(6)
        assert isinstance(tetris_env.observation_space, spaces.Dict)
        assert tetris_env.board is not None

    def test_reset_functionality(self, tetris_env):
        """リセット機能テスト"""
        observation, info = tetris_env.reset()
        
        # 観測の構造確認
        assert isinstance(observation, dict)
        assert "board" in observation
        assert "current_piece_type" in observation
        assert "current_piece_x" in observation
        assert "current_piece_y" in observation
        assert "current_piece_rotation" in observation
        assert "next_piece_type" in observation
        assert "score" in observation
        assert "lines_cleared" in observation
        assert "level" in observation
        
        # 情報辞書の確認
        assert isinstance(info, dict)
        
        # ボード状態の確認
        assert isinstance(observation["board"], np.ndarray)
        assert observation["board"].shape == (20, 10)
        assert observation["score"] == 0
        assert observation["lines_cleared"] == 0
        assert observation["level"] == 1

    def test_step_execution(self, tetris_env):
        """ステップ実行テスト"""
        observation, info = tetris_env.reset()
        
        # 各アクションをテスト
        for action in [Action.MOVE_LEFT, Action.MOVE_RIGHT, Action.ROTATE, Action.SOFT_DROP]:
            obs, reward, terminated, truncated, info = tetris_env.step(action)
            
            # 戻り値の型確認
            assert isinstance(obs, dict)
            assert isinstance(reward, (int, float))
            assert isinstance(terminated, bool)
            assert isinstance(truncated, bool)
            assert isinstance(info, dict)
            
            # 観測の構造確認
            assert "board" in obs
            assert "current_piece_type" in obs
            assert "next_piece_type" in obs
            
            if terminated:
                break

    def test_action_space(self, tetris_env):
        """行動空間テスト"""
        action_space = tetris_env.action_space
        assert isinstance(action_space, spaces.Discrete)
        assert action_space.n == 6
        
        # 全アクションが有効であることを確認
        for action in range(6):
            assert action_space.contains(action)
        
        # 無効なアクションの確認
        assert not action_space.contains(-1)
        assert not action_space.contains(6)

    def test_observation_space(self, tetris_env):
        """観測空間テスト"""
        obs_space = tetris_env.observation_space
        assert isinstance(obs_space, spaces.Dict)
        
        # 期待されるキーの存在確認
        expected_keys = ["board", "current_piece_type", "current_piece_x", "current_piece_y", 
                        "current_piece_rotation", "next_piece_type", "score", "lines_cleared", "level"]
        for key in expected_keys:
            assert key in obs_space.spaces
        
        # ボード空間の確認
        board_space = obs_space.spaces["board"]
        assert isinstance(board_space, spaces.Box)
        assert board_space.shape == (20, 10)

    def test_reward_calculation(self, tetris_env):
        """報酬計算テスト"""
        observation, info = tetris_env.reset()
        
        # 通常のアクション
        obs, reward, terminated, truncated, info = tetris_env.step(Action.MOVE_LEFT)
        assert isinstance(reward, (int, float))
        
        # ソフトドロップ（正の報酬期待）
        obs, reward, terminated, truncated, info = tetris_env.step(Action.SOFT_DROP)
        assert isinstance(reward, (int, float))

    def test_termination_conditions(self, tetris_env):
        """終了条件テスト"""
        observation, info = tetris_env.reset()
        
        # 通常の状態では終了しない
        obs, reward, terminated, truncated, info = tetris_env.step(Action.NOTHING)
        assert not terminated
        assert not truncated

    def test_render_functionality(self, tetris_env):
        """レンダリング機能テスト"""
        tetris_env.reset()
        
        # レンダリングが例外を発生させないことを確認
        try:
            render_output = tetris_env.render()
            # レンダリング出力がNoneまたは文字列であることを確認
            assert render_output is None or isinstance(render_output, str)
        except Exception as e:
            pytest.fail(f"Rendering failed with exception: {e}")

    def test_close_functionality(self, tetris_env):
        """クローズ機能テスト"""
        # クローズが例外を発生させないことを確認
        try:
            tetris_env.close()
        except Exception as e:
            pytest.fail(f"Close failed with exception: {e}")

    def test_seed_functionality(self, tetris_env):
        """シード機能テスト"""
        # シード設定
        observation1, info1 = tetris_env.reset(seed=42)
        
        # 同じシードで再実行
        observation2, info2 = tetris_env.reset(seed=42)
        
        # 初期状態が同じであることを確認
        assert observation1["score"] == observation2["score"]
        assert observation1["lines_cleared"] == observation2["lines_cleared"]
        assert observation1["level"] == observation2["level"]

    def test_hard_drop_action(self, tetris_env):
        """ハードドロップアクションテスト"""
        observation, info = tetris_env.reset()
        initial_score = observation["score"]
        
        # ハードドロップ実行
        obs, reward, terminated, truncated, info = tetris_env.step(Action.HARD_DROP)
        
        # ハードドロップ後の状態確認
        assert obs["score"] >= initial_score  # スコアが増加または同じ
        assert isinstance(reward, (int, float))  # 報酬が数値

    def test_multiple_steps_consistency(self, tetris_env):
        """複数ステップの一貫性テスト"""
        observation, info = tetris_env.reset()
        
        steps = 10
        for i in range(steps):
            action = i % 6  # 0-5のアクションを循環
            obs, reward, terminated, truncated, info = tetris_env.step(action)
            
            # 観測の一貫性確認
            assert isinstance(obs["board"], np.ndarray)
            assert obs["board"].shape == (20, 10)
            assert obs["score"] >= 0
            assert obs["lines_cleared"] >= 0
            assert obs["level"] >= 1
            
            if terminated:
                break

    def test_observation_bounds(self, tetris_env):
        """観測値の範囲テスト"""
        observation, info = tetris_env.reset()
        
        # ボードの値が0-7の範囲内であることを確認
        board = observation["board"]
        assert np.all(board >= 0)
        assert np.all(board <= 7)
        
        # スコア・レベル・ライン数の妥当性確認
        assert observation["score"] >= 0
        assert observation["lines_cleared"] >= 0
        assert observation["level"] >= 1

    def test_action_conversion(self, tetris_env):
        """アクション変換テスト"""
        tetris_env.reset()
        
        # int型のアクション
        obs, reward, terminated, truncated, info = tetris_env.step(1)  # MOVE_LEFT
        assert isinstance(obs, dict)
        
        # Action型のアクション
        obs, reward, terminated, truncated, info = tetris_env.step(Action.MOVE_RIGHT)
        assert isinstance(obs, dict)

    def test_fall_speed_update(self, tetris_env):
        """落下速度更新テスト"""
        tetris_env.reset()
        initial_fall_speed = tetris_env.fall_speed
        
        # レベルが変わるまで何度かステップ実行
        for _ in range(20):  # 十分な回数実行
            obs, reward, terminated, truncated, info = tetris_env.step(Action.SOFT_DROP)
            if terminated:
                break
        
        # 落下速度が初期値以下であることを確認（レベル上昇で速くなる）
        assert tetris_env.fall_speed <= initial_fall_speed

    def test_info_content(self, tetris_env):
        """情報辞書の内容テスト"""
        observation, info = tetris_env.reset()
        
        # 期待されるキーの確認
        assert "step_count" in info
        assert "fall_speed" in info
        assert "board_with_piece" in info
        
        # 値の型確認
        assert isinstance(info["step_count"], int)
        assert isinstance(info["fall_speed"], int)
        assert isinstance(info["board_with_piece"], np.ndarray)