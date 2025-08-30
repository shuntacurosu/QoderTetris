# QoderTetris

Gymnasium準拠のテトリスゲーム環境  
強化学習研究用途を見据えた設計で、現段階では人間による手動プレイを実装。

## 機能

- Gymnasium環境準拠のテトリス実装
- CUIベースのリアルタイム描画
- 人間による手動プレイ対応
- 将来の強化学習エージェント対応を考慮した設計

## 必要ライブラリ

```bash
pip install -r requirements.txt
```

## 実行方法

```bash
python play.py
```

## プロジェクト構造

```
QoderTetris/
├── requirements.txt
├── README.md
├── tetris/
│   ├── __init__.py
│   ├── core.py          # テトリスのコアゲームロジック
│   ├── env.py           # Gymnasium環境クラス
│   ├── renderer.py      # CUI描画システム
│   └── input_handler.py # 入力処理システム
└── play.py              # メインプレイスクリプト
```

## 操作方法

- A/D または ←/→: 左右移動
- W または ↑: 回転
- S または ↓: 高速落下
- Q: ゲーム終了