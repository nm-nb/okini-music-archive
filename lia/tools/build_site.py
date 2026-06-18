#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE = ROOT / "site"


ORDER = [
    "index.md",
    "setting-notes.md",
    "timeline.md",
    "crossover.md",
    "structure.md",
    "world.md",
    "characters.md",
    "episode-06.md",
    "episode-07.md",
]


def inline_markup(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", markdown_link, text)
    return text


def markdown_link(match: re.Match[str]) -> str:
    label = match.group(1)
    href = match.group(2)
    if href == "index.md":
        href = "index.html"
    elif href.endswith(".md"):
        href = href[:-3] + ".html"
    return f'<a href="{href}">{label}</a>'


def convert_table(lines: list[str]) -> str:
    rows = []
    for line in lines:
        cells = [inline_markup(cell.strip()) for cell in line.strip().strip("|").split("|")]
        rows.append(cells)

    if len(rows) >= 2:
        body = rows[:1] + rows[2:]
    else:
        body = rows

    output = ["<table>"]
    if body:
        output.append("<thead><tr>")
        for cell in body[0]:
            output.append(f"<th>{cell}</th>")
        output.append("</tr></thead>")
    if len(body) > 1:
        output.append("<tbody>")
        for row in body[1:]:
            output.append("<tr>")
            for cell in row:
                output.append(f"<td>{cell}</td>")
            output.append("</tr>")
        output.append("</tbody>")
    output.append("</table>")
    return "\n".join(output)


def markdown_to_html(markdown: str) -> str:
    output: list[str] = []
    paragraph: list[str] = []
    table: list[str] = []
    in_code = False
    code_lines: list[str] = []
    list_open = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            output.append(f"<p>{inline_markup(' '.join(paragraph))}</p>")
            paragraph = []

    def flush_table() -> None:
        nonlocal table
        if table:
            output.append(convert_table(table))
            table = []

    def close_list() -> None:
        nonlocal list_open
        if list_open:
            output.append("</ul>")
            list_open = False

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()

        if line.startswith("```"):
            flush_paragraph()
            flush_table()
            close_list()
            if in_code:
                output.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(raw_line)
            continue

        if line.startswith("|") and line.endswith("|"):
            flush_paragraph()
            close_list()
            table.append(line)
            continue
        flush_table()

        if not line.strip():
            flush_paragraph()
            close_list()
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1))
            text = inline_markup(heading.group(2))
            output.append(f"<h{level}>{text}</h{level}>")
            continue

        if line.startswith("- "):
            flush_paragraph()
            if not list_open:
                output.append("<ul>")
                list_open = True
            output.append(f"<li>{inline_markup(line[2:].strip())}</li>")
            continue

        paragraph.append(line.strip())

    flush_paragraph()
    flush_table()
    close_list()
    return "\n".join(output)


def page_template(title: str, body: str, nav: str) -> str:
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <div class="site-title">リア ～春の風を運ぶもの～</div>
    <nav>{nav}
      <a href="editor.html">編集</a></nav>
  </header>
  <main>
    {body}
  </main>
</body>
</html>
"""


def title_from_markdown(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def main() -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    files = [DOCS / name for name in ORDER if (DOCS / name).exists()]
    files.extend(sorted(path for path in DOCS.glob("*.md") if path.name not in ORDER))

    nav_items = []
    titles = {}
    for path in files:
        markdown = path.read_text(encoding="utf-8")
        title = title_from_markdown(markdown, path.stem)
        titles[path.name] = title
        href = "index.html" if path.name == "index.md" else f"{path.stem}.html"
        nav_items.append(f'<a href="{href}">{html.escape(title)}</a>')
    nav = "\n      ".join(nav_items)

    for path in files:
        markdown = path.read_text(encoding="utf-8")
        title = titles[path.name]
        body = markdown_to_html(markdown)
        filename = "index.html" if path.name == "index.md" else f"{path.stem}.html"
        (SITE / filename).write_text(page_template(title, body, nav), encoding="utf-8")

    (SITE / "editor.html").write_text(editor_template(nav), encoding="utf-8")
    (SITE / "style.css").write_text(STYLE, encoding="utf-8")
    print(f"Generated {len(files)} pages and editor in {SITE}")


STYLE = """
:root {
  color-scheme: light;
  --bg: #f7f3ea;
  --paper: #fffdf8;
  --ink: #24211d;
  --muted: #6f675e;
  --line: #dfd4c2;
  --accent: #8d2f3f;
  --accent-2: #2f6f73;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", sans-serif;
  line-height: 1.75;
}

header {
  border-bottom: 1px solid var(--line);
  background: rgba(255, 253, 248, 0.96);
  position: sticky;
  top: 0;
  z-index: 1;
}

.site-title {
  max-width: 1080px;
  margin: 0 auto;
  padding: 18px 24px 8px;
  font-weight: 700;
  font-size: 20px;
}

nav {
  max-width: 1080px;
  margin: 0 auto;
  padding: 0 24px 14px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

nav a {
  color: var(--accent-2);
  text-decoration: none;
  border: 1px solid var(--line);
  background: #ffffff;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 14px;
}

main {
  max-width: 960px;
  margin: 32px auto 80px;
  padding: 34px 42px;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 12px;
}

h1,
h2,
h3 {
  line-height: 1.35;
  letter-spacing: 0;
}

h1 {
  margin-top: 0;
  font-size: 30px;
}

h2 {
  margin-top: 42px;
  border-bottom: 1px solid var(--line);
  padding-bottom: 8px;
  font-size: 22px;
}

h3 {
  margin-top: 30px;
  font-size: 18px;
}

a {
  color: var(--accent);
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 18px 0 28px;
  font-size: 14px;
}

th,
td {
  border: 1px solid var(--line);
  padding: 8px 10px;
  vertical-align: top;
}

th {
  background: #f0e7d8;
  text-align: left;
}

code {
  background: #f0e7d8;
  padding: 0.1em 0.35em;
  border-radius: 4px;
}

pre {
  overflow-x: auto;
  background: #2b2926;
  color: #fffaf0;
  padding: 16px;
  border-radius: 8px;
}

@media (max-width: 700px) {
  main {
    margin: 18px 12px 48px;
    padding: 24px 18px;
    border-radius: 8px;
  }

  .site-title,
  nav {
    padding-left: 14px;
    padding-right: 14px;
  }

  h1 {
    font-size: 24px;
  }
}
"""


def editor_template(nav: str) -> str:
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>設定ノート編集</title>
  <link rel="stylesheet" href="style.css">
  <style>
    main.editor-main {{
      max-width: 1080px;
    }}
    .editor-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 18px;
    }}
    .editor-panel {{
      min-width: 0;
    }}
    label {{
      display: block;
      font-weight: 700;
      margin: 14px 0 6px;
    }}
    input,
    textarea {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 12px;
      font: inherit;
      font-size: 16px;
      background: #fff;
      color: var(--ink);
    }}
    .quick-add {{
      border: 1px solid var(--line);
      background: #fff;
      border-radius: 12px;
      padding: 16px;
      margin: 20px 0 18px;
    }}
    .quick-add textarea {{
      min-height: 34vh;
      font-family: inherit;
      line-height: 1.8;
    }}
    textarea {{
      min-height: 62vh;
      resize: vertical;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 14px;
      line-height: 1.7;
    }}
    .editor-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 18px 0;
    }}
    button {{
      border: 0;
      border-radius: 8px;
      background: var(--accent-2);
      color: #fff;
      padding: 10px 14px;
      font: inherit;
      font-weight: 700;
    }}
    button.secondary {{
      background: #fff;
      color: var(--accent-2);
      border: 1px solid var(--line);
    }}
    .status {{
      min-height: 1.8em;
      color: var(--muted);
      white-space: pre-wrap;
    }}
    .preview {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 18px;
      min-height: 62vh;
      overflow: auto;
    }}
    .config {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 0 14px;
    }}
    .wide {{
      grid-column: 1 / -1;
    }}
    @media (max-width: 820px) {{
      .editor-grid,
      .config {{
        grid-template-columns: 1fr;
      }}
      textarea,
      .preview {{
        min-height: 48vh;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="site-title">リア ～春の風を運ぶもの～</div>
    <nav>{nav}
      <a href="editor.html">編集</a></nav>
  </header>
  <main class="editor-main">
    <h1>設定ノート編集</h1>
    <p>GitHub Contents APIで <code>docs/setting-notes.md</code> と <code>site/setting-notes.html</code> を更新するページ。</p>

    <section class="config">
      <div>
        <label for="owner">Owner</label>
        <input id="owner" autocomplete="username" placeholder="例: nm-nb">
      </div>
      <div>
        <label for="repo">Repo</label>
        <input id="repo" placeholder="例: okini-music-archive">
      </div>
      <div>
        <label for="branch">Branch</label>
        <input id="branch" value="main">
      </div>
      <div>
        <label for="basePath">Base path</label>
        <input id="basePath" value="lia">
      </div>
      <div class="wide">
        <label for="token">GitHub token</label>
        <input id="token" type="password" autocomplete="off" placeholder="Fine-grained token: Contents Read and write">
      </div>
    </section>

    <div class="editor-actions">
      <button type="button" id="load">GitHubから読み込み</button>
      <button type="button" id="save">GitHubへ保存</button>
      <button type="button" id="previewBtn" class="secondary">プレビュー更新</button>
      <button type="button" id="remember" class="secondary">設定だけ保存</button>
    </div>
    <div id="status" class="status"></div>

    <section class="quick-add">
      <h2>スマホ追記</h2>
      <p>ここに書いて保存すると、設定ノートの「最新メモ」に追記する。</p>
      <label for="appendTitle">見出し</label>
      <input id="appendTitle" placeholder="例: 第6話の姉妹名">
      <label for="appendText">追記内容</label>
      <textarea id="appendText" placeholder="ここに設定メモを書く"></textarea>
      <div class="editor-actions">
        <button type="button" id="appendSave">追記して保存</button>
      </div>
    </section>

    <section class="editor-grid">
      <div class="editor-panel">
        <label for="markdown">Markdown</label>
        <textarea id="markdown" spellcheck="false"></textarea>
      </div>
      <div class="editor-panel">
        <label>Preview</label>
        <div id="preview" class="preview"></div>
      </div>
    </section>
  </main>

  <script>
    const els = {{
      owner: document.getElementById('owner'),
      repo: document.getElementById('repo'),
      branch: document.getElementById('branch'),
      basePath: document.getElementById('basePath'),
      token: document.getElementById('token'),
      markdown: document.getElementById('markdown'),
      preview: document.getElementById('preview'),
      status: document.getElementById('status'),
      load: document.getElementById('load'),
      save: document.getElementById('save'),
      previewBtn: document.getElementById('previewBtn'),
      remember: document.getElementById('remember')
      , appendTitle: document.getElementById('appendTitle')
      , appendText: document.getElementById('appendText')
      , appendSave: document.getElementById('appendSave')
    }};

    let currentSha = null;

    function setStatus(message) {{
      els.status.textContent = message;
    }}

    function trimSlashes(value) {{
      return value.replace(/^\\/+|\\/+$/g, '');
    }}

    function config() {{
      const basePath = trimSlashes(els.basePath.value.trim());
      return {{
        owner: els.owner.value.trim(),
        repo: els.repo.value.trim(),
        branch: els.branch.value.trim() || 'main',
        token: els.token.value.trim(),
        basePath,
        mdPath: `${{basePath}}/docs/setting-notes.md`,
        htmlPath: `${{basePath}}/site/setting-notes.html`
      }};
    }}

    function apiUrl(path) {{
      const c = config();
      return `https://api.github.com/repos/${{encodeURIComponent(c.owner)}}/${{encodeURIComponent(c.repo)}}/contents/${{path}}?ref=${{encodeURIComponent(c.branch)}}`;
    }}

    function headers() {{
      const c = config();
      return {{
        'Accept': 'application/vnd.github+json',
        'Authorization': `Bearer ${{c.token}}`,
        'X-GitHub-Api-Version': '2022-11-28'
      }};
    }}

    function encodeBase64(text) {{
      const bytes = new TextEncoder().encode(text);
      let binary = '';
      for (const byte of bytes) binary += String.fromCharCode(byte);
      return btoa(binary);
    }}

    function decodeBase64(base64) {{
      const binary = atob(base64.replace(/\\n/g, ''));
      const bytes = Uint8Array.from(binary, ch => ch.charCodeAt(0));
      return new TextDecoder().decode(bytes);
    }}

    function escapeHtml(text) {{
      return text
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;');
    }}

    function inlineMarkup(text) {{
      return escapeHtml(text)
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>')
        .replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, (_, label, href) => {{
          let out = href;
          if (out === 'index.md') out = 'index.html';
          else if (out.endsWith('.md')) out = out.slice(0, -3) + '.html';
          return `<a href="${{escapeHtml(out)}}">${{escapeHtml(label)}}</a>`;
        }});
    }}

    function markdownToHtml(markdown) {{
      const lines = markdown.split(/\\r?\\n/);
      const out = [];
      let paragraph = [];
      let listOpen = false;
      let codeOpen = false;
      let code = [];

      function flushParagraph() {{
        if (paragraph.length) {{
          out.push(`<p>${{inlineMarkup(paragraph.join(' '))}}</p>`);
          paragraph = [];
        }}
      }}
      function closeList() {{
        if (listOpen) {{
          out.push('</ul>');
          listOpen = false;
        }}
      }}

      for (const raw of lines) {{
        const line = raw.trimEnd();
        if (line.startsWith('```')) {{
          flushParagraph();
          closeList();
          if (codeOpen) {{
            out.push(`<pre><code>${{escapeHtml(code.join('\\n'))}}</code></pre>`);
            code = [];
            codeOpen = false;
          }} else {{
            codeOpen = true;
          }}
          continue;
        }}
        if (codeOpen) {{
          code.push(raw);
          continue;
        }}
        if (!line.trim()) {{
          flushParagraph();
          closeList();
          continue;
        }}
        const heading = /^(#{{1,6}})\\s+(.+)$/.exec(line);
        if (heading) {{
          flushParagraph();
          closeList();
          const level = heading[1].length;
          out.push(`<h${{level}}>${{inlineMarkup(heading[2])}}</h${{level}}>`);
          continue;
        }}
        if (line.startsWith('- ')) {{
          flushParagraph();
          if (!listOpen) {{
            out.push('<ul>');
            listOpen = true;
          }}
          out.push(`<li>${{inlineMarkup(line.slice(2).trim())}}</li>`);
          continue;
        }}
        paragraph.push(line.trim());
      }}
      flushParagraph();
      closeList();
      return out.join('\\n');
    }}

    function settingNotesHtml(markdown, navHtml) {{
      return `<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>設定ノート</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <div class="site-title">リア ～春の風を運ぶもの～</div>
    <nav>${{navHtml}}
      <a href="editor.html">編集</a></nav>
  </header>
  <main>
    ${{markdownToHtml(markdown)}}
  </main>
</body>
</html>
`;
    }}

    function currentNavHtml() {{
      const nav = document.querySelector('nav');
      return Array.from(nav.querySelectorAll('a'))
        .filter(a => a.getAttribute('href') !== 'editor.html')
        .map(a => `<a href="${{a.getAttribute('href')}}">${{escapeHtml(a.textContent)}}<\\/a>`)
        .join('\\n      ');
    }}

    async function getContent(path) {{
      const res = await fetch(apiUrl(path), {{ headers: headers() }});
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || `GitHub API error: ${{res.status}}`);
      return data;
    }}

    async function putContent(path, content, sha, message) {{
      const c = config();
      const body = {{
        message,
        content: encodeBase64(content),
        branch: c.branch
      }};
      if (sha) body.sha = sha;
      const res = await fetch(apiUrl(path).replace(/\\?ref=.*/, ''), {{
        method: 'PUT',
        headers: {{ ...headers(), 'Content-Type': 'application/json' }},
        body: JSON.stringify(body)
      }});
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || `GitHub API error: ${{res.status}}`);
      return data.content.sha;
    }}

    async function loadMarkdown() {{
      try {{
        const c = config();
        if (!c.owner || !c.repo || !c.token) throw new Error('Owner / Repo / token を入力してください。');
        setStatus('読み込み中...');
        const data = await getContent(c.mdPath);
        currentSha = data.sha;
        els.markdown.value = decodeBase64(data.content);
        updatePreview();
        saveLocalConfig(false);
        setStatus('読み込みました。');
      }} catch (error) {{
        setStatus(`読み込み失敗: ${{error.message}}`);
      }}
    }}

    async function saveMarkdown() {{
      try {{
        const c = config();
        if (!c.owner || !c.repo || !c.token) throw new Error('Owner / Repo / token を入力してください。');
        setStatus('保存中...');

        const mdData = await getContent(c.mdPath);
        currentSha = mdData.sha;
        await putContent(c.mdPath, els.markdown.value, currentSha, 'Update Lia setting notes');

        let htmlSha = null;
        try {{
          htmlSha = (await getContent(c.htmlPath)).sha;
        }} catch (_) {{
          htmlSha = null;
        }}
        const html = settingNotesHtml(els.markdown.value, currentNavHtml());
        await putContent(c.htmlPath, html, htmlSha, 'Update Lia setting notes page');

        updatePreview();
        saveLocalConfig(false);
        setStatus('保存しました。公開ページへの反映には少し時間がかかる場合があります。');
      }} catch (error) {{
        setStatus(`保存失敗: ${{error.message}}`);
      }}
    }}

    function makeAppendBlock(title, text) {{
      const now = new Date();
      const yyyy = now.getFullYear();
      const mm = String(now.getMonth() + 1).padStart(2, '0');
      const dd = String(now.getDate()).padStart(2, '0');
      const hh = String(now.getHours()).padStart(2, '0');
      const mi = String(now.getMinutes()).padStart(2, '0');
      const heading = title ? `#### ${{title}}` : `#### 追記 ${{yyyy}}-${{mm}}-${{dd}} ${{hh}}:${{mi}}`;
      return `${{heading}}\\n\\n${{text.trim()}}\\n`;
    }}

    function insertLatestMemo(markdown, block) {{
      const marker = '### 最新メモ';
      const index = markdown.indexOf(marker);
      if (index < 0) {{
        return `${{markdown.trimEnd()}}\\n\\n## 追記メモ\\n\\n${{block}}\\n`;
      }}
      const afterMarker = index + marker.length;
      const nextHeading = markdown.indexOf('\\n### ', afterMarker);
      if (nextHeading < 0) {{
        return `${{markdown.slice(0, afterMarker)}}\\n\\n${{block}}\\n${{markdown.slice(afterMarker).trimStart()}}`;
      }}
      return `${{markdown.slice(0, afterMarker)}}\\n\\n${{block}}\\n${{markdown.slice(afterMarker, nextHeading).trimStart()}}${{markdown.slice(nextHeading)}}`;
    }}

    async function appendAndSave() {{
      try {{
        const c = config();
        const text = els.appendText.value.trim();
        if (!c.owner || !c.repo || !c.token) throw new Error('Owner / Repo / token を入力してください。');
        if (!text) throw new Error('追記内容を入力してください。');
        setStatus('追記保存中...');

        const mdData = await getContent(c.mdPath);
        const current = decodeBase64(mdData.content);
        const block = makeAppendBlock(els.appendTitle.value.trim(), text);
        const nextMarkdown = insertLatestMemo(current, block);
        await putContent(c.mdPath, nextMarkdown, mdData.sha, 'Append Lia setting note');

        let htmlSha = null;
        try {{
          htmlSha = (await getContent(c.htmlPath)).sha;
        }} catch (_) {{
          htmlSha = null;
        }}
        const html = settingNotesHtml(nextMarkdown, currentNavHtml());
        await putContent(c.htmlPath, html, htmlSha, 'Update Lia setting notes page');

        els.markdown.value = nextMarkdown;
        els.appendText.value = '';
        updatePreview();
        saveLocalConfig(false);
        setStatus('追記して保存しました。公開ページへの反映には少し時間がかかる場合があります。');
      }} catch (error) {{
        setStatus(`追記保存失敗: ${{error.message}}`);
      }}
    }}

    function updatePreview() {{
      els.preview.innerHTML = markdownToHtml(els.markdown.value);
    }}

    function saveLocalConfig(showStatus = true) {{
      const c = config();
      localStorage.setItem('liaEditorConfig', JSON.stringify({{
        owner: c.owner,
        repo: c.repo,
        branch: c.branch,
        basePath: c.basePath
      }}));
      sessionStorage.setItem('liaEditorToken', c.token);
      if (showStatus) setStatus('設定を保存しました。tokenはこのブラウザのセッション内だけに保存します。');
    }}

    function loadLocalConfig() {{
      try {{
        const saved = JSON.parse(localStorage.getItem('liaEditorConfig') || '{{}}');
        els.owner.value = saved.owner || '';
        els.repo.value = saved.repo || '';
        els.branch.value = saved.branch || 'main';
        els.basePath.value = saved.basePath || 'lia';
        els.token.value = sessionStorage.getItem('liaEditorToken') || '';
      }} catch (_) {{
        els.branch.value = 'main';
        els.basePath.value = 'リア';
      }}
    }}

    els.load.addEventListener('click', loadMarkdown);
    els.save.addEventListener('click', saveMarkdown);
    els.appendSave.addEventListener('click', appendAndSave);
    els.previewBtn.addEventListener('click', updatePreview);
    els.remember.addEventListener('click', () => saveLocalConfig(true));
    els.markdown.addEventListener('input', () => {{
      clearTimeout(window.previewTimer);
      window.previewTimer = setTimeout(updatePreview, 300);
    }});

    loadLocalConfig();
    updatePreview();
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
