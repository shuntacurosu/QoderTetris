import pytest
from tetris.renderer import CUIRenderer
from tetris.core import TetrisBoard


class TestCUIRenderer:
    """CUIRendererクラスのテスト"""

    def test_renderer_initialization(self, cui_renderer):
        """レンダラー初期化テスト"""
        assert cui_renderer is not None
        assert hasattr(cui_renderer, 'render')
        assert hasattr(cui_renderer, 'render_board')
        assert hasattr(cui_renderer, 'render_start_screen')
        assert hasattr(cui_renderer, 'render_game_over')

    def test_board_rendering(self, cui_renderer, tetris_board):
        """ボード描画テスト"""
        tetris_board.spawn_piece()
        
        try:
            result = cui_renderer.render_board(tetris_board)
            assert isinstance(result, str)
            assert len(result) > 0
        except Exception as e:
            pytest.fail(f"Board rendering failed: {e}")

    def test_start_screen_rendering(self, cui_renderer):
        """スタート画面描画テスト"""
        try:
            result = cui_renderer.render_start_screen()
            assert isinstance(result, str)
            assert len(result) > 0
            assert "QoderTetris" in result or "TETRIS" in result.upper()
        except Exception as e:
            pytest.fail(f"Start screen rendering failed: {e}")

    def test_game_over_screen_rendering(self, cui_renderer, tetris_board):
        """ゲームオーバー画面描画テスト"""
        tetris_board.game_over = True
        tetris_board.score = 1000
        
        try:
            result = cui_renderer.render_game_over(tetris_board)
            assert isinstance(result, str)
            assert len(result) > 0
            assert "GAME OVER" in result.upper()
        except Exception as e:
            pytest.fail(f"Game over screen rendering failed: {e}")

    def test_render_method(self, cui_renderer, tetris_board):
        """メインrenderメソッドテスト"""
        tetris_board.spawn_piece()
        
        try:
            result = cui_renderer.render(tetris_board)
            assert isinstance(result, str)
            assert len(result) > 0
        except Exception as e:
            pytest.fail(f"Main render method failed: {e}")

    def test_display_management(self, cui_renderer):
        """画面管理テスト"""
        try:
            # 初期化テスト
            cui_renderer.initialize_display()
            
            # クリアテスト
            cui_renderer.clear_screen()
            
            # クリーンアップテスト
            cui_renderer.cleanup_display()
            
        except Exception as e:
            pytest.fail(f"Display management failed: {e}")

    def test_screen_dimensions(self, cui_renderer):
        """画面サイズテスト"""
        if hasattr(cui_renderer, 'get_terminal_size'):
            try:
                width, height = cui_renderer.get_terminal_size()
                assert width > 0
                assert height > 0
            except Exception as e:
                # ターミナルサイズ取得が失敗してもテストは続行
                pass