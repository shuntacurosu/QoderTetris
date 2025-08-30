---
trigger: manual
---
# Python環境セットアップルール (Model Decision)

**適用条件**: 新しいPythonプロジェクトの開始、環境構築時

## conda仮想環境の必須使用

### 1. 環境作成手順
```bash
# プロジェクト専用環境の作成
conda create --name [project_name] python=3.12 --yes

# 環境のアクティベート
conda activate [project_name]

# 依存関係のインストール
pip install -r requirements.txt
```

### 2. 環境管理のベストプラクティス
- **プロジェクト名**: 明確で識別しやすい環境名
- **Python版指定**: 明示的なPythonバージョン指定
- **requirements.txt**: 依存関係の適切な管理
- **conda vs pip**: conda優先、unavailableな場合のみpip使用

### 3. 環境分離の原則
- **base環境の保護**: base環境には最小限のパッケージのみ
- **プロジェクト専用**: 各プロジェクトに独立した環境
- **依存関係の明確化**: バージョン固定による再現性確保

## 環境構築の文書化

### README.mdへの記載例
```markdown
## セットアップ

### 推奨方法: Conda環境を使用

1. **専用conda環境を作成**
   ```bash
   conda create --name [project_name] python=3.12 --yes
   ```

2. **環境をアクティベート**
   ```bash
   conda activate [project_name]
   ```

3. **依存関係をインストール**
   ```bash
   pip install -r requirements.txt
   ```
```

### requirements.txt の管理
```bash
# 現在の環境の依存関係を出力
pip freeze > requirements.txt

# バージョン指定の例
gymnasium>=0.29.0
numpy>=1.24.0
keyboard>=0.13.5
```

## 環境の検証

### 動作確認コード
```python
def verify_environment():
    """環境のセットアップ確認"""
    try:
        import sys
        print(f"Python version: {sys.version}")
        
        # 主要ライブラリのインポート確認
        import gymnasium
        import numpy
        
        print("環境セットアップ成功!")
        return True
    except ImportError as e:
        print(f"環境セットアップエラー: {e}")
        return False
```

### トラブルシューティング
- 環境が見つからない場合の対処
- 依存関係の競合解決
- パッケージインストールエラーの対応