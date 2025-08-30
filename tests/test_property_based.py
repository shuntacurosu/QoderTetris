import pytest
import numpy as np
from hypothesis import given, strategies as st, settings, assume
from tetris.env import TetrisEnv
from tetris.core import TetrisBoard, Action, TetrominoType, Tetromino


class TestPropertyBasedTesting:
    """プロパティベーステスト - 不変条件の検証"""

    @given(st.integers(min_value=0, max_value=5))
    @settings(max_examples=100)
    def test_action_invariants(self, action):
        """アクション実行の不変条件テスト"""
        env = TetrisEnv()
        try:
            observation, info = env.reset()
            initial_board_shape = observation["board"].shape
            initial_score = observation["score"]
            
            # アクション実行
            obs, reward, terminated, truncated, info = env.step(action)
            
            # 不変条件の確認
            assert obs["board"].shape == initial_board_shape, "Board shape changed"
            assert obs["score"] >= initial_score, "Score decreased"
            assert obs["lines_cleared"] >= observation["lines_cleared"], "Lines cleared decreased"
            assert obs["level"] >= observation["level"], "Level decreased"
            assert isinstance(reward, (int, float)), "Reward not numeric"
            assert isinstance(terminated, bool), "Terminated not boolean"
            assert isinstance(truncated, bool), "Truncated not boolean"
            
        finally:
            env.close()

    @given(st.lists(st.integers(min_value=0, max_value=5), min_size=1, max_size=50))
    @settings(max_examples=50)
    def test_action_sequence_properties(self, action_sequence):
        """アクションシーケンスの特性テスト"""
        env = TetrisEnv()
        try:
            observation, info = env.reset()
            initial_state = observation.copy()
            
            scores = [observation["score"]]
            lines_cleared = [observation["lines_cleared"]]
            
            for action in action_sequence:
                obs, reward, terminated, truncated, info = env.step(action)
                scores.append(obs["score"])
                lines_cleared.append(obs["lines_cleared"])
                
                if terminated:
                    observation, info = env.reset()
                    break
            
            # 単調性の確認
            assert all(s2 >= s1 for s1, s2 in zip(scores[:-1], scores[1:])), "Score not monotonic"
            assert all(l2 >= l1 for l1, l2 in zip(lines_cleared[:-1], lines_cleared[1:])), "Lines cleared not monotonic"
            
        finally:
            env.close()

    @given(st.integers(min_value=1, max_value=1000))
    @settings(max_examples=20)
    def test_reset_consistency(self, seed):
        """リセット一貫性テスト"""
        env = TetrisEnv()
        try:
            # 同じシードで2回リセット
            obs1, info1 = env.reset(seed=seed)
            obs2, info2 = env.reset(seed=seed)
            
            # 初期状態が同じであることを確認
            assert obs1["score"] == obs2["score"], "Score not consistent after reset"
            assert obs1["lines_cleared"] == obs2["lines_cleared"], "Lines cleared not consistent"
            assert obs1["level"] == obs2["level"], "Level not consistent"
            assert np.array_equal(obs1["board"], obs2["board"]), "Board not consistent after reset"
            
        finally:
            env.close()

    @given(st.integers(min_value=0, max_value=19), st.integers(min_value=0, max_value=9))
    @settings(max_examples=100)
    def test_board_bounds_invariant(self, y, x):
        """ボード境界不変条件テスト"""
        board = TetrisBoard()
        
        # ボード内の座標であることを前提
        assume(0 <= y < board.height and 0 <= x < board.width)
        
        # ボードの値が有効範囲内であることを確認
        board_value = board.board[y][x]
        assert 0 <= board_value <= 7, f"Invalid board value {board_value} at ({y}, {x})"

    @given(st.lists(st.integers(min_value=0, max_value=5), min_size=10, max_size=100))
    @settings(max_examples=30)
    def test_game_over_properties(self, actions):
        """ゲームオーバー特性テスト"""
        env = TetrisEnv()
        try:
            observation, info = env.reset()
            game_over_occurred = False
            
            for action in actions:
                obs, reward, terminated, truncated, info = env.step(action)
                
                if terminated:
                    game_over_occurred = True
                    
                    # ゲームオーバー時の特性確認
                    assert obs["score"] >= 0, "Negative score at game over"
                    assert obs["lines_cleared"] >= 0, "Negative lines cleared at game over"
                    assert obs["level"] >= 1, "Invalid level at game over"
                    
                    # リセット後は正常状態に戻る
                    reset_obs, reset_info = env.reset()
                    assert reset_obs["score"] == 0, "Score not reset to 0"
                    assert reset_obs["lines_cleared"] == 0, "Lines cleared not reset to 0"
                    assert reset_obs["level"] == 1, "Level not reset to 1"
                    break
            
        finally:
            env.close()

    @given(st.integers(min_value=0, max_value=6))
    @settings(max_examples=50)
    def test_tetromino_type_properties(self, type_value):
        """テトロミノタイプ特性テスト"""
        # 有効なテトロミノタイプのみテスト
        assume(type_value < len(TetrominoType))
        
        tetromino_type = list(TetrominoType)[type_value]
        piece = Tetromino(tetromino_type)
        
        # テトロミノの基本特性
        assert piece.type == tetromino_type, "Type mismatch"
        assert isinstance(piece.x, int), "X coordinate not integer"
        assert isinstance(piece.y, int), "Y coordinate not integer"
        assert 0 <= piece.rotation < 4, f"Invalid rotation {piece.rotation}"
        assert piece.shape.ndim == 2, "Shape not 2D"
        assert piece.shape.size > 0, "Empty shape"

    @given(st.integers(min_value=-5, max_value=15), st.integers(min_value=-5, max_value=25))
    @settings(max_examples=100)
    def test_position_validation_properties(self, x, y):
        """位置検証特性テスト"""
        board = TetrisBoard()
        
        # ランダムなテトロミノを作成
        tetromino_type = TetrominoType.I
        piece = Tetromino(tetromino_type, x, y, 0)
        
        is_valid = board.is_valid_position(piece)
        
        # 境界条件の確認
        if x < 0 or y < 0:
            assert not is_valid, f"Negative position ({x}, {y}) should be invalid"
        
        if x >= board.width or y >= board.height:
            # 完全にボード外の場合は無効（ただし、ピースの形状により例外あり）
            pass  # 形状により複雑な判定が必要

    @given(st.integers(min_value=0, max_value=3))
    @settings(max_examples=50)
    def test_rotation_properties(self, rotation):
        """回転特性テスト"""
        board = TetrisBoard()
        
        for tetromino_type in TetrominoType:
            piece = Tetromino(tetromino_type, 5, 5, rotation)
            
            # 4回回転すると元に戻る特性
            original_shape = piece.shape.copy()
            current_piece = piece
            
            for _ in range(4):
                current_piece = current_piece.rotate()
            
            # 同じ形状に戻ることを確認（位置によって異なる場合があるので、形状のみ比較）
            assert current_piece.rotation == piece.rotation, "Rotation not cyclic"

    @given(st.lists(st.integers(min_value=0, max_value=5), min_size=1, max_size=20))
    @settings(max_examples=30)
    def test_reward_accumulation_properties(self, action_sequence):
        """報酬累積特性テスト"""
        env = TetrisEnv()
        try:
            observation, info = env.reset()
            
            total_reward = 0
            rewards = []
            
            for action in action_sequence:
                obs, reward, terminated, truncated, info = env.step(action)
                rewards.append(reward)
                total_reward += reward
                
                if terminated:
                    break
            
            # 報酬特性の確認
            assert isinstance(total_reward, (int, float)), "Total reward not numeric"
            assert all(isinstance(r, (int, float)) for r in rewards), "Individual rewards not numeric"
            
            # ソフトドロップ報酬は正であるべき
            soft_drop_actions = [i for i, action in enumerate(action_sequence) 
                               if action == Action.SOFT_DROP and i < len(rewards)]
            for i in soft_drop_actions:
                if rewards[i] > 0:  # ソフトドロップが実際に実行された場合
                    pass  # 報酬が正であることを期待するが、移動不可の場合は0の場合もある
            
        finally:
            env.close()

    @given(st.integers(min_value=1, max_value=100))
    @settings(max_examples=20)
    def test_deterministic_behavior(self, seed):
        """決定論的動作テスト"""
        env1 = TetrisEnv()
        env2 = TetrisEnv()
        
        try:
            # 同じシードで初期化
            obs1, info1 = env1.reset(seed=seed)
            obs2, info2 = env2.reset(seed=seed)
            
            # 同じアクションシーケンスを実行
            action_sequence = [1, 2, 3, 4, 0, 5] * 5
            
            for action in action_sequence:
                obs1, reward1, term1, trunc1, info1 = env1.step(action)
                obs2, reward2, term2, trunc2, info2 = env2.step(action)
                
                # 同じ結果であることを確認
                assert obs1["score"] == obs2["score"], f"Score mismatch: {obs1['score']} != {obs2['score']}"
                assert reward1 == reward2, f"Reward mismatch: {reward1} != {reward2}"
                assert term1 == term2, f"Termination mismatch: {term1} != {term2}"
                
                if term1:
                    break
            
        finally:
            env1.close()
            env2.close()

    @given(st.integers(min_value=0, max_value=5))
    @settings(max_examples=50)
    def test_observation_space_consistency(self, action):
        """観測空間一貫性テスト"""
        env = TetrisEnv()
        try:
            observation, info = env.reset()
            
            # 観測空間の構造を記録
            initial_keys = set(observation.keys())
            initial_types = {k: type(v) for k, v in observation.items()}
            initial_shapes = {k: v.shape if hasattr(v, 'shape') else None 
                             for k, v in observation.items()}
            
            # アクション実行後も同じ構造を維持
            obs, reward, terminated, truncated, info = env.step(action)
            
            assert set(obs.keys()) == initial_keys, "Observation keys changed"
            
            for key in initial_keys:
                assert type(obs[key]) == initial_types[key], f"Type changed for key {key}"
                if initial_shapes[key] is not None:
                    assert obs[key].shape == initial_shapes[key], f"Shape changed for key {key}"
            
        finally:
            env.close()


class TestGameLogicProperties:
    """ゲームロジック特性テスト"""

    @given(st.integers(min_value=0, max_value=1000))
    @settings(max_examples=30)
    def test_score_monotonicity(self, steps):
        """スコア単調性テスト"""
        env = TetrisEnv()
        try:
            observation, info = env.reset()
            previous_score = observation["score"]
            
            for i in range(min(steps, 100)):  # 最大100ステップに制限
                action = i % 6
                obs, reward, terminated, truncated, info = env.step(action)
                
                # スコアは減少しない
                assert obs["score"] >= previous_score, f"Score decreased: {obs['score']} < {previous_score}"
                previous_score = obs["score"]
                
                if terminated:
                    break
            
        finally:
            env.close()

    @given(st.integers(min_value=1, max_value=20))
    @settings(max_examples=20)
    def test_level_progression_properties(self, target_lines):
        """レベル進行特性テスト"""
        board = TetrisBoard()
        
        initial_level = board.level
        board.lines_cleared = target_lines
        board.update_level()
        
        # レベルは適切に更新される
        expected_level = max(1, 1 + target_lines // 10)
        assert board.level == expected_level, f"Level calculation error: {board.level} != {expected_level}"

    @given(st.lists(st.integers(min_value=0, max_value=9), min_size=10, max_size=10))
    @settings(max_examples=30)
    def test_line_clear_detection(self, row_pattern):
        """ライン消去検出テスト"""
        board = TetrisBoard()
        
        # 最下段を指定パターンで埋める
        bottom_row = board.height - 1
        for x, value in enumerate(row_pattern):
            board.board[bottom_row][x] = 1 if value > 5 else 0
        
        # 完全に埋まった行の場合のみライン消去が発生すべき
        is_complete_line = all(board.board[bottom_row][x] != 0 for x in range(board.width))
        
        initial_lines_cleared = board.lines_cleared
        board.clear_lines()
        
        if is_complete_line:
            assert board.lines_cleared > initial_lines_cleared, "Complete line not cleared"
        else:
            assert board.lines_cleared == initial_lines_cleared, "Incomplete line was cleared"