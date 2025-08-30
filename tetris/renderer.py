"""
CUIベースのリアルタイム描画システム
"""

import os
import sys
from typing import Optional
from .core import TetrisBoard, TetrominoType


class CUIRenderer:
    """CUIベースのテトリス描画クラス"""
    
    # テトリミノタイプに応じた色とシンボル
    PIECE_COLORS = {
        0: '',  # 空
        TetrominoType.I: '\033[96m',  # シアン
        TetrominoType.O: '\033[93m',  # 黄色
        TetrominoType.T: '\033[95m',  # マゼンタ
        TetrominoType.S: '\033[92m',  # 緑
        TetrominoType.Z: '\033[91m',  # 赤
        TetrominoType.J: '\033[94m',  # 青
        TetrominoType.L: '\033[33m',  # オレンジ
    }
    
    RESET_COLOR = '\033[0m'
    
    def __init__(self, use_color: bool = True):
        self.use_color = use_color
        self.last_render = ""
    
    def clear_screen(self):
        """画面をクリア"""
        if os.name == 'nt':  # Windows
            os.system('cls')
        else:  # Unix/Linux/Mac
            os.system('clear')
    
    def move_cursor_to_top(self):
        """カーソルを画面上部に移動"""
        sys.stdout.write('\033[H')  # カーソルをホームポジションに
        sys.stdout.flush()
    
    def render_board(self, board: TetrisBoard) -> str:
        """ボードを文字列として描画"""
        lines = []
        
        # タイトル
        lines.append("╔════════════════════════════════════╗")
        lines.append("║           QoderTetris              ║")
        lines.append("╠════════════════════════════════════╣")
        
        # ゲーム情報を横並びで表示
        score_line = f"║ Score: {board.score:<8} Level: {board.level:<3} ║"
        lines.append(score_line)
        
        lines_line = f"║ Lines: {board.lines_cleared:<8}            ║"
        lines.append(lines_line)
        
        lines.append("╠════════════════════════════════════╣")
        
        # 次のピース表示エリア
        lines.append("║ Next:                              ║")
        
        if board.next_piece:
            next_shape = board.next_piece.shape
            for i, row in enumerate(next_shape):
                if i < 4:  # 最大4行表示
                    line = "║ "
                    for cell in row:
                        if cell != 0 and self.use_color:
                            color = self.PIECE_COLORS.get(board.next_piece.type, '')
                            line += f"{color}██{self.RESET_COLOR}"
                        elif cell != 0:
                            line += "██"
                        else:
                            line += "  "
                    # パディング調整
                    line += " " * (32 - len(line.replace('\033[96m', '').replace('\033[0m', '').replace('\033[93m', '').replace('\033[95m', '').replace('\033[92m', '').replace('\033[91m', '').replace('\033[94m', '').replace('\033[33m', '')) + len("║ "))
                    line += " ║"
                    lines.append(line)
        
        # 空行で調整
        for _ in range(4 - (4 if board.next_piece else 0)):
            lines.append("║                                    ║")
        
        lines.append("╠════════════════════════════════════╣")
        
        # メインゲームボード
        board_with_piece = board.get_board_with_piece()
        
        # 上端
        lines.append("║ ┌────────────────────┐             ║")
        
        # ボード内容（上位4行は非表示エリア）
        for y in range(4, board.height):  # 上位4行をスキップ
            line = "║ │"
            for x in range(board.width):
                cell = board_with_piece[y, x]
                if cell == 0:
                    line += "  "
                else:
                    if self.use_color:
                        color = self.PIECE_COLORS.get(cell, '')
                        line += f"{color}██{self.RESET_COLOR}"
                    else:
                        line += "██"
            line += "│             ║"
            lines.append(line)
        
        # 下端
        lines.append("║ └────────────────────┘             ║")
        
        lines.append("╠════════════════════════════════════╣")
        
        # ゲームオーバー表示
        if board.game_over:
            lines.append("║            GAME OVER               ║")
            lines.append("║         Press R to Restart         ║")
        else:
            lines.append("║                                    ║")
            lines.append("║                                    ║")
        
        lines.append("╠════════════════════════════════════╣")
        
        # 操作説明
        lines.append("║ Controls:                          ║")
        lines.append("║ A/D or ←/→: Move Left/Right        ║")
        lines.append("║ W or ↑: Rotate                     ║")
        lines.append("║ S or ↓: Soft Drop                  ║")
        lines.append("║ Space: Hard Drop                   ║")
        lines.append("║ R: Restart  Q: Quit                ║")
        lines.append("╚════════════════════════════════════╝")
        
        return "\n".join(lines)
    
    def render_game_over(self, board: TetrisBoard) -> str:
        """ゲームオーバー画面を描画"""
        lines = []
        
        lines.append("╔════════════════════════════════════╗")
        lines.append("║            GAME OVER               ║")
        lines.append("╠════════════════════════════════════╣")
        lines.append(f"║ Final Score: {board.score:<17} ║")
        lines.append(f"║ Level Reached: {board.level:<15} ║")
        lines.append(f"║ Lines Cleared: {board.lines_cleared:<15} ║")
        lines.append("╠════════════════════════════════════╣")
        lines.append("║                                    ║")
        lines.append("║         Press R to Restart         ║")
        lines.append("║         Press Q to Quit            ║")
        lines.append("║                                    ║")
        lines.append("╚════════════════════════════════════╝")
        
        return "\n".join(lines)
    
    def render_start_screen(self) -> str:
        """スタート画面を描画"""
        lines = []
        
        lines.append("╔════════════════════════════════════╗")
        lines.append("║           QoderTetris              ║")
        lines.append("║                                    ║")
        lines.append("║      Gymnasium Compatible          ║")
        lines.append("║                                    ║")
        lines.append("╠════════════════════════════════════╣")
        lines.append("║                                    ║")
        lines.append("║      Press any key to start       ║")
        lines.append("║                                    ║")
        lines.append("║         Press Q to Quit            ║")
        lines.append("║                                    ║")
        lines.append("╠════════════════════════════════════╣")
        lines.append("║ Controls:                          ║")
        lines.append("║ A/D or ←/→: Move Left/Right        ║")
        lines.append("║ W or ↑: Rotate                     ║")
        lines.append("║ S or ↓: Soft Drop                  ║")
        lines.append("║ Space: Hard Drop                   ║")
        lines.append("║ R: Restart  Q: Quit                ║")
        lines.append("╚════════════════════════════════════╝")
        
        return "\n".join(lines)
    
    def render(self, board: Optional[TetrisBoard] = None, game_state: str = "playing") -> str:
        """
        ゲーム状態に応じて描画
        
        Args:
            board: テトリスボード（Noneの場合はスタート画面）
            game_state: ゲーム状態 ("start", "playing", "game_over")
        """
        if game_state == "start" or board is None:
            return self.render_start_screen()
        elif game_state == "game_over" or board.game_over:
            return self.render_game_over(board)
        else:
            return self.render_board(board)
    
    def update_display(self, content: str):
        """表示を更新（ちらつき防止）"""
        if content != self.last_render:
            self.move_cursor_to_top()
            sys.stdout.write(content)
            sys.stdout.flush()
            self.last_render = content
    
    def initialize_display(self):
        """表示初期化"""
        self.clear_screen()
        # カーソルを非表示に（対応している場合）
        try:
            sys.stdout.write('\033[?25l')
            sys.stdout.flush()
        except:
            pass
    
    def cleanup_display(self):
        """表示クリーンアップ"""
        # カーソルを表示に戻す
        try:
            sys.stdout.write('\033[?25h')
            sys.stdout.flush()
        except:
            pass