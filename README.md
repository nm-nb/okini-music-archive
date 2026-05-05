# oKini Music Character Archive

GitHub Pages向けの静的キャラクターアーカイブです。

## 公開方法

1. GitHubで公開リポジトリを作成する。
2. このフォルダの中身をリポジトリへpushする。
3. GitHubの `Settings > Pages` で `Deploy from a branch` を選ぶ。
4. Branchを `main`、Folderを `/ (root)` にする。
5. 表示された `https://<user>.github.io/<repo>/` をYouTube概要欄に貼る。

## YouTube概要欄用リンク例

```text
▼キャラクター設定・キャラシート
https://<user>.github.io/<repo>/charsheets/uzan-no-batto/
```

## 構成

- `index.html`: トップページ
- `charsheets/<slug>/index.html`: キャラクター個別ページ
- `assets/charsheets/<slug>/profile.png`: 通常キャラシート原本
- `assets/charsheets/<slug>/simple.png`: シンプルキャラシート原本
- `assets/charsheets/<slug>/*-preview.jpg`: 軽量プレビュー
- `characters.json`: AI検索や将来の自動更新用メタデータ
