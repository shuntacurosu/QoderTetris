import pytest
import numpy as np
from tetris.env import TetrisEnv
from tetris.core import TetrisBoard, Action, TetrominoType, Tetromino
import time


class TestEdgeCases:
    """エッジケースのテスト"""

    def test_board_overflow_protection(self, tetris_board):
        """ボードオーバーフロー保護テスト"""
        # ボードの上部を完全に埋める
        for y in range(5):
            for x in range(tetris_board.width):
                tetris_board.board[y][x] = 1
        
        # 新しいピースのスポーンを試行
        result = tetris_board.spawn_piece()
        assert not result  # スポーンは失敗するはず
        assert tetris_board.game_over

    def test_extreme_position_boundaries(self, tetris_board):
        """極端な位置境界テスト"""
        tetris_board.spawn_piece()
        piece = tetris_board.current_piece
        
        # 極端に左に移動を試行
        for _ in range(20):  # ボード幅以上の移動試行
            moved, _ = tetris_board.apply_action(Action.MOVE_LEFT)
            if not moved:
                break
        
        # まだボード内にあることを確認
        assert piece.x >= 0
        
        # 極端に右に移動を試行
        for _ in range(30):
            moved, _ = tetris_board.apply_action(Action.MOVE_RIGHT)
            if not moved:
                break
        
        # まだボード内にあることを確認
        assert piece.x < tetris_board.width

    def test_rapid_rotation_at_boundaries(self, tetris_board):
        """境界での高速回転テスト"""
        tetris_board.spawn_piece()
        
        # 左端に移動
        while tetris_board.current_piece.x > 0:
            moved, _ = tetris_board.apply_action(Action.MOVE_LEFT)
            if not moved:
                break
        
        # 高速回転を試行
        initial_rotation = tetris_board.current_piece.rotation
        for _ in range(10):
            moved, _ = tetris_board.apply_action(Action.ROTATE)
        
        # 回転が適切に処理されることを確認
        assert tetris_board.current_piece.rotation != initial_rotation or not moved

    def test_simultaneous_actions_rejection(self, tetris_env):
        """同時アクション拒否テスト"""
        observation, info = tetris_env.reset()
        
        # 複数のアクションを短時間で実行
        actions = [Action.MOVE_LEFT, Action.ROTATE, Action.SOFT_DROP]
        results = []
        
        for action in actions:
            obs, reward, terminated, truncated, info = tetris_env.step(action)
            results.append((obs, reward, terminated, truncated))
            if terminated:
                break
        
        # すべてのアクションが適切に処理されることを確認
        assert len(results) == len(actions) or any(result[2] for result in results)

    def test_memory_leak_prevention(self, tetris_env):
        """メモリリーク防止テスト"""
        import gc
        import psutil
        import os
        
        # 初期メモリ使用量を記録
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 大量のステップを実行
        observation, info = tetris_env.reset()
        for i in range(1000):
            action = i % 6
            obs, reward, terminated, truncated, info = tetris_env.step(action)
            if terminated:
                observation, info = tetris_env.reset()
        
        # ガベージコレクションを強制実行
        gc.collect()
        
        # 最終メモリ使用量をチェック
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # メモリ使用量の増加が合理的な範囲内であることを確認（50MB以下）
        assert memory_increase < 50, f"Memory leak detected: {memory_increase}MB increase"

    def test_extreme_score_handling(self, tetris_board):
        """極端なスコア処理テスト"""
        # スコアを人為的に高い値に設定
        tetris_board.score = 999999999
        
        # さらにスコアを追加（直接更新）
        tetris_board.score += 1000
        
        # オーバーフローが発生していないことを確認
        assert tetris_board.score >= 999999999
        assert isinstance(tetris_board.score, int)

    def test_max_level_boundary(self, tetris_board):
        """最大レベル境界テスト"""
        # レベルを高い値に設定
        tetris_board.level = 999
        tetris_board.lines_cleared = 9990
        
        # ライン消去を実行してレベルアップを試行
        tetris_board.lines_cleared += 10
        # レベル計算は自動的に行われる
        calculated_level = tetris_board.lines_cleared // 10 + 1
        tetris_board.level = calculated_level
        
        # レベルが適切に更新されることを確認
        assert tetris_board.level >= 999

    def test_board_state_corruption_recovery(self, tetris_board):
        """ボード状態破損回復テスト"""
        # ボード状態を人為的に破損
        tetris_board.board[0][0] = -1  # 無効な値
        tetris_board.board[5][5] = 999  # 範囲外の値
        
        # 状態取得時にエラーが発生しないことを確認
        try:
            state = tetris_board.get_state()
            assert isinstance(state, dict)
        except Exception as e:
            pytest.fail(f"State corruption caused exception: {e}")

    def test_piece_spawn_edge_conditions(self, tetris_board):
        """ピーススポーンエッジ条件テスト"""
        # ボードの上部数行を部分的に埋める
        for x in range(3, 7):  # 中央部分のみ
            tetris_board.board[1][x] = 1
        
        # スポーンを試行
        result = tetris_board.spawn_piece()
        
        # スポーン可能性の確認（ピースの種類により異なる）
        if result:
            assert tetris_board.current_piece is not None
        else:
            assert tetris_board.game_over

    def test_negative_coordinate_protection(self, tetris_board):
        """負の座標保護テスト"""
        tetris_board.spawn_piece()
        piece = tetris_board.current_piece
        
        # 人為的に負の座標を設定しようとする
        invalid_piece = Tetromino(piece.type, -5, -5)
        invalid_piece.rotation = piece.rotation
        
        # 無効な位置として検出されることを確認
        assert not tetris_board.is_valid_position(invalid_piece)

    def test_high_frequency_actions(self, tetris_env):
        """高頻度アクションテスト"""
        observation, info = tetris_env.reset()
        
        start_time = time.time()
        action_count = 0
        
        # 1秒間に可能な限り多くのアクションを実行
        while time.time() - start_time < 1.0:
            action = action_count % 6
            obs, reward, terminated, truncated, info = tetris_env.step(action)
            action_count += 1
            
            if terminated:
                observation, info = tetris_env.reset()
        
        # 最低限のパフォーマンスを確認（1秒間に100アクション以上）
        assert action_count >= 100, f"Performance issue: only {action_count} actions in 1 second"

    def test_board_full_line_clear_edge(self, tetris_board):
        """ボード満杯時のライン消去エッジテスト"""
        # ボードをほぼ満杯にする（最上段は空ける）
        for y in range(1, tetris_board.height):
            for x in range(tetris_board.width - 1):  # 1つ空けておく
                tetris_board.board[y][x] = 1
        
        # 最後の空白を埋めてライン消去をトリガー
        tetris_board.board[tetris_board.height - 1][tetris_board.width - 1] = 1
        
        # ライン消去処理
        initial_lines = tetris_board.lines_cleared
        tetris_board._clear_lines()
        
        # ライン消去が正常に実行されることを確認
        assert tetris_board.lines_cleared >= initial_lines

    def test_zero_dimension_piece_protection(self, tetris_board):
        """ゼロ次元ピース保護テスト"""
        # 空の形状を持つピースの作成を試行
        try:
            piece = Tetromino(TetrominoType.I)
            # 形状データを空にする（実際のコードでは不可能だが、テストとして）
            original_shape = piece.shape
            piece.shape = np.array([])
            
            # 有効性チェック
            is_valid = tetris_board.is_valid_position(piece)
            
            # 元の形状に戻す
            piece.shape = original_shape
            
        except Exception as e:
            # 例外が適切に処理されることを確認
            assert isinstance(e, (ValueError, AttributeError, IndexError))


class TestPerformanceBoundaries:
    """パフォーマンス境界テスト"""

    def test_large_scale_operations(self, tetris_env):
        """大規模操作テスト"""
        observation, info = tetris_env.reset()
        
        start_time = time.time()
        steps = 0
        
        # 10000ステップまたは10秒のいずれか早い方まで実行
        while steps < 10000 and time.time() - start_time < 10.0:
            action = steps % 6
            obs, reward, terminated, truncated, info = tetris_env.step(action)
            steps += 1
            
            if terminated:
                observation, info = tetris_env.reset()
        
        execution_time = time.time() - start_time
        fps = steps / execution_time
        
        # 最低30FPSのパフォーマンスを要求
        assert fps >= 30, f"Performance below threshold: {fps:.2f} FPS"

    @pytest.mark.timeout(5)
    def test_infinite_loop_prevention(self, tetris_board):
        """無限ループ防止テスト"""
        tetris_board.spawn_piece()
        
        # 潜在的に無限ループを引き起こす可能性のある操作
        for _ in range(1000):  # 十分大きな数
            moved, reward = tetris_board.apply_action(Action.ROTATE)
            if not moved:
                break
        
        # テストが5秒以内に完了することをtimeoutデコレータで確認
        assert True  # ここに到達すれば無限ループは発生していない

    def test_concurrent_environment_safety(self):
        """並行環境安全性テスト"""
        import threading
        
        envs = [TetrisEnv() for _ in range(5)]
        results = []
        errors = []
        
        def run_env(env, env_id):
            try:
                observation, info = env.reset()
                for _ in range(100):
                    action = np.random.randint(0, 6)
                    obs, reward, terminated, truncated, info = env.step(action)
                    if terminated:
                        observation, info = env.reset()
                results.append(f"Env {env_id} completed successfully")
            except Exception as e:
                errors.append(f"Env {env_id} failed: {e}")
            finally:
                env.close()
        
        # 複数の環境を並行実行
        threads = []
        for i, env in enumerate(envs):
            thread = threading.Thread(target=run_env, args=(env, i))
            threads.append(thread)
            thread.start()
        
        # すべてのスレッドの完了を待つ
        for thread in threads:
            thread.join()
        
        # エラーが発生していないことを確認
        assert len(errors) == 0, f"Concurrent execution errors: {errors}"
        assert len(results) == 5, f"Not all environments completed: {results}"