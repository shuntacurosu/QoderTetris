"""
Gymnasium準拠のテトリス環境実装
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Any, Dict, Optional, Tuple, Union

from .core import TetrisBoard, Action


class TetrisEnv(gym.Env):
    """
    Gymnasium準拠のテトリス環境
    
    Action Space:
        - 0: NOTHING (何もしない)
        - 1: MOVE_LEFT (左移動)
        - 2: MOVE_RIGHT (右移動) 
        - 3: ROTATE (回転)
        - 4: SOFT_DROP (ソフトドロップ)
        - 5: HARD_DROP (ハードドロップ)
    
    Observation Space:
        - board: (20, 10) ボード状態
        - current_piece_type: int 現在のピース種類
        - current_piece_x: int 現在のピースX座標
        - current_piece_y: int 現在のピースY座標
        - current_piece_rotation: int 現在のピース回転
        - next_piece_type: int 次のピース種類
        - score: int スコア
        - lines_cleared: int 消去ライン数
        - level: int レベル
    
    Reward:
        - 各アクション: 基本0
        - ソフトドロップ: +1
        - ハードドロップ: +2 * 落下距離
        - ライン消去時のスコア増加分
        - ゲームオーバー: -100
    """
    
    metadata = {"render_modes": ["human", "ansi"], "render_fps": 4}
    
    def __init__(self, width: int = 10, height: int = 20, render_mode: Optional[str] = None):
        super().__init__()
        
        self.width = width
        self.height = height
        self.render_mode = render_mode
        
        # アクション空間（6つのアクション）
        self.action_space = spaces.Discrete(6)
        
        # 観測空間
        self.observation_space = spaces.Dict({
            'board': spaces.Box(
                low=0, high=7, shape=(height, width), dtype=np.int32
            ),
            'current_piece_type': spaces.Discrete(8),  # 0-7 (0は空)
            'current_piece_x': spaces.Box(low=0, high=width-1, shape=(), dtype=np.int32),
            'current_piece_y': spaces.Box(low=0, high=height-1, shape=(), dtype=np.int32),
            'current_piece_rotation': spaces.Discrete(4),
            'next_piece_type': spaces.Discrete(8),
            'score': spaces.Box(low=0, high=np.inf, shape=(), dtype=np.int32),
            'lines_cleared': spaces.Box(low=0, high=np.inf, shape=(), dtype=np.int32),
            'level': spaces.Box(low=1, high=np.inf, shape=(), dtype=np.int32),
        })
        
        # ゲーム状態
        self.board = TetrisBoard(width, height)
        self.last_score = 0
        self.step_count = 0
        self.fall_time = 0
        self.fall_speed = 60  # フレーム数（レベルに応じて変更）
        
    def reset(self, *, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[Dict, Dict]:
        """環境をリセット"""
        super().reset(seed=seed)
        
        if seed is not None:
            np.random.seed(seed)
        
        # ボードリセット
        self.board.reset()
        self.board.spawn_piece()
        
        # 内部状態リセット
        self.last_score = 0
        self.step_count = 0
        self.fall_time = 0
        self._update_fall_speed()
        
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, info
    
    def step(self, action: Union[int, Action]) -> Tuple[Dict, float, bool, bool, Dict]:
        """1ステップ実行"""
        if isinstance(action, int):
            action = Action(action)
        
        # 前のスコアを記録
        prev_score = self.board.score
        
        # アクション実行
        action_successful, action_reward = self.board.apply_action(action)
        
        # 自然落下処理
        self.fall_time += 1
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            self.board.step()
        
        # レベル変更時の落下速度更新
        self._update_fall_speed()
        
        # 報酬計算
        reward = action_reward
        
        # スコア増加による報酬
        score_diff = self.board.score - prev_score
        reward += score_diff
        
        # ゲームオーバー時のペナルティ
        if self.board.game_over:
            reward -= 100
        
        # 観測・情報取得
        observation = self._get_observation()
        terminated = self.board.game_over
        truncated = False  # 今回は時間制限なし
        info = self._get_info()
        
        self.step_count += 1
        
        return observation, reward, terminated, truncated, info
    
    def render(self):
        """レンダリング"""
        if self.render_mode == "ansi":
            return self._render_ansi()
        elif self.render_mode == "human":
            print(self._render_ansi())
        else:
            return None
    
    def close(self):
        """環境クリーンアップ"""
        pass
    
    def _get_observation(self) -> Dict:
        """現在の観測を取得"""
        state = self.board.get_state()
        
        return {
            'board': state['board'].astype(np.int32),
            'current_piece_type': np.int32(state['current_piece_type']),
            'current_piece_x': np.int32(state['current_piece_x']),
            'current_piece_y': np.int32(state['current_piece_y']),
            'current_piece_rotation': np.int32(state['current_piece_rotation']),
            'next_piece_type': np.int32(state['next_piece_type']),
            'score': np.int32(state['score']),
            'lines_cleared': np.int32(state['lines_cleared']),
            'level': np.int32(state['level']),
        }
    
    def _get_info(self) -> Dict:
        """追加情報を取得"""
        return {
            'step_count': self.step_count,
            'fall_speed': self.fall_speed,
            'board_with_piece': self.board.get_board_with_piece(),
        }
    
    def _update_fall_speed(self):
        """レベルに応じて落下速度を更新"""
        # レベルが上がるほど速く落下
        self.fall_speed = max(1, 60 - (self.board.level - 1) * 5)
    
    def _render_ansi(self) -> str:
        """ANSI形式でのレンダリング"""
        lines = []
        
        # タイトル
        lines.append("=== QoderTetris ===")
        lines.append("")
        
        # ゲーム情報
        lines.append(f"Score: {self.board.score}")
        lines.append(f"Level: {self.board.level}")
        lines.append(f"Lines: {self.board.lines_cleared}")
        lines.append("")
        
        # 次のピース表示
        if self.board.next_piece:
            lines.append("Next:")
            next_shape = self.board.next_piece.shape
            for row in next_shape:
                line = ""
                for cell in row:
                    line += "██" if cell != 0 else "  "
                lines.append(line)
        lines.append("")
        
        # ボード表示
        board_with_piece = self.board.get_board_with_piece()
        
        # 上端
        lines.append("┌" + "──" * self.width + "┐")
        
        # ボード内容
        for y in range(self.height):
            line = "│"
            for x in range(self.width):
                cell = board_with_piece[y, x]
                if cell == 0:
                    line += "  "
                else:
                    # ピースタイプに応じた表示
                    symbols = {1: "██", 2: "██", 3: "██", 4: "██", 5: "██", 6: "██", 7: "██"}
                    line += symbols.get(cell, "██")
            line += "│"
            lines.append(line)
        
        # 下端
        lines.append("└" + "──" * self.width + "┘")
        
        # ゲームオーバー表示
        if self.board.game_over:
            lines.append("")
            lines.append("GAME OVER")
        
        # 操作説明
        lines.append("")
        lines.append("Controls:")
        lines.append("A/D or ←/→: Move")
        lines.append("W or ↑: Rotate") 
        lines.append("S or ↓: Soft Drop")
        lines.append("Space: Hard Drop")
        lines.append("Q: Quit")
        
        return "\n".join(lines)


# Gymnasiumへの登録
gym.register(
    id='Tetris-v0',
    entry_point='tetris.env:TetrisEnv',
    max_episode_steps=10000,
)