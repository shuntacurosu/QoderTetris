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
        assert hasattr(cui_renderer, 'use_color')

    def test_board_rendering(self, cui_renderer, tetris_board):
        """ボード描画テスト"""
        tetris_board.spawn_piece()
        
        try:
            result = cui_renderer.render_board(tetris_board)
            assert isinstance(result, str)
            assert len(result) > 0
            assert "QoderTetris" in result
        except Exception as e:
            pytest.fail(f"Board rendering failed: {e}")

    def test_start_screen_rendering(self, cui_renderer):
        """スタート画面描画テスト"""
        try:
            result = cui_renderer.render_start_screen()
            assert isinstance(result, str)
            assert len(result) > 0
            assert "QoderTetris" in result
            assert "Press any key to start" in result
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
            assert "GAME OVER" in result
            assert "1000" in result  # スコアが表示される
        except Exception as e:
            pytest.fail(f"Game over screen rendering failed: {e}")

    def test_render_method_with_states(self, cui_renderer, tetris_board):
        """状態別renderメソッドテスト"""
        tetris_board.spawn_piece()
        
        try:
            # playing状態のレンダリング
            result = cui_renderer.render(tetris_board, "playing")
            assert isinstance(result, str)
            assert len(result) > 0
            
            # start状態のレンダリング
            result = cui_renderer.render(tetris_board, "start")
            assert isinstance(result, str)
            assert "Press any key to start" in result
            
            # game_over状態のレンダリング
            tetris_board.game_over = True
            result = cui_renderer.render(tetris_board, "game_over")
            assert isinstance(result, str)
            assert "GAME OVER" in result
            
        except Exception as e:
            pytest.fail(f"State-based render method failed: {e}")

    def test_render_method_without_board(self, cui_renderer):
        """ボードなしのrenderメソッドテスト"""
        try:
            # Noneボードでスタート画面を表示
            result = cui_renderer.render(None, "start")
            assert isinstance(result, str)
            assert "Press any key to start" in result
            
            # デフォルト状態
            result = cui_renderer.render()
            assert isinstance(result, str)
            
        except Exception as e:
            pytest.fail(f"Render without board failed: {e}")

    def test_display_management(self, cui_renderer):
        """画面管理テスト"""
        try:
            # 初期化テスト
            cui_renderer.initialize_display()
            
            # クリアテスト
            cui_renderer.clear_screen()
            
            # カーソル移動テスト
            cui_renderer.move_cursor_to_top()
            
            # 更新テスト
            test_content = "Test content"
            cui_renderer.update_display(test_content)
            assert cui_renderer.last_render == test_content
            
            # クリーンアップテスト
            cui_renderer.cleanup_display()
            
        except Exception as e:
            pytest.fail(f"Display management failed: {e}")

    def test_color_functionality(self):
        """色機能テスト"""
        # 色ありレンダラー
        color_renderer = CUIRenderer(use_color=True)
        assert color_renderer.use_color == True
        
        # 色なしレンダラー
        no_color_renderer = CUIRenderer(use_color=False)
        assert no_color_renderer.use_color == False
        
        # 色設定の確認
        assert hasattr(color_renderer, 'PIECE_COLORS')
        assert hasattr(color_renderer, 'RESET_COLOR')

    def test_board_with_next_piece(self, cui_renderer, tetris_board):
        """次のピース表示テスト"""
        tetris_board.spawn_piece()  # current_pieceとnext_pieceを生成
        
        try:
            result = cui_renderer.render_board(tetris_board)
            assert isinstance(result, str)
            assert "Next:" in result
            
        except Exception as e:
            pytest.fail(f"Board with next piece rendering failed: {e}")

    def test_empty_board_rendering(self, cui_renderer):
        """空のボード描画テスト"""
        empty_board = TetrisBoard()
        # ピースをスポーンしない状態でテスト
        
        try:
            result = cui_renderer.render_board(empty_board)
            assert isinstance(result, str)
            assert len(result) > 0
            
        except Exception as e:
            pytest.fail(f"Empty board rendering failed: {e}")

    def test_update_display_optimization(self, cui_renderer):
        """表示更新最適化テスト"""
        test_content = "Test content for optimization"
        
        # 初回更新
        cui_renderer.update_display(test_content)
        assert cui_renderer.last_render == test_content
        
        # 同じ内容での更新（最適化されるべき）
        cui_renderer.update_display(test_content)
        assert cui_renderer.last_render == test_content
        
        # 異なる内容での更新
        new_content = "New test content"
        cui_renderer.update_display(new_content)
        assert cui_renderer.last_render == new_content