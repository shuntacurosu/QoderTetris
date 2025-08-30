import pytest
from tetris.env import TetrisEnv
from tetris.core import TetrisBoard
from tetris.renderer import CUIRenderer
from tetris.input_handler import InputHandler

@pytest.fixture
def tetris_env():
    """TetrisEnv インスタンスを提供するフィクスチャ"""
    env = TetrisEnv()
    yield env
    env.close()

@pytest.fixture
def tetris_board():
    """TetrisBoard インスタンスを提供するフィクスチャ"""
    board = TetrisBoard()
    return board

@pytest.fixture
def cui_renderer():
    """CUIRenderer インスタンスを提供するフィクスチャ"""
    renderer = CUIRenderer()
    return renderer

@pytest.fixture
def input_handler():
    """InputHandler インスタンスを提供するフィクスチャ"""
    handler = InputHandler()
    yield handler
    handler.stop()