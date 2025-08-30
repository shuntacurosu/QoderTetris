# MCPツール活用ガイド (Apply Manually)

**使用方法**: @rule mcp_tools でチャットで手動適用

## 利用可能なMCPツール一覧

### Context7 - ライブラリドキュメント
```bash
# ライブラリID解決
@mcp_context7_resolve-library-id gymnasium

# ドキュメント取得
@mcp_context7_get-library-docs /gymnasium/gymnasium
```

### DeepWiki - GitHub情報
```bash
# リポジトリ構造確認
@mcp_deepwiki_read_wiki_structure facebook/react

# リポジトリ内容確認
@mcp_deepwiki_read_wiki_contents facebook/react

# 質問による情報取得
@mcp_deepwiki_ask_question facebook/react "How to setup development environment?"
```

### GitHub操作
```bash
# リポジトリ検索
@mcp_github_search_repositories "tetris gymnasium"

# ファイル内容取得
@mcp_github_get_file_contents owner repo path/to/file.py

# リポジトリ作成
@mcp_github_create_repository project_name
```

## MCPツール活用シナリオ

### 1. ライブラリ調査・選定時
```bash
# 1. ライブラリ検索
@mcp_github_search_repositories "python gymnasium tetris"

# 2. ライブラリIDの解決
@mcp_context7_resolve-library-id gymnasium

# 3. ドキュメント詳細取得
@mcp_context7_get-library-docs /gymnasium/gymnasium

# 4. 実装例の調査
@mcp_deepwiki_ask_question Farama-Foundation/Gymnasium "How to create custom environment?"
```

### 2. 技術実装の調査時
```bash
# 既存実装の調査
@mcp_github_search_code "class TetrisEnv gym.Env"

# ベストプラクティスの確認
@mcp_deepwiki_read_wiki_contents relevant/repository

# 具体的な実装方法の質問
@mcp_deepwiki_ask_question repository/name "How to implement keyboard input handling?"
```

### 3. プロジェクト管理時
```bash
# リポジトリ作成
@mcp_github_create_repository new_project

# ファイルの一括アップロード
@mcp_github_push_files owner repo branch files

# Issue作成
@mcp_github_create_issue owner repo "Feature request title"
```

## 効果的な活用方法

### 段階的アプローチ
1. **概要把握**: リポジトリ構造やWikiで全体像を理解
2. **詳細調査**: 具体的なドキュメントやコード例を取得
3. **実装確認**: 実際のコードや設定ファイルを確認
4. **質問による深掘り**: 不明点を直接質問で解決

### 情報の統合
- 複数のMCPツールから得た情報を統合
- 技術選定時は複数の観点から評価
- 実装前に十分な調査を実施

### ベストプラクティス
- **具体的なクエリ**: 曖昧でない明確な検索条件
- **段階的詳細化**: 広範囲から具体的な情報へ
- **複数ソース確認**: 単一ソースに依存しない情報収集