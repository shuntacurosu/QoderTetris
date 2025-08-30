# QoderTetris

Gymnasium準拠のテトリスゲーム環境  
強化学習研究用途を見据えた設計で、現段階では人間による手動プレイを実装。

## 特徴

- **Gymnasium 0.29.0+** 準拠のテトリス環境実装
- **CUIベース** のリアルタイム描画（pygame/tkinter不使用）
- **WASDキー** による快適な操作性
- **モジュール設計** でゲームロジックとUI表示を分離
- 将来の**強化学習エージェント**対応を考慮した拡張可能な設計
- 包括的なテストスイート付き

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
python test.py
```

## 必要ライブラリ

- **gymnasium** >= 0.29.0 - Gymnasium準拠のRL環境
- **numpy** >= 1.24.0 - 数値計算
- **keyboard** >= 0.13.5 - キーボード入力処理

詳細は `requirements.txt` を参照してください。


## プロジェクト構造

```
QoderTetris/
├── requirements.txt     # 依存関係定義
├── README.md           # プロジェクト説明
├── play.py             # メインゲームプレイスクリプト
├── test.py             # テストスイート
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

## 技術仕様

- **Python**: 3.12+
- **環境標準**: Gymnasium 0.29.0+
- **UI**: CUIベース（ターミナル上でのリアルタイム描画）
- **プラットフォーム**: Windows/Unix/Linux 対応

## テスト

コア機能、Gymnasium環境、レンダラー、ゲームプレイの包括的なテストが含まれています。

```bash
python test.py
```

テストは以下を検証します：
- ✅ コア機能（ボード、ピース、アクション）
- ✅ Gymnasium環境（reset, step, render, close）
- ✅ レンダラー（スタート、ゲーム、ゲームオーバー画面）
- ✅ 基本ゲームプレイ（自動デモ付き）

## 開発者情報

### アーキテクチャ
- **モジュール性**: ゲームロジックとUI表示の完全分離
- **拡張性**: 強化学習エージェント接続時の切り替えが容易
- **標準準拠**: Gymnasium環境の標準的なインターフェースを避守

### 主要クラス
- **TetrisBoard**: ゲーム盤面とルール管理
- **TetrisEnv**: Gymnasium準拠のRL環境
- **TetrisRenderer**: CUIベースの描画システム
- **GameController**: キーボード入力処理とアクション変換

## ライセンス

オープンソースプロジェクトです。