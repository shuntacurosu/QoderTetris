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
        result = tetris_board.spawn_piece()
        assert result  # スポーン成功
        assert tetris_board.current_piece is not None
        assert tetris_board.next_piece is not None
        assert tetris_board.current_piece.x >= 0
        assert tetris_board.current_piece.y >= 0

    def test_piece_movement(self, tetris_board):
        """ピース移動テスト"""
        tetris_board.spawn_piece()
        initial_x = tetris_board.current_piece.x
        
        # 左移動テスト
        moved, reward = tetris_board.apply_action(Action.MOVE_LEFT)
        assert moved  # 移動成功
        assert tetris_board.current_piece.x == initial_x - 1
        
        # 右移動テスト
        moved, reward = tetris_board.apply_action(Action.MOVE_RIGHT)
        assert moved
        assert tetris_board.current_piece.x == initial_x

    def test_piece_rotation(self, tetris_board):
        """ピース回転テスト"""
        tetris_board.spawn_piece()
        initial_rotation = tetris_board.current_piece.rotation
        
        moved, reward = tetris_board.apply_action(Action.ROTATE)
        assert moved  # 回転成功
        assert tetris_board.current_piece.rotation == (initial_rotation + 1) % 4

    def test_soft_drop(self, tetris_board):
        """ソフトドロップテスト"""
        tetris_board.spawn_piece()
        initial_y = tetris_board.current_piece.y
        
        moved, reward = tetris_board.apply_action(Action.SOFT_DROP)
        assert moved
        assert tetris_board.current_piece.y == initial_y + 1
        assert reward == 1  # ソフトドロップボーナス

    def test_hard_drop(self, tetris_board):
        """ハードドロップテスト"""
        tetris_board.spawn_piece()
        initial_y = tetris_board.current_piece.y
        
        moved, reward = tetris_board.apply_action(Action.HARD_DROP)
        assert moved
        assert tetris_board.current_piece.y > initial_y
        assert reward >= 0  # ハードドロップボーナス

    def test_collision_detection(self, tetris_board):
        """衝突判定テスト"""
        tetris_board.spawn_piece()
        
        # 左端への移動を繰り返す
        while tetris_board.current_piece.x > 0:
            moved, reward = tetris_board.apply_action(Action.MOVE_LEFT)
            if not moved:
                break
        
        # 壁との衝突
        moved, reward = tetris_board.apply_action(Action.MOVE_LEFT)
        assert not moved  # 移動失敗

    def test_step_execution(self, tetris_board):
        """ステップ実行テスト"""
        tetris_board.spawn_piece()
        initial_y = tetris_board.current_piece.y
        
        success, reward = tetris_board.step()
        assert success
        assert tetris_board.current_piece.y >= initial_y

    def test_game_over_condition(self, tetris_board):
        """ゲームオーバー条件テスト"""
        # ボードの上部を埋めてゲームオーバー状態を作る
        for y in range(3):
            for x in range(tetris_board.width):
                tetris_board.board[y][x] = 1
        
        result = tetris_board.spawn_piece()
        assert not result  # スポーン失敗
        assert tetris_board.game_over

    def test_board_state(self, tetris_board):
        """ボード状態取得テスト"""
        tetris_board.spawn_piece()
        
        state = tetris_board.get_state()
        assert isinstance(state, dict)
        assert 'board' in state
        assert 'score' in state
        assert 'lines_cleared' in state
        assert 'level' in state
        assert 'game_over' in state

    def test_board_with_piece(self, tetris_board):
        """ピース付きボード取得テスト"""
        tetris_board.spawn_piece()
        
        board_with_piece = tetris_board.get_board_with_piece()
        assert board_with_piece.shape == (tetris_board.height, tetris_board.width)
        
        # ピースが描画されていることを確認
        original_board = tetris_board.board
        assert not (board_with_piece == original_board).all()

    def test_valid_position_check(self, tetris_board):
        """有効位置チェックテスト"""
        tetris_board.spawn_piece()
        
        # 現在の位置は有効
        assert tetris_board.is_valid_position(tetris_board.current_piece)
        
        # 左端を超えた位置は無効
        invalid_piece = tetris_board.current_piece.move(-10, 0)
        assert not tetris_board.is_valid_position(invalid_piece)

    def test_piece_placement(self, tetris_board):
        """ピース配置テスト"""
        tetris_board.spawn_piece()
        piece = tetris_board.current_piece
        
        # ピースを最下部まで移動
        while tetris_board.is_valid_position(piece.move(0, 1)):
            piece = piece.move(0, 1)
        
        # ピース配置
        initial_score = tetris_board.score
        tetris_board.place_piece(piece)
        
        # ボードにピースが配置されたことを確認
        assert (tetris_board.board > 0).any()


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


class TestTetromino:
    """Tetrominoクラスのテスト"""

    def test_tetromino_creation(self):
        """テトロミノ作成テスト"""
        from tetris.core import Tetromino
        
        piece = Tetromino(TetrominoType.I)
        assert piece.type == TetrominoType.I
        assert piece.x == 3  # デフォルト位置
        assert piece.y == 0
        assert piece.rotation == 0

    def test_tetromino_movement(self):
        """テトロミノ移動テスト"""
        from tetris.core import Tetromino
        
        piece = Tetromino(TetrominoType.T)
        moved_piece = piece.move(1, 1)
        
        # 元のピースは変更されない
        assert piece.x == 3
        assert piece.y == 0
        
        # 新しいピースは移動している
        assert moved_piece.x == 4
        assert moved_piece.y == 1

    def test_tetromino_rotation(self):
        """テトロミノ回転テスト"""
        from tetris.core import Tetromino
        
        piece = Tetromino(TetrominoType.T)
        rotated_piece = piece.rotate()
        
        # 元のピースは変更されない
        assert piece.rotation == 0
        
        # 新しいピースは回転している
        assert rotated_piece.rotation == 1

    def test_tetromino_shape(self):
        """テトロミノ形状テスト"""
        from tetris.core import Tetromino
        
        piece = Tetromino(TetrominoType.I)
        shape = piece.shape
        
        assert len(shape) == 4
        assert len(shape[0]) == 4
        assert any(1 in row for row in shape)  # 少なくとも1つのブロックがある