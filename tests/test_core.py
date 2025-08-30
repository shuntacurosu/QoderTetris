import pytest
from tetris.core import TetrisBoard, Action, TetrominoType


class TestTetrisBoard:
    """TetrisBoardクラスのテスト"""

    def test_board_initialization(self, tetris_board):
        """ボード初期化テスト"""
        assert tetris_board.width == 10
        assert tetris_board.height == 20
        assert not tetris_board.game_over
        assert tetris_board.score == 0
        assert tetris_board.lines_cleared == 0
        assert tetris_board.level == 1

    def test_piece_spawn(self, tetris_board):
        """ピース生成テスト"""
        tetris_board.spawn_piece()
        assert tetris_board.current_piece is not None
        assert tetris_board.next_piece is not None
        assert tetris_board.current_piece.x >= 0
        assert tetris_board.current_piece.y >= 0

    def test_piece_movement(self, tetris_board):
        """ピース移動テスト"""
        tetris_board.spawn_piece()
        initial_x = tetris_board.current_piece.x
        
        # 左移動テスト
        result = tetris_board.apply_action(Action.MOVE_LEFT)
        assert result  # 移動成功
        assert tetris_board.current_piece.x == initial_x - 1
        
        # 右移動テスト
        result = tetris_board.apply_action(Action.MOVE_RIGHT)
        assert result
        assert tetris_board.current_piece.x == initial_x

    def test_piece_rotation(self, tetris_board):
        """ピース回転テスト"""
        tetris_board.spawn_piece()
        initial_rotation = tetris_board.current_piece.rotation
        
        result = tetris_board.apply_action(Action.ROTATE)
        assert result  # 回転成功
        assert tetris_board.current_piece.rotation == (initial_rotation + 1) % 4

    def test_soft_drop(self, tetris_board):
        """ソフトドロップテスト"""
        tetris_board.spawn_piece()
        initial_y = tetris_board.current_piece.y
        
        result = tetris_board.apply_action(Action.SOFT_DROP)
        assert result
        assert tetris_board.current_piece.y == initial_y + 1

    def test_collision_detection(self, tetris_board):
        """衝突判定テスト"""
        tetris_board.spawn_piece()
        
        # 左端での左移動テスト
        while tetris_board.current_piece.x > 0:
            tetris_board.apply_action(Action.MOVE_LEFT)
        
        # 壁との衝突
        result = tetris_board.apply_action(Action.MOVE_LEFT)
        assert not result  # 移動失敗

    def test_line_clear_detection(self, tetris_board):
        """ライン消去検出テスト"""
        # 最下行を手動で埋める
        for x in range(tetris_board.width):
            tetris_board.board[tetris_board.height - 1][x] = 1
        
        lines_to_clear = tetris_board._check_line_clears()
        assert tetris_board.height - 1 in lines_to_clear

    def test_step_execution(self, tetris_board):
        """ステップ実行テスト"""
        tetris_board.spawn_piece()
        initial_y = tetris_board.current_piece.y
        
        tetris_board.step()
        assert tetris_board.current_piece.y >= initial_y

    def test_game_over_condition(self, tetris_board):
        """ゲームオーバー条件テスト"""
        # ボードの上部を埋めてゲームオーバー状態を作る
        for y in range(3):
            for x in range(tetris_board.width):
                tetris_board.board[y][x] = 1
        
        tetris_board.spawn_piece()
        assert tetris_board._check_game_over()

    def test_scoring_system(self, tetris_board):
        """スコアリングシステムテスト"""
        initial_score = tetris_board.score
        
        # 最下行を埋めてライン消去を発生させる
        for x in range(tetris_board.width):
            tetris_board.board[tetris_board.height - 1][x] = 1
        
        tetris_board._clear_lines([tetris_board.height - 1])
        assert tetris_board.score > initial_score
        assert tetris_board.lines_cleared == 1


class TestAction:
    """Actionクラスのテスト"""

    def test_action_values(self):
        """アクション値テスト"""
        assert Action.NOTHING == 0
        assert Action.MOVE_LEFT == 1
        assert Action.MOVE_RIGHT == 2
        assert Action.ROTATE == 3
        assert Action.SOFT_DROP == 4
        assert Action.HARD_DROP == 5

    def test_action_count(self):
        """アクション数テスト"""
        actions = [action for action in Action]
        assert len(actions) == 6


class TestTetrominoType:
    """TetrominoTypeクラスのテスト"""

    def test_tetromino_types(self):
        """テトロミノタイプテスト"""
        types = [t for t in TetrominoType]
        assert len(types) == 7  # I, O, T, S, Z, J, L
        
        # 各タイプが存在することを確認
        assert TetrominoType.I in types
        assert TetrominoType.O in types
        assert TetrominoType.T in types
        assert TetrominoType.S in types
        assert TetrominoType.Z in types
        assert TetrominoType.J in types
        assert TetrominoType.L in types