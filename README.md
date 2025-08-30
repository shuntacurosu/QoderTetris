# QoderTetris

Gymnasium準拠のテトリスゲーム環境  
強化学習研究用途を見据えた設計で、現段階では人間による手動プレイを実装。

## 特徴

- **Gymnasium 0.29.0+** 準拠のテトリス環境実装
- **CUIベース** のリアルタイム描画（pygame/tkinter不使用）
- **WASDキー** による快適な操作性
- **モジュール設計** でゲームロジックとUI表示を分離
- 将来の**強化学習エージェント**対応を考慮した拡張可能な設計
- **包括的なテストスイート** 付き

## セットアップ

### 推奨方法: Conda環境を使用

1. **専用conda環境を作成**
   ```bash
   conda create --name qodertetris python=3.12 --yes
   ```

2. **環境をアクティベート**
   ```bash
   conda activate qodertetris
   ```

3. **依存関係をインストール**
   ```bash
   pip install -r requirements.txt
   ```

### 通常のpip環境を使用する場合

```bash
pip install -r requirements.txt
```

## 実行方法

### ゲームをプレイ
```bash
python play.py
```

### テストを実行
```bash
# 基本テスト
pytest

# カバレッジ付きテスト
pytest --cov=tetris --cov-report=html

# 特定のテストカテゴリ
pytest -m "not slow"          # 高速テストのみ
pytest -m performance         # パフォーマンステスト
pytest -m edge_case           # エッジケーステスト
pytest -m property_based      # プロパティベーステスト
```

## 必要ライブラリ

### 基本依存関係
- **gymnasium** >= 0.29.0 - Gymnasium準拠のRL環境
- **numpy** >= 1.24.0 - 数値計算
- **keyboard** >= 0.13.5 - キーボード入力処理

### テスト依存関係
- **pytest** >= 7.0.0 - テストフレームワーク
- **pytest-cov** >= 4.0.0 - カバレッジ測定
- **pytest-timeout** >= 2.1.0 - タイムアウト制御
- **hypothesis** >= 6.0.0 - プロパティベーステスト
- **psutil** >= 5.9.0 - パフォーマンス監視

詳細は `requirements.txt` を参照してください。

## プロジェクト構造

```
QoderTetris/
├── requirements.txt     # 依存関係定義
├── README.md           # プロジェクト説明
├── pytest.ini         # テスト設定
├── play.py             # メインゲームプレイスクリプト
├── test.py             # 統合テストスクリプト
├── .github/workflows/  # CI/CD設定
│   └── test.yml        # GitHub Actions設定
├── tests/              # テストスイート
│   ├── conftest.py                # テスト設定とフィクスチャ
│   ├── test_core.py              # コアロジックテスト
│   ├── test_env.py               # Gymnasium環境テスト
│   ├── test_renderer.py          # レンダラーテスト
│   ├── test_integration.py       # 統合テスト
│   ├── test_edge_cases.py        # エッジケーステスト
│   ├── test_performance.py       # パフォーマンステスト
│   └── test_property_based.py    # プロパティベーステスト
└── tetris/             # コアモジュール
    ├── __init__.py
    ├── core.py         # テトリスのコアゲームロジック
    ├── env.py          # Gymnasium環境クラス
    ├── renderer.py     # CUI描画システム
    └── input_handler.py # 入力処理システム
```

## 操作方法

### ゲーム操作
- **A/D** または **←/→**: 左右移動
- **W** または **↑**: 回転
- **S** または **↓**: ソフトドロップ（高速落下）
- **スペース**: ハードドロップ（瞬間落下）

### ゲーム制御
- **Q**: ゲーム終了
- **R**: リスタート

## テストスイート

### テストカテゴリ

1. **基本テスト** (`test_core.py`, `test_env.py`, `test_renderer.py`)
   - コア機能の動作確認
   - Gymnasium環境の準拠性検証
   - レンダリング機能テスト

2. **統合テスト** (`test_integration.py`)
   - コンポーネント間の連携テスト
   - エンドツーエンドシナリオ

3. **エッジケーステスト** (`test_edge_cases.py`)
   - 境界条件での動作確認
   - 異常系の処理検証
   - メモリリーク防止テスト

4. **パフォーマンステスト** (`test_performance.py`)
   - 実行速度の測定（目標: 60+ FPS）
   - メモリ使用量の監視
   - スケーラビリティ検証

5. **プロパティベーステスト** (`test_property_based.py`)
   - 不変条件の検証
   - ランダムデータでの堅牢性テスト
   - 決定論的動作の確認

### テスト品質指標

- **行カバレッジ**: 80%以上（目標: 90%）
- **実行速度**: 60+ FPS
- **メモリ使用量**: 安定性確保
- **並行実行**: 複数環境対応

### CI/CD

GitHub Actionsによる自動テスト実行：
- 複数OS対応（Ubuntu, Windows, macOS）
- Python 3.9-3.12サポート
- カバレッジレポート自動生成
- コード品質チェック（Black, flake8, mypy）

## 技術仕様

- **Python**: 3.9+（推奨: 3.12）
- **環境標準**: Gymnasium 0.29.0+
- **UI**: CUIベース（ターミナル上でのリアルタイム描画）
- **プラットフォーム**: Windows/Unix/Linux 対応
- **テスト**: pytest + hypothesis + 性能監視

## 開発者情報

### アーキテクチャ
- **モジュール性**: ゲームロジックとUI表示の完全分離
- **拡張性**: 強化学習エージェント接続時の切り替えが容易
- **標準準拠**: Gymnasium環境の標準的なインターフェースを遵守

### 主要クラス
- **TetrisBoard**: ゲーム盤面とルール管理
- **TetrisEnv**: Gymnasium準拠のRL環境
- **TetrisRenderer**: CUIベースの描画システム
- **GameController**: キーボード入力処理とアクション変換

### 開発ワークフロー
- **TDD**: テスト駆動開発の採用
- **コード品質**: 自動フォーマット・リント
- **継続的統合**: GitHub Actions
- **カバレッジ**: Codecov連携

## ライセンス

オープンソースプロジェクトです。