"""
テトリスのコアゲームロジック実装
"""

import numpy as np
from typing import List, Tuple, Optional
from enum import IntEnum
import copy

class Action(IntEnum):
    """アクション定義"""
    NOTHING = 0
    MOVE_LEFT = 1
    MOVE_RIGHT = 2
    ROTATE = 3
    SOFT_DROP = 4
    HARD_DROP = 5

class TetrominoType(IntEnum):
    """テトリミノの種類"""
    I = 1
    O = 2
    T = 3
    S = 4
    Z = 5
    J = 6
    L = 7

# テトリミノの形状定義（4x4マトリックス）
TETROMINO_SHAPES = {
    TetrominoType.I: [
        [[0, 0, 0, 0],
         [1, 1, 1, 1],
         [0, 0, 0, 0],
         [0, 0, 0, 0]]
    ],
    TetrominoType.O: [
        [[0, 0, 0, 0],
         [0, 1, 1, 0],
         [0, 1, 1, 0],
         [0, 0, 0, 0]]
    ],
    TetrominoType.T: [
        [[0, 0, 0, 0],
         [0, 1, 0, 0],
         [1, 1, 1, 0],
         [0, 0, 0, 0]]
    ],
    TetrominoType.S: [
        [[0, 0, 0, 0],
         [0, 1, 1, 0],
         [1, 1, 0, 0],
         [0, 0, 0, 0]]
    ],
    TetrominoType.Z: [
        [[0, 0, 0, 0],
         [1, 1, 0, 0],
         [0, 1, 1, 0],
         [0, 0, 0, 0]]
    ],
    TetrominoType.J: [
        [[0, 0, 0, 0],
         [1, 0, 0, 0],
         [1, 1, 1, 0],
         [0, 0, 0, 0]]
    ],
    TetrominoType.L: [
        [[0, 0, 0, 0],
         [0, 0, 1, 0],
         [1, 1, 1, 0],
         [0, 0, 0, 0]]
    ]
}

class Tetromino:
    """テトリミノクラス"""
    
    def __init__(self, tetromino_type: TetrominoType, x: int = 3, y: int = 0):
        self.type = tetromino_type
        self.x = x
        self.y = y
        self.rotation = 0
        self.shapes = self._generate_rotations()
    
    def _generate_rotations(self) -> List[List[List[int]]]:
        """回転パターンを生成"""
        base_shape = TETROMINO_SHAPES[self.type][0]
        rotations = [base_shape]
        
        # Oピースは回転しない
        if self.type == TetrominoType.O:
            return rotations * 4
        
        # 他のピースは90度ずつ回転
        current = base_shape
        for _ in range(3):
            current = self._rotate_90(current)
            rotations.append(current)
        
        return rotations
    
    def _rotate_90(self, shape: List[List[int]]) -> List[List[int]]:
        """90度時計回りに回転"""
        return [[shape[3-j][i] for j in range(4)] for i in range(4)]
    
    @property
    def shape(self) -> List[List[int]]:
        """現在の回転状態の形状を取得"""
        return self.shapes[self.rotation % 4]
    
    def rotate(self) -> 'Tetromino':
        """回転した新しいテトリミノを返す"""
        new_tetromino = copy.deepcopy(self)
        new_tetromino.rotation = (self.rotation + 1) % 4
        return new_tetromino
    
    def move(self, dx: int, dy: int) -> 'Tetromino':
        """移動した新しいテトリミノを返す"""
        new_tetromino = copy.deepcopy(self)
        new_tetromino.x += dx
        new_tetromino.y += dy
        return new_tetromino

class TetrisBoard:
    """テトリスボードクラス"""
    
    def __init__(self, width: int = 10, height: int = 20):
        self.width = width
        self.height = height
        self.board = np.zeros((height, width), dtype=int)
        self.current_piece: Optional[Tetromino] = None
        self.next_piece: Optional[Tetromino] = None
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        
    def reset(self):
        """ボードをリセット"""
        self.board = np.zeros((self.height, self.width), dtype=int)
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
    
    def spawn_piece(self) -> bool:
        """新しいピースを生成"""
        if self.next_piece is None:
            self.next_piece = self._random_piece()
        
        self.current_piece = self.next_piece
        self.next_piece = self._random_piece()
        
        # ゲームオーバーチェック
        if not self.is_valid_position(self.current_piece):
            self.game_over = True
            return False
        
        return True
    
    def _random_piece(self) -> Tetromino:
        """ランダムなテトリミノを生成"""
        piece_type = np.random.choice(list(TetrominoType))
        return Tetromino(piece_type)
    
    def is_valid_position(self, tetromino: Tetromino) -> bool:
        """テトリミノの位置が有効かチェック"""
        shape = tetromino.shape
        
        for dy in range(4):
            for dx in range(4):
                if shape[dy][dx] != 0:
                    nx, ny = tetromino.x + dx, tetromino.y + dy
                    
                    # 境界チェック
                    if nx < 0 or nx >= self.width or ny >= self.height:
                        return False
                    
                    # 上端は除外（スポーン時）
                    if ny < 0:
                        continue
                        
                    # 既存ブロックとの衝突チェック
                    if self.board[ny][nx] != 0:
                        return False
        
        return True
    
    def place_piece(self, tetromino: Tetromino):
        """テトリミノをボードに固定"""
        shape = tetromino.shape
        
        for dy in range(4):
            for dx in range(4):
                if shape[dy][dx] != 0:
                    nx, ny = tetromino.x + dx, tetromino.y + dy
                    if 0 <= ny < self.height and 0 <= nx < self.width:
                        self.board[ny][nx] = tetromino.type
        
        # ライン消去チェック
        self._clear_lines()
    
    def _clear_lines(self):
        """完成したラインを消去"""
        lines_to_clear = []
        
        for y in range(self.height):
            if np.all(self.board[y] != 0):
                lines_to_clear.append(y)
        
        if lines_to_clear:
            # 上から下へ順番に処理
            for y in reversed(lines_to_clear):
                # 該当行を削除し、上部に空行を追加
                self.board = np.delete(self.board, y, axis=0)
                self.board = np.insert(self.board, 0, np.zeros(self.width, dtype=int), axis=0)
            
            # スコア計算
            cleared_count = len(lines_to_clear)
            self.lines_cleared += cleared_count
            line_scores = [0, 40, 100, 300, 1200]  # 0, 1, 2, 3, 4ライン
            score_multiplier = line_scores[min(cleared_count, 4)]
            self.score += score_multiplier * (self.level + 1)
            
            # レベルアップ（10ライン毎）
            self.level = self.lines_cleared // 10 + 1
    
    def apply_action(self, action: Action) -> Tuple[bool, int]:
        """アクションを適用"""
        if self.game_over or self.current_piece is None:
            return False, 0
        
        reward = 0
        moved = False
        
        if action == Action.MOVE_LEFT:
            new_piece = self.current_piece.move(-1, 0)
            if self.is_valid_position(new_piece):
                self.current_piece = new_piece
                moved = True
        
        elif action == Action.MOVE_RIGHT:
            new_piece = self.current_piece.move(1, 0)
            if self.is_valid_position(new_piece):
                self.current_piece = new_piece
                moved = True
        
        elif action == Action.ROTATE:
            new_piece = self.current_piece.rotate()
            if self.is_valid_position(new_piece):
                self.current_piece = new_piece
                moved = True
        
        elif action == Action.SOFT_DROP:
            new_piece = self.current_piece.move(0, 1)
            if self.is_valid_position(new_piece):
                self.current_piece = new_piece
                reward = 1  # ソフトドロップボーナス
                moved = True
        
        elif action == Action.HARD_DROP:
            # 一番下まで落とす
            drop_distance = 0
            while True:
                new_piece = self.current_piece.move(0, drop_distance + 1)
                if not self.is_valid_position(new_piece):
                    break
                drop_distance += 1
            
            if drop_distance > 0:
                self.current_piece = self.current_piece.move(0, drop_distance)
                reward = drop_distance * 2  # ハードドロップボーナス
                moved = True
        
        return moved, reward
    
    def step(self) -> Tuple[bool, int]:
        """1ステップ進める（自然落下）"""
        if self.game_over or self.current_piece is None:
            return False, 0
        
        # 自然落下を試行
        new_piece = self.current_piece.move(0, 1)
        
        if self.is_valid_position(new_piece):
            self.current_piece = new_piece
            return True, 0
        else:
            # 着地したのでピースを固定
            self.place_piece(self.current_piece)
            self.current_piece = None
            
            # 新しいピースをスポーン
            if not self.spawn_piece():
                return False, 0  # ゲームオーバー
            
            return True, 0
    
    def get_board_with_piece(self) -> np.ndarray:
        """現在のピースを含むボード状態を取得"""
        display_board = self.board.copy()
        
        if self.current_piece is not None:
            shape = self.current_piece.shape
            for dy in range(4):
                for dx in range(4):
                    if shape[dy][dx] != 0:
                        nx, ny = self.current_piece.x + dx, self.current_piece.y + dy
                        if 0 <= ny < self.height and 0 <= nx < self.width:
                            display_board[ny][nx] = self.current_piece.type
        
        return display_board
    
    def get_state(self) -> dict:
        """現在の状態を辞書形式で取得"""
        return {
            'board': self.board.copy(),
            'board_with_piece': self.get_board_with_piece(),
            'current_piece_type': self.current_piece.type if self.current_piece else 0,
            'current_piece_x': self.current_piece.x if self.current_piece else 0,
            'current_piece_y': self.current_piece.y if self.current_piece else 0,
            'current_piece_rotation': self.current_piece.rotation if self.current_piece else 0,
            'next_piece_type': self.next_piece.type if self.next_piece else 0,
            'score': self.score,
            'lines_cleared': self.lines_cleared,
            'level': self.level,
            'game_over': self.game_over
        }