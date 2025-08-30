---
trigger: manual
---
# Pythonファイル専用ルール (Specific Files: *.py)

## コーディング標準

### インポート順序
```python
# 1. 標準ライブラリ
import os
import sys
from typing import Optional, Dict

# 2. サードパーティライブラリ
import numpy as np
import gymnasium as gym

# 3. ローカルモジュール
from .core import TetrisBoard
from .renderer import TetrisRenderer
```

### 関数・クラス設計
```python
class ExampleClass:
    """クラスの説明を日本語で記述
    
    Args:
        param1: パラメータの説明
        param2: パラメータの説明
    """
    
    def __init__(self, param1: str, param2: int):
        self.param1 = param1
        self.param2 = param2
    
    def example_method(self) -> bool:
        """メソッドの説明を日本語で記述
        
        Returns:
            bool: 処理結果の説明
        """
        # 実装の詳細説明（必要に応じて）
        return True
```

## エラーハンドリング

### 例外処理の標準形
```python
def safe_operation():
    """安全な操作の実装例"""
    try:
        # 処理の実行
        result = risky_operation()
        return result
    except SpecificException as e:
        # 具体的な例外の処理
        logger.error(f"具体的エラー: {e}")
        raise
    except Exception as e:
        # 予期しない例外の処理
        logger.error(f"予期しないエラー: {e}")
        raise RuntimeError(f"操作に失敗しました: {e}") from e
```

## TDD実践

### テストファーストの実装
```python
# 1. まずテストを書く (test_*.py)
def test_new_feature():
    """新機能のテスト（失敗から開始）"""
    # Arrange
    setup_data = create_test_data()
    
    # Act
    result = new_feature(setup_data)
    
    # Assert
    assert result.is_success()
    assert result.value == expected_value

# 2. 最小限の実装で通す
def new_feature(data):
    """最小限の実装"""
    return MockResult(success=True, value=expected_value)

# 3. リファクタリングで品質向上
def new_feature(data):
    """実際の実装"""
    # 本格的な実装
    pass
```

## パフォーマンス考慮

### 効率的な実装
```python
# NumPy配列の活用
def process_data(data: np.ndarray) -> np.ndarray:
    """NumPyを活用した効率的な処理"""
    # ベクトル化された操作を優先
    return np.where(data > threshold, data * 2, data)

# メモリ効率
def memory_efficient_processing(large_data):
    """メモリ効率を考慮した処理"""
    # ジェネレータやイテレータの活用
    for chunk in process_in_chunks(large_data):
        yield process_chunk(chunk)
```