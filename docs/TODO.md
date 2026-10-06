# TODO.md

## 当前目标

- 线上站 = `zosc.com`（Astro / Vercel / Cloudflare 橙云）。`zerb.net` 已是**纯 301 转发域名**，
  至少再续一年（301 必须持续有效，GSC 地址更改要靠它）。
- **SEO 主线：拿下裸词 `zosc` 的搜索结果。** 现状有利——该词没有任何竞争实体，
  占着首页的只是几个 Open Sound Control 技术文档页（GitHub 小库、Ubuntu manpage）和一个大学课程代码
  `ZOSC 312`，**没有知识图谱实体**。这和 `zerb` 被一位巴西 DJ 占着是完全不同的局面。
  可达目标：**第一名 + 知识面板 + 首页 3–5 个位置**；拿不到的是 ubuntu.com / github.com 上那些页面，
  它们域名权重太高，会在第一页待很多年——**但不影响首屏全是你**。
- 内容：12 个项目详情页正文已补齐；`zosc.com` 后续计划改造成**导航页**，索引到各个作品
  （motionrules、MotionPilot、makerlion 等），不再只是个人简介页。

## 2026-10-06 迁移已完成，验收全绿

```
GSC 地址更改             2026-10-06 已提交（zerb.net → zosc.com），约 180 天迁移窗口
zosc.com/                200  title "zosc — Motion · Visual · Code"  canonical=zosc.com
zerb.net/*               301 → zosc.com/*  逐页保留路径
sitemap-index.xml        200  application/xml  15 个 URL 全新域名
favicon svg/ico/png      200  已换成 Z 标
hi@zosc.com + catch-all  → zcbgood@gmail.com
blog.zosc.com            HTTPS 200，证书 approved，Enforce HTTPS 已开
GitHub                   byzosc；profile README 仓库已改名为 byzosc
```

详细做法、七个踩过的坑、受保护不可替换的字符串清单，见 `docs/DONE.md` 2026-10-06 条目。

## 待办

### sameAs 五条（2026-10-06 全部实测 200）
```
github.com/byzosc · x.com/byzosc · behance.net/zosc
steamcommunity.com/id/byzosc · blog.zosc.com
```
**改任何一个平台的 handle，必须同步改 `app/src/layouts/Layout.astro` 的 sameAs 和
`app/src/components/Footer.astro`——死的 sameAs 比没有更糟，会破坏 Google 的实体聚合。**

### 需要用户操作（无 API 通道）
- [ ] ~~改 Mac DNS~~ 已撤销：zosc.com 打不开只是 NS 切换的正常传播，
      最晚 2026-10-08 16:26 SGT 自愈，无需任何操作。详见 DONE.md 2026-10-07
- [ ] 发一封测试信到 `hi@zosc.com` 确认转发（本机无 MTA / 无 SMTP 凭据，发不了）

### 可做
- [ ] `zosc.com` 改造成导航页（用户方向，尚未开工）
- [ ] 子域名服务迁移：`clip` / `img` / `hub` / `drop` 仍挂在 `zerb.net` 下，
      若将来卖掉 zerb.net 必须先迁走（用户说今年慢慢做）
- [ ] 项目 `.md` 补 `year` 字段（featured 叠层不显示年份）

### 凭据（本会话已配置，存在本机）
```
~/.config/cloudflare/token   Zone·DNS·Edit + Zone·Email Routing Rules + Account·Email Routing Addresses
                             （「启用 Email Routing」那个端点不在任何一条里，但不影响——
                               启用的实质是写规则 + 加 MX，都能用 API 做）
~/.config/vercel/token       全账号权限；team = zerbs-projects (team_uL4RMxYBszxow0z3ELSHmi4M)
gh                           已登录 byzosc
```
Cloudflare account_id `f2f3c33a954d9e68ea2005b021c54c67`，后台直达 URL 可按
`https://dash.cloudflare.com/<account_id>/<域名>/<页面>` 拼。

## 正在处理

**Astro 重建版已上线，`app/` 是站点唯一实现**（根目录 WordPress 静态导出已于 2026-07-04 删除，git 历史可找回）：

- 线上地址：**`https://zerb.net`**（Vercel 项目 `net-website-mu.vercel.app`，Root Directory = `app`，生产分支 `main`，push main 即部署）。zerb.net 的 DNS 在 Cloudflare：橙云（已代理）+ 缓存，SSL 用 Full/Full(strict)。
- 改 `app/` 前**必读 `AGENTS.md`「Astro 重建版工作规则」**（架构 + View Transitions/遮罩/Lenis/光标/预览环境等踩坑总结）。
- 视频在 Cloudflare R2（`zerbnet-media`，公共域名 r2.dev）；图片在 `app/public/media/images`；字体自托管（Montserrat 标题 + Mulish 正文）；AI 问答 `/api/chat` 多 provider（Gemini key 在 Vercel 环境变量）。
- 站内中文已全部翻成英文（项目正文/博客/标题）。
- 首页 = Hero 三段进场（蒙版/模糊/打字）+ 三板块 featured-first 网格 + 「AI Ask」内联引导块（复用侧边栏）。

### 当前待办 / 待用户决定

- **AI 限流（可选，用户操作）**：限流器支持 Upstash Redis（REST）跨实例共享计数（`app/src/lib/ratelimit.ts`），未配置时自动回退内存版、Redis 出错时 fail-open 不影响问答。激活只差一步：在 https://upstash.com 建免费 Redis → 把 `UPSTASH_REDIS_REST_URL` / `UPSTASH_REDIS_REST_TOKEN`（或 Vercel KV 的 `KV_REST_API_URL` / `KV_REST_API_TOKEN`）加到 Vercel 环境变量并重新部署。限流本身已在生产生效（2026-06-22 实测 per-min=5、全站 cap=200），Upstash 仅为跨实例共享计数。
- **媒体高清**：Motion 的 featured（VIVO XR / GLASS）只有 950px 源图，全宽横幅略糊；想清晰需用户给 ≥1600px 高清横图。其余 featured 已用高清源（dynamic-weather 用 1920px）。
- **项目 `year` 未填**：所有 `app/src/content/projects/*.md` 都没填 `year`，featured 叠层不显示年份——要显示就补。
- **Code 板块**：目前只有 MotionSheet 一个作品，是否补内容待定。
- **可选打磨**：详情页正文（`app/src/project-bodies/*.html`）部分仍含 WordPress 导出的冗余 class/空块，可逐页清理；桌面 featured 卡片高度可再微调（现 ~3.7:1）。
- **R2 自定义域名（可选）**：r2.dev 有速率限制，可换 `media.zerb.net` + Cloudflare CDN，只需改 `.env` 的 `R2_PUBLIC_BASE` 重跑 `npm run media:manifest && npm run media:apply`。
- **国内访问再加速（可选）**：现橙云 + 缓存后国内可正常访问；要更快才需国内 CDN/备案。
- **跨项目依赖（2026-07-28 记）**：新站 `makerlion.com`（仓库 `/data/Projects/makerlion`，GitHub `zerbLion/makerlion`，部署 Vercel）**未来唯一可能从本项目移植的东西就是 AI 问答能力**——`app/src/pages/api/chat.ts` + `app/src/lib/{providers,knowledge,ratelimit}.ts` + `app/src/components/AskAI.astro`。现在不做。**大改这几个文件时顺手想一下可移植性**（尤其别把知识库逻辑和作品集内容耦合死）。makerlion 侧的评估写在该仓库 `docs/TODO.md`。

更早的历史（Astro 重构 Phase 1-5、2026-07-04 根目录清理与 SEO 修正、2026-06-08 媒体优化等）见 `docs/DONE.md`。

## 未完成事项

- SEO 双线作战计划（2026-07-04 定，目标：`zerblion` 通吃 + 长期抢下 `zerb`，两线共用同一实体/内容/外链）——**⚠️ 已被 2026-09-03 更名决定取代，下列仅存档；更名落地后按 zezr 重写**：
  - **第 0 阶段（用户）**：GSC 确认域名级资源 + sitemap 状态"成功"；GitHub/X/blog 签名统一 `ZERB (zerblion) — zerb.net`。站内技术项（schema/重定向/sitemap）2026-07-04 已完成。
  - **第 1 阶段（内容冲刺）**：12 个项目详情页正文已于 2026-07-05 全部补齐；剩余顺手项：项目 `.md` 补 `year`；blog 用 "ZERB" 锚文本链回 zerb.net；个别页可继续加深。
  - **第 2 阶段（1-3 月，外部权重，攻 zerb 的关键）**：Behance/Dribbble/ArtStation/站酷建档（名字 ZERB、链 zerb.net）；投 Awwwards/CSSDA/siteInspire；每月初看 GSC 查询报告（zerb/zerblion/zerb lion 趋势）。
  - **检查点**：2 周 → zerblion 第一、索引 ≥13 页；1-2 月 → zerb lion 第一、zerb 进第一页；3-6 月 → zerb 前三。

## 已知问题

- 详情页正文（`app/src/project-bodies/*.html`）和 `app/src/migrated/about.html` 部分仍是 WordPress 导出的长行压缩 HTML（含冗余 class），大段 patch 风险较高，改动要小步、改完浏览器验证。
- Motion featured（VIVO XR / GLASS）无 ≥1600px 高清源，全宽横幅略糊（见待办）。
- GSC 有 15 页"已发现/已抓取-尚未编入索引"，属新站正常，等消化，月度复查即可。

## 下一步

1. 先阅读 `README.md`、`AGENTS.md`（改 `app/` 必读「Astro 重建版工作规则」）、`docs/TODO.md`、`docs/DONE.md`。
2. 本地开发：

```bash
cd app
npm install   # 首次
npm run dev   # http://localhost:4321/
```

3. 检查首页、`works/`、`about/`、关键 `project/` 页面；涉及导航、滚动、hover 等动效时先对照线上原效果，再小范围改动。
4. 上线前构建验证：`cd app && npm run build`（构建内含 `patch-vercel-redirects.mjs` 重定向后处理）。
5. 媒体：图片放 `app/public/media/images/...`；视频走 R2——根目录 `npm run media:upload` 上传、`npm run media:manifest && npm run media:apply` 更新引用（需 `.env` 里的 R2 凭据）。
6. 改完 commit 并 push `main`（生产分支，push 即触发 Vercel 部署）。
7. 文档只维护 `README.md`、`AGENTS.md`、`docs/TODO.md`、`docs/DONE.md`，不要新增分散状态文件。

## 注意事项

- 删除资源前必须确认没有页面/组件引用。
- 改写媒体路径后必须用浏览器验证，不要只依赖文本扫描。
- 不要过度压缩作品集图片。
- 不要创建或使用 `MIGRATION_NOTES.md`、`TASK_STATE.md`、`CHANGELOG.md`、`WEB_STATE.md`、`WEB_LOG.md`、`WEB_TODO.md`、`WEB_DONE.md`。
- 修改业务代码前先说明计划；复杂修改不要直接大改。
- 修改已有动效前必须先对照原效果，不要新增用户没有要求的折叠、隐藏或布局位移。
