# v2 子任务 A「内容与隐私」报告（2026-10-08）

依据：`docs/TODO.md`「v2 改版」一节（唯一事实源）。本报告**不写**现任雇主名、真名、旧时间线与城市名——
本仓库是公开的，写进来就等于公开了。按主会话要求，本轮**没有改** `docs/TODO.md` / `docs/DONE.md`（另一子任务并行，由主会话汇总）。

## 结论

| 项 | 改前 | 改后 |
|---|---|---|
| about 正文词数（构建产物 `<article class="entry-content">`） | 564 | **201**（介绍段 150） |
| `app/src/migrated/about.html` | 72 行 / 5639 字节 | 16 行 / 1964 字节 |
| about 里的起止年月 | 7 个 | **0** |
| `app/src` 里的旧 Gmail | 7 处（5 个文件 6 行） | **0** |
| AI system prompt 里的 about 文本 | 4088 字符，被 `slice(0, 4000)` 截在 "ACA" 中间——三项 ACAA 认证模型一项也看不到 | **全文 1357 字符**，不截断 |
| 构建 | 通过 | 通过 |

## 做了什么、为什么

1. **先备份，再动 about**。改前的 about.html 原样快照进私有仓库 `zosc-career`（本地 git，无 remote，未 push）：
   逐字节拷贝的 `.html`（sha256 与源文件一致）+ 可读 `.md`（与 HTML 逐词比对一致，含全部职责条目与年月）+
   RESUME.md 末尾加一节指向它们，说明「公开站已压缩，完整履历以此为准」。私有仓库提交 `6de2bad`（快照）、`fe704e4`（禁词表，见第 5 条）。
   理由：详细履历的归宿是 PDF 简历，不是公开站（TODO「备份」一行）。

2. **about 压成一段话 + 技能一行 + 认证一行 + 联系方式**（`app/src/migrated/about.html`）。
   - 介绍段 150 词：身份（motion designer, visual artist & developer，建动效体系并把体系落成工具链）+ 10+ 年 +
     四个雇主锚点，各一句短语级上下文：**vivo**（MR 智能眼镜动效框架 0→1）、**JMGO**（旗舰 OS 动效框架 0→1）、
     **China Mobile**（展厅投影映射合成）、**Galanz**（官方商城 UI 与动效重做）。雇主名保留，它们是 Google 实体锚点。
   - 拿掉：Highlights / Experience 下全部逐条职责、全部起止年月、"Present"、年度员工/绩效评级、
     JMGO 后面括号里带城市名的公司全称（属于"所在地描述"）。
   - 措辞刻意**不排先后、不用现在时**（没有 "most recently / currently at"），避免读者推出在职时间线或误以为某家是现任。
   - 每句话都能在快照原文里找到出处；没有从私有简历里搬任何表述。
   - 技能压成一行（去掉版本号、Particle System、调参、沟通等次要项）；认证一行（三项 ACAA）；
     联系方式 Email `hi@zosc.com` / Behance / GitHub / **X（新增）**，沿用模板已有的 `.contact-list` 样式。
   - 名字一律小写 `zosc`。正文直接用 Unicode 字符（’ — ·），不再用 `&rsquo;` 之类实体（原因见第 4 条）。
   - `app/src/pages/about/index.astro`（模板、样式、meta description）**未改**；description 里本来就没有年份和地点。

3. **对外邮箱统一 `hi@zosc.com`**：Footer（mailto）、about、`knowledge.ts` CONTACT、`chat.ts` 两条文案
   （当日限额、出错兜底）、AskAI 面板底部提示。`app/public` 里本来就没有旧 Gmail。

4. **AI 问答只读短版**（`app/src/lib/knowledge.ts`，无新环境变量、无第二份履历文本）：
   - 短版全文 1357 字符，远低于 4000 上限，`slice` 保留只作保险。改前（HEAD 版）长版抽出来是
     4088 字符，最后 88 个字符被截掉，模型只看到 "Certifications Awards ACA"，三项认证全丢——压缩顺带修掉了这个问题。
   - 修了 `stripHtml` 两个旧问题：① 行内标签被替换成空格，模型看到的是 `vivo ’s`、`JMGO ’s`；
     ② 所有实体都被替换成空格，`&amp;`、破折号全部丢失。现在行内标签直接删除、常用实体还原成字符。
   - 第一句里改名遗留的 "zosc (also known as zosc)" 改成 "zosc, a motion designer, visual artist & developer"。
   - CONTACT 行带上三个 profile 的完整 URL（以前模型只看到 `@zosc` 这样的 handle，可能自己拼链接）。
   - 新增一行 **PRIVACY**：所在地、现任雇主、在职时间与其他个人信息不公开，不许说、也不许从页面上的公司名推测；
     被问到就说不在这里公开、建议发邮件。理由是把 TODO「AI 问答」一行的逻辑（"AI 一问就背等于只防 Google 没防人"）
     再往前推一步：长版已经不喂给 AI 了，但模型仍可能从页面上的公司名自己推出所在地或"现任"，所以明确禁止。
     **此条超出"邮箱统一"的字面范围，见下方待拍板 2。**

5. **新增 `tools/check-about.mjs`**：可重复跑的校验（年份 / 通用禁词 / 引用完整性 / 词数 / AI prompt 实抓）。
   AI 那一项是直接 import **构建产物**里的 `/api/chat` handler，把 `fetch` 换成桩、用假 key，
   抓到模型实际会收到的 system prompt——测的是真正上线的代码，不是重写一遍逻辑。不联网，什么也不发出去。
   现任雇主名、城市名、真名**故意不写进这个脚本**（公开仓库里的禁词表等于公开这些词）：
   它们放在私有仓库的一行正则里，用 `--private-deny <文件>` 传入，输出只有命中次数。

## 校验（命令与输出）

全部在本 worktree 跑，构建产物为最终版本。

```
$ cd app && npm run build
...
[build] Complete!
[patch-vercel-redirects] patched 24 redirect routes            → exit 0

# 主会话指定的隐私 grep（5 个文件）。<现任雇主 4 个写法> 是主会话 prompt 里的原词，故意不写进公开仓库
$ grep -rniE "zcbgood|zerb|<现任雇主 4 个写法>|china-based|mainland" \
    app/src/migrated/about.html app/src/lib/knowledge.ts app/src/components/Footer.astro \
    app/src/components/AskAI.astro app/src/pages/api/chat.ts
(无输出)                                                        → exit 1 = 0 条

$ grep -oE "\b20[12][0-9]\b" app/src/migrated/about.html
(无输出)                                                        → exit 1 = 0 条

$ grep -rn zcbgood app/src
(无输出)                                                        → exit 1 = 0 条

# 加测：同一组词（含现任雇主 4 个写法）扫构建产物（静态页 + 服务端函数包，排除 node_modules）
$ grep -rIl "zcbgood" app/dist app/.vercel/output --exclude-dir=node_modules       → 0 个文件
$ grep -rIliE "<现任雇主 4 个写法>|china-based|mainland|国内" app/dist app/.vercel/output \
    --exclude-dir=node_modules                                                       → 0 个文件

$ node tools/check-about.mjs --before <git show HEAD:app/src/migrated/about.html 的导出> \
    --private-deny /data/Projects/zosc-career/tools/public-denylist.txt
1. years in about.html
  ok   0 matches for \b20[12][0-9]\b
2. generic deny-list in about.html
  ok   0 matches for /zcbgood|zerb|china-based|mainland|国内/gi
  ok   about.html: 0 private-term matches (--private-deny)
  ok   name only appears lowercase (no ZOSC / Zosc)
3. reference integrity
  ok   about.html has 0 root-relative src/href (only mailto: and https:// links)
  ok   built about page: 13/13 root-relative references resolve to real files
  ok   built about page (whole HTML incl. header/footer/JSON-LD): 0 private-term matches
4. word count (built about article)
  built article: 201 words  (source fragment: 201; must match since set:html injects it verbatim)
  intro paragraph (.lead): 150 words  (target ~120–180)
  ok   article word count within 120–260
  before (about-before-HEAD.html): 564 words  →  after: 201 words
5. AI system prompt (built /api/chat, fetch stubbed, fake key)
  ok   handler streamed the stub reply (status 200, body "stub-ok")
  provider host: generativelanguage.googleapis.com (stubbed)   system prompt: 4545 chars
  about text inside prompt: 1357 chars (slice cap 4000)
  ok   about text in prompt == full about.html text (nothing truncated or dropped)
  ok   contact hi@zosc.com present
  ok   no old Gmail in prompt
  ok   no tag-gap artifacts (" ’s")
  ok   AI system prompt (incl. all project summaries + blog list): 0 private-term matches
RESULT: PASS
```

`--private-deny` 指向私有仓库里的一行正则（现任雇主 4 个写法 + 旧 about 里出现过的城市名 + 真名），脚本只打印命中次数，
不打印词本身，所以上面的输出可以放进公开仓库。阳性对照：换成一个确实存在的词，三处扫描全部 FAIL（1 / 4 / 4 次），exit 1。

引用完整性那 13 条不是空转：11 个真实文件（Layout CSS、两个 JS、两个字体、favicon.ico/svg、三个 zosc-mark PNG、
页头 logo）+ 2 个页面路由（`/`、`/about/`），逐条确认存在。about.html 本身只有 `mailto:` 和 `https://` 链接。

词数口径：空白分隔、且至少含一个字母或数字的 token 算一个词（`—` `·` 分隔符不算，`hi@zosc.com`、`C#`、`10+` 算）。
构建产物里的 article 与源 about.html 计数相同（201 = 201），因为 `set:html` 原样注入；所以"改前 564"直接用 HEAD 版 about.html 计。

本地静态预览（`python3 -m http.server` 起 `app/dist/client`，无头 chromium）：
- 截图 1440 宽与 390 宽 @2x 已看过，联系方式行在手机上折成两行，样式全部来自模板现有 CSS。截图在会话 scratchpad，未入库。
- 横向溢出是**实测**的，不是看截图（截图隐藏了滚动条，看不出来）：同源页面用 iframe 加载 `/about/` 量 `scrollWidth`。

```
390 宽 ：docScrollWidth 380 = docClientWidth 380（差的 10px 是 iframe 自己的竖滚动条）；.entry-content 内元素 x 24–356
1440 宽：docScrollWidth 1430 = docClientWidth 1430；.entry-content 内元素 x 331–1099（max-w-3xl = 768px）
.lead 字号 21.6px（模板 1.35rem），两种宽度一致
```

预览环境看不到动效（AGENTS.md「预览环境的真实局限」），about 页本轮也没碰任何动效；交互与视觉最终以 Vercel 预览实测为准。

## 待拍板

1. **介绍段整段用了 `.lead` 大字号。** 桌面好看；手机上大约 30 行大字，偏重。三个选项：
   保持 / 首句 `.lead` + 其余正文字号（会变成两段，与"一段话"的字面略有出入）/ 整段正文字号。改起来就是一个 class。
2. **`knowledge.ts` 的 PRIVACY 一行**是我加的（不在"邮箱统一"字面里，但属于本子任务的隐私范围）。不要就删那一行。
3. **about 联系方式新增了 X**（主会话 prompt 列了它）；Steam / Blog 没加，Footer 里已有。

## 范围外发现（都没改）

- `app/src/components/Header.astro` 页头 logo 文件叫 `zerb-logo.png`。图片 URL 爬虫看得到；但改名是改媒体文件，
  按"不删媒体、改引用必校验"的规则留给专门处理。
- `app/src/layouts/Layout.astro` JSON-LD 的 `alternateName` 含 ZERB 系列：这是**刻意**保留的旧身份关联，不是遗漏。
- `knowledge.ts` 的 THREE PILLARS 仍是 Motion / Visual / Code 顺序；Layout 默认 title 仍是 `zosc — Motion · Visual · Code`。
  v2 定了 Code 优先，属子任务 C。
- `AGENTS.md` 文档规则只列了 README / AGENTS / TODO / DONE 四个 md；`docs/v2/` 是按主会话要求新建的，
  汇总进 DONE.md 后是否保留，由主会话决定。
