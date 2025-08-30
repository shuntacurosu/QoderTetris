import pytest
from tetris.env import TetrisEnv
from tetris.core import TetrisBoard
from tetris.renderer import CUIRenderer

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