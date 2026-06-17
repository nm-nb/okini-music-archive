# リア ～春の風を運ぶもの～ 設定資料

このフォルダは、リアの物語の設定資料を追記しながら管理するための場所です。

## 使い方

1. `docs/` の Markdown ファイルに設定を追記する
2. 下記コマンドで公開用 HTML を生成する

```sh
python3 リア/tools/build_site.py
```

3. `リア/site/index.html` をブラウザで開いて確認する

まず自由に書き足したい場合は、`docs/setting-notes.md` に追記する。
整理が進んだら、`docs/world.md` や `docs/characters.md` などの各ページへ移す。

## フォルダ構成

```text
リア/
  docs/      設定資料の原稿 Markdown
  site/      公開用 HTML 出力
  tools/     変換スクリプト
```

## 追記ルール

- 設定の原本は `docs/` 側に書く
- 公開用の見た目は `site/` 側に生成される
- 新しい設定を足すときは、まず既存の `docs/*.md` に追記する
- 迷ったら `docs/setting-notes.md` に書く
- 大きな項目が増えたら、新しい Markdown ファイルを作って `docs/index.md` にリンクを追加する
