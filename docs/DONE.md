## 2026-10-09 about 页邮箱显示 [email protected]（main 7da0e16）

Cloudflare 的 Email Address Obfuscation 会把页面里的邮箱改写成 `[email protected]` 占位 + `/cdn-cgi/l/email-protection` 链接，
靠它注入的解码脚本在浏览器里还原；本站用 `<ClientRouter />` 无刷新切页，脚本常不执行，about 页就露出占位。
本机 Cloudflare token **没有 Zone Settings 权限**（PATCH `settings/email_obfuscation` 返回 10000），所以改用 Cloudflare 认可的
`<!--email_off-->…<!--/email_off-->` 标记包住 Layout 的 body。线上验证：about 页明文 `hi@zosc.com` 4 处、mailto 2 处、占位与 cdn-cgi 链接 0。
**以后加任何显示邮箱的位置都在 body 内，自动受保护；不要把邮箱放进 `<head>`。**

## 2026-10-09 10:36 SGT v3-G/H 上线 + Google 缩略图根因修复（main 83407a6）

**合并**：v3-G（删产品条，Code 板块即 PRODUCTS，三张大卡下一行小字直达链接，Motion 上挂 WORK 眉题）、
v3-H（默认分享卡 og-default.png 1200×630 纯黑底；旧 og 图上其实写着 ZERB，一并去掉）。
与 Codex 同期提交（页脚删 MakerLion `c8a4fa1`、logo 原型归档暂停 `f505610`）无冲突，页脚删除保留。

**Google 搜索结果右侧灰边大 Z —— 根因已查实并修复**：
- 不是 og:image，是**页头 `<img>` logo**（zosc-logo.png，672×546，透明底）。首页 13 张图里只有它比例 1.231 与截图缩略图 1.227 吻合。
  Google 把非方图等比塞进方框补灰条，透明处填黑。
- Google 文档原文（developers.google.com/search/docs/appearance/google-images）：**内联 SVG 与 CSS 背景图不被索引为图片**；
  首选图三种声明方式 primaryImageOfPage / mainEntity.image / og:image；首选图要求「代表页面、**不要 logo、不要带字**、不要极端比例、高分辨率」。
- 修法：① 页头 logo 改**内联 SVG**（同 favicon.svg 路径，视觉不变）；② 首页 og:image + `WebPage.primaryImageOfPage`
  指向 `home-thumb.jpg`（dynamic-weather-art 1080×1080 居中裁切，不透明、无字）；③ og-default 品牌卡留给其他页面做社交分享卡。
- 线上验证：页头 `<img>` 0 个；首页 JSON-LD = Organization / Person / WebPage / WebSite；about 等页仍用 og-default。
- **生效要等 Google 重抓首页**（缩略图跟网页爬虫，比 favicon 快）。若重抓后仍不显示新图：Google 可能选择不显示缩略图，这也比灰边 Z 好。

**favicon（Astro A）根因**：站内无遗漏。Googlebot UA 经 Cloudflare 取到的全部是 Z（四个入口 md5 一致）。
Google 图标服务 `faviconV2?url=https://zosc.com` 仍是 10-06 的 Astro 旧记录，而 `?url=https://www.zosc.com`（新抓）已是 Z。
只能等 Google 图标爬虫轮到这条；复查命令见 `docs/v3/HANDOFF-2026-10-08-night.md`。

**其他**：Code 板块底部 `View all work →` → `View all products →`；大卡标题到直达行 57px 保持（G 的理由：叠到图上会破坏 hover 与入场）。
check-home 同步三条断言（页头必须内联 SVG、首页 og 用 home-thumb、首页 4 个 JSON-LD 块）；check-projects / check-about / check-motion 全过。
clip：PRODUCTS 板块 `v9tcsn2e1k` · 手机整页 `emx878std1` · 缩略图 `hkcfax20gq`。

## 2026-10-08 移除共享页尾 MakerLion

- 对照线上现状，最底部实际为 MakerLion 文字链接；按用户要求删除整项，所有使用共享 Footer 的页面一致生效。
  未删除媒体资源，其他页尾链接和品牌/动效保留。
- `npm run build` 与 `tools/check-home.py` 通过，23 页页尾只剩 X/GitHub/Steam/Blog/MotionRules/Cubby/Email。
- Chromium 桌面/手机页尾截图坏图 0、横向溢出 0；Hero 与真实点击导航/跨页锚点检查通过。
- 移动菜单 toggle/Esc/背景/导航后关闭、Ask AI 跨页后打开与关闭、works 四种筛选通过；
  headless 未提供 fine pointer，光标 hover/标签/复位以模拟 fine-pointer 条件检查。
- clip 桌面 `5fbdt7pyxk`、手机 `7x3aqtysz0`，上传读回哈希一致。
- 浏览器逐页复核 23 页 HTTP 200、坏图 0、页尾无 MakerLion。代码发布 `c8a4fa1`，
  生产部署 `dpl_F4QJioBkJDVgzWvAfxJ5hMA3qppn` READY；常规线上 URL（未加缓存绕过参数）
  首页、about、works、cubby 均返回新页尾且为 200。

## 2026-10-08 oscillator 工作暂停与原型归档

- 用户明确要求「先不做这个动效了」。停止继续制作和接入；第二/第三稿及原 Claude 原型保留为归档。
- 本地原型与评审文档收尾归档，不替换线上 logo 或 favicon。品牌首页 v3 已由另一会话合并上线
  （`5ea1709`，本轮开始时 main 为 `faacce6`）；下方原型条目中的「未合并 F」描述对应此前时点。

## 2026-10-08 oscillator 第三稿：波形生成字形（随后暂停）

- 第二稿被用户否决：造型太丑，未表达 oscillator。停止将「整字振荡」作为下一稿方向。
- 新增独立 `lab/zosc-signal/`：连续周期性正弦分成三个弧段，O 卷合，S/C 转向后变成字形；
  静态 O 内保留橙色正弦作为信号源线索。动态 2.52 秒后停止，减少动态偏好直接显示静态。
- 调整转向位置与缩放，避免 S/C 在中途相碰；采样变形后重建平滑 Bezier 曲线，避免密集折线接缝。
  保留独立 SVG、可切换概念板/动画/页头的页面与随机端口截图导出器；README 更新当前预览路径。
- Chromium 实际 rAF 播放后所有路径准确回到终态，减少动态模式检查通过，Runtime exception 为 0；
  检查起振、变形、终态静帧及桌面/手机落位。导出 GIF/MP4 25fps，总长 6 秒含静态停留。
- clip：GIF `3erc472sw3`，MP4 `6m4fkcjzkp`，概念板 `9nanmzg93y`；
  桌面页头 `g4ydzmyxsc`；手机页头 `ryem586c5h`。视频实测 1200×676、25fps、150 帧、6 秒。
  上传后读回核对 SHA-256、MIME 与大小。原型仍待用户评价，未改 `app/`/favicon/原 Claude 原型，
  未合并 v3-F 或触发生产部署。

## 2026-10-08 Codex zosc 字标第二稿与 clip 预览（随后被用户否决）

- 按用户「做完放 clip」的要求，新增 `lab/zosc-wordmark/`：原生 SVG 定制横向字标、
  1.04 秒衰减振荡、黑白/小尺寸展示、桌面与手机页头落位图。
  动态直接变形 Bezier 控制点，保留圆滑路径；结束恢复原始路径，减少动态偏好直接显示静态。
- `record.mjs` 用随机端口与独立 Chromium 进程导出截图和 25fps 预览，关闭时仅结束自己的进程；
  产物留在忽略的 `.render-tmp/zosc-wordmark/`。README 已补独立预览与导出方式。
- 验证：实际 rAF 播放归位、减少动态模式、无 Runtime exception；检查静帧与桌面/手机截图。
  GIF/MP4 均为 4.2 秒（含静态停留），GIF 循环仅用于预览，网页默认播放一次。
- clip 上传且读回校验 SHA-256/MIME/大小：静态板 `8jv486b3n5`，桌面页头 `56j7f0hsaq`，
  手机页头 `p4gc4pbcf8`，MP4 `15ck4dywmj`，GIF `05hjcnr7cx`。
- 本轮只交付独立设计稿；未替换线上字标或 favicon，未修改原 Claude 动效原型，未合并 v3-F。

## 2026-10-08 15:16 SGT v2 改版上线（main 3e5ce5f）

**线上实测（直连 IP 绕过本机解析）**：
```
title           zosc — Code · Motion · Visual
板块顺序        #code → #motion → #visual；Code 板块 3 张：motionpilot / motionrules / cubby（大卡用 cover-large）
产品页          8 页（+ 原 MotionSheet），各带 SoftwareApplication + 自己的 og:image；sitemap 15 → 23 URL
about           231 词，雇主锚点保留，无年份/现任雇主/地点词；邮箱 hi@zosc.com（Cloudflare 邮箱混淆会把它
                改写成 /cdn-cgi/l/email-protection，grep 源码看不到是正常的，浏览器显示正确）
旧词            zerb-logo / zerb-favicon / zerb.cc.cd 在页面输出中 0 次；blog.zosc.com 标题已是 zosc blog
```
**流程**：A 内容与隐私 → B 产品库 → C 首页/标题/logo → E 收尾，各在独立 worktree 分支，主会话逐个独立复核后
合并 v2，再 `--no-ff` 合并 main。四份报告 `docs/v2/A|B|C|E-REPORT.md`，校验脚本进了 `tools/`
（check-about / check-projects / check-home / check-motion / shoot-pages / product-covers）。

**备份与回滚**：tag `pre-v2-2026-10-08`（6247c29）；Vercel 生产部署 `dpl_Yamf1VWLCaSspQkSruT3Fyhhr1Di` 可一键 promote；
线上 15 页 HTML 快照 `.render-tmp/prod-snapshot-2026-10-08/`；about 原文在 zosc-career 私有仓库。

**用户当天定的流程规矩**：自己的站**核完直接推 main，截图推 clip**，不设「先看预览」门槛，不让用户登录后台；
预览保护已用 API 关闭（`ssoProtection: null`）。

**子任务纠正过主会话的判断**（都对）：私有仓库 README 不进索引；GitHub 自动社交卡含 star 数不能当封面；
QuantMind / quant-buddy-skills 是 fork、0 提交，不上架。

**同日追加（a3d7400）**：Hero 三行改回 **Motion · Visual · Code**，板块仍 Code 优先。用户反馈 Code 在前后
节奏散了——原编排是两行长词铺垫 + 4 字母 Code 用打字机收尾（短词结尾 = 句号）；4-6-6 台阶越走越重，
打字机落在 6 字母的 Visual 上拖沓。**Hero 是品牌宣言不是导航**，与板块顺序不一致无妨；标题标签不变。
教训：换词序之前先想动效与词长的配对，E 只换了文字、动效按行位绑定，结果可预见但派活时没想到这层。

**遗留（未改，记录在案）**：跨页锚点落点高度 21–160px 浮动（原有问题，疑似 `lenis.scrollTo` 与路由 hash 滚动抢）；
Hero 三行动效与词的对应变了（Code=遮罩 / Motion=模糊 / Visual=打字机）；`motion.ts` 注释仍按旧顺序命名；
12 个旧项目页 og:image 仍用 253×83 默认图；gateway 小卡封面底部标签被裁一半；「Zerb Hub」博文历史叙述与 README 旧截图保留。

## 2026-10-08 公开仓库改名 zerb-net → zosc.com

```
github.com/byzosc/zerb-net   → 301 → github.com/byzosc/zosc.com   （旧链接不会死）
本机 git remote              → git@github.com:byzosc/zosc.com.git
Vercel 项目 net-website      按 repoId 1262948974 关联，改名不影响部署
本机目录 /data/Projects/zerb-net   **不改**（见下）
```

**为什么改这一个**：它是唯一公开、被 Google 索引的带 `zerb` 的仓库，其标题字面是
`GitHub - byzosc/zerb-net: zosc's personal portfolio…` —— 描述已是 zosc，但仓库名把 `zerb`
顶在 URL 和 title 最前。GitHub 仓库页权重高，这是少数仍在给旧词投票的位置。
改后 `zosc` 在 URL 与标题中各出现两次。

**为什么其余不改**（用户判据：只改爬虫抓得到的）：
```
zerb-clip / zerb-hub          PRIVATE，匿名 404，爬虫看不到 → 零收益
/data/Projects/zerb-net       零 SEO，但三处 CLAUDE.md/AGENTS.md 写死该路径，
                              各会话工作目录、tmux 窗口全要跟着动 → 牵扯大收益零
clip.zerb.net                 自用中转服务，不对外、本就不该被索引
```

**名字选 `zosc.com` 而非 `zosc-net`**：后者还拖着 zerb.net 时代的 `-net`；前者整串即品牌词+域名。

## 2026-10-08 搜索结果里的 Astro 图标：根因与解法

**不是「缓存还没更新」，是 Google 第一次就抓到了错的，然后按 URL 一直存着。**

```
10-06  品牌替换把 Layout 引用改成 zosc-favicon-*.png，但文件还叫 zerb-favicon-*.png
       → 三个图标全 404
       → Googlebot 恰在此窗口首次抓取 zosc.com，声明的 PNG 全取不到
       → 回退取 /favicon.svg，而那时它还是 Astro 模板默认 logo
       → 存入图标缓存
```

**决定性证据**：GSC 资源列表里 `zerb.net` 显示 Z 标、`zosc.com` 显示 Astro logo。
两站用同一套图标文件，结果不同，差别只在**首次抓取的时间点**。

**2026-10-08 10:44 SGT 已在 GSC 对首页点「请求编入索引」**（简中文案；繁中为「要求建立索引」。GSC 没有刷新图标的专用入口，图标只能随首页重抓一起更新）。

**解法：换 URL，不等缓存。** Google 图标缓存按 URL 存，旧 URL 已绑定错误结果，
改用从未被抓过的新路径强制重取：`zosc-favicon-*.png` → `zosc-mark-*.png`（旧文件保留不删）。
再在 GSC 对首页点一次「要求建立索引」即可。

**同日按 Google 文档修正的图标声明**（developers.google.com/search/docs/appearance/favicon-in-search）：
```
要求：正方形、至少 8x8，建议 >48px      （不存在「必须是 48 的倍数」这条，我差点说错）
支持：BMP GIF ICO PNG JPEG PPM TIFF     不含 SVG
明确：不会自动回退取 /favicon.ico，必须在首页显式声明
```
原先第一条声明是 32x32（低于建议值），且 ico/svg 文件虽在却未声明。现已把 192 提到最前，
并补上 `/favicon.ico`（实含 16/32/48 三档）与 svg 声明。

**教训（10-06 那个坑的第二次发作）**：引用改名而文件没改名，当时只造成「图标不显示」，
看起来是小事；真正的代价是**在那个窗口被 Googlebot 抓到，错误被固化进缓存，两天后才发现，
且无法手动清除**。全局替换后的引用完整性校验不是洁癖，是防止错误被外部系统固化。

### 邮件转发复核（同日）
```
启用  hi@zosc.com → zcbgood@gmail.com
启用  catch-all   → zcbgood@gmail.com
```
用户首次投递失败应为 MX 记录传播窗口，现已确认可用。

## 2026-10-07 DKIM 补齐授权后权限复查

- 用户授权补齐 Cloudflare 转发 DKIM 公钥，询问是否需要再次提供 token。
- 本机 `~/.config/cloudflare/token` 已存在，`GET /user/tokens/verify` 返回 200 / active；
  `GET /zones/{zosc_zone_id}/email/routing/dns` 仍返回 403 / Authentication error，
  精确查询 `cf2024-1._domainkey.zosc.com` 的 DNS API 返回空列表。
- 确认当前阻碍是所需端点的权限，非 token 丢失或失效。官方端点要求 Zone Settings Read 或 Write；
  指引在原 token 上为 `zosc.com` 增加 Zone Settings Read。尚未获取官方公钥，未写入 DNS。

## 2026-10-07 邮件转发复核：已投递，测试信在 Gmail 垃圾邮件；DKIM 遗漏待补

- 通过 Cloudflare API 确认 `hi@zosc.com` 与 catch-all 均 `enabled=true`，转发目标一致，
  `zcbgood@gmail.com` 状态为 `verified`；公共 DNS 的三条 MX 和单条 SPF 正确。
- 在已连接的目标 Gmail 全邮箱搜索（含垃圾邮件）找到 2026-10-07 21:57 SGT 的测试信，主题「666」。
  邮件头 `To: hi@zosc.com`、`X-Forwarded-For: hi@zosc.com zcbgood@gmail.com`、
  `Delivered-To: zcbgood@gmail.com` 与 Cloudflare Received 路径证明端到端转发成功，
  当前标签为 `SPAM`。未发送新测试信，未修改 Gmail 标签或过滤器。
- 用户消息中的 `hi@vosc.com` 与找到的实际邮件地址不同。公开 DNS 显示 `vosc.com`
  使用 worldnic NS / netsol MX，且不在当前 Cloudflare 账号 zone 列表中。
- 发现 DNS 缺少 `cf2024-1._domainkey.zosc.com` 的 DKIM TXT 公钥：DNS API 列表不存在该记录，
  Google 和 Cloudflare 公共 DNS 均返回 NXDOMAIN；邮件头对应签名出现
  `dkim=permerror (no key for signature)`。原发件方 Gmail DKIM、Cloudflare 公共域 DKIM、
  SPF、DMARC、ARC 均通过，不能据此断言缺失公钥是本次垃圾邮件分类的唯一原因。
- Cloudflare 官方说明 Email Routing 需要 MX、SPF **和 DKIM**：
  https://developers.cloudflare.com/email-service/configuration/domains/#routing-records 。
  当前 token 读 routing 设置及 `/email/routing/dns` 均返回 403；后者官方要求
  Zone Settings Read 或 Write：
  https://developers.cloudflare.com/api/resources/email_routing/subresources/dns/methods/get/ 。
  本轮未补公钥、未修改 DNS；剩余工作写入 TODO。
- 更正 2026-10-06 的过强结论：规则 + MX/SPF 足以让本次邮件成功转发，
  **不代表配置完整或收件箱归类已验收**；此前「验收全绿」未覆盖实际邮件投递和 DKIM。

## 2026-10-07 motionrules.com 旧身份清扫完成（keyframe-sheet-38 执行，本会话复核）

```
六页跟随跳转后逐页实测，可见文本 / meta / schema 中旧身份 = 0
补上的实体信号  author=zosc · Person.url=github.com/byzosc · sameAs=[github.com/byzosc] · zosc.com
```

**最有价值的一处不是改名字**：`index.html` 的 JSON-LD `Person.url` + `sameAs` 原本指向
`github.com/zerbLion`，**而该 URL 是 404**（GitHub 改用户名后连用户主页都不跳转，只有仓库 URL 跳）。
**sameAs 指向 404 等于给自己的实体投废票**，比显示旧名字更伤。六页页脚 `rel=author` 同一个 404。

**仍保留**：`data-origin="zerblion"`（三页各一处）、provenance 水印、`--motion-signature`。
HTML 自定义属性值不是可见文本、不被当内容索引，零 SEO 影响，且属产物溯源标记。

### 我被现查推翻的一条
我判断「GitHub README 被 Google 索引且权重高，README:264 的 AGPL 署名要改」。
对方去 `gh repo view` 查了可见性：`byzosc/keyframe_sheet` 是 **PRIVATE**，匿名访问 404，
README 根本不进索引 → 按用户判据属「爬虫抓不到」，不改。我已复核属实。
**我是按常识推的，它是现查的** —— 正是「说之前先把自己问明白」那条规矩的反例。
**判据：涉及「某页面会不会被索引」的结论，先查该仓库/页面的可见性，不要默认公开。**

### 另一条通用教训
对方同时改了生成器 `motionos/tools/add_seo_head.py` 的四个常量——**不改生成器，下次一跑全还原**。
与本会话在 `zero-build-blog` 改 `update-blog.mjs`、在 profile 仓库改 `scripts/update-blog.mjs` 同理。
**凡是被模板/脚本生成的内容，根在生成器里，改产物只是擦痕迹。**

### 未并入本轮（已知会用户，等其决定）
`keyframe_sheet/web/main.js:13` 的 `TOKENS_URL = https://motion.zerb.net/motion-tokens.json`
**是死链**（DNS 无记录，curl http=000）；正确落点 `https://motionrules.com/motion-tokens.json`（200/2852B）。
网页端静默降级所以长期无人发现；注释写明 AE 插件拉同一地址，MotionPilot 侧可能同样断着。
**这是功能故障不是 SEO 问题**，按用户「只改爬虫抓得到的」判据不并入本轮。

## 2026-10-07 01:39 SGT GSC 首页已索引，已请求重抓

```
网址检查 https://zosc.com/
  网址在 Google 服务中     ✓
  网页索引状态  已编入索引  ✓
  HTTPS                    ✓
  → 已点「要求建立索引」(2026-10-07 01:39 SGT)
```

**为什么要重抓**：Googlebot 在 10-06 抓到的是改名过程中的**中间版本**，
快照标题是 `ZOSC LION — Motion · Visual · Code`。当天改名分两步
（`ZERB LION` → `ZOSC LION` → 用户拍板的小写 `zosc`），正好被抓在中间那一刻。
线上实况早已是 `zosc — Motion · Visual · Code`（已核），**不是漏改**。
`ZOSC LION` 这个标题会稀释裸词 `zosc`，所以必须刷掉，只能靠「要求建立索引」插队，等不来。

**同轮修掉的外部实体信号**（GitHub 页面权重高、爬得勤，往往比自己的站更早被用来确认「zosc 是谁」）：
```
profile README        "Hi, I'm ZERB LION" → zosc；全部博客链接 → blog.zosc.com
scripts/update-blog.mjs  SITE 常量 → blog.zosc.com   ← 根因：不改它，Action 每次把死链写回来
workflows             BLOG_REPO / STATS_USER → byzosc
4 个仓库 homepage     zerb.net → zosc.com / blog.zosc.com
zerb-net 仓库描述     "ZERB LION's personal portfolio" → "zosc's ..."
```
**关键事实：`zerblion.github.io` 在改用户名后是 404**（实测）——GitHub 只对仓库 URL 做跳转，
`<用户名>.github.io` 不跳。所以 profile 上那整块博客链接此前全是死链。

**zero-build-blog 仓库已一并处理**（用户 2026-10-07 追加指示「blog 的事情你也做了吧」）：
```
assets/app.js       CONFIG.repo + giscus.repo → byzosc/zero-build-blog
                    repoId/categoryId 是不变的规范 ID，未动，评论区不受影响
博客自身地址        zerblion.github.io（404）→ blog.zosc.com
文章正文旧仓库链接  按实际改名修正，不是简单换用户名：
                      AI_Chat_ChromeExtension → AiChat-Extension
                      nas_monitoring          → nas-monitoring
                      zrxl_blog               → zero-build-blog
README / zh-CN      署名 @ZerbLion → @byzosc
LICENSE             版权人 → zosc
```
线上已验证：`blog.zosc.com/assets/app.js` 中 `ZerbLion` 出现 0 次，首页 200。

**改链接前先逐个实测可达性**，否则会把旧名字换成一堆新 404。本轮因此发现：
`keyframe_sheet` / `motion-design` / `trading-pannel` / `AiChat-Extension` **四个仓库是 private**，
文章里指向它们的链接**对读者一直是 404**，与改不改名无关。这是内容决策（设为 public，
或从文章里撤掉链接），留给用户定，未擅自改动文章结构。

### 下一步对照
- 1–3 天：GSC「网页索引状态」报表数据出来（新资源固定延迟，不是故障）
- 重抓生效后：搜索结果标题应变成小写 `zosc`
- favicon 的地球图标：Google 单独抓站点图标且缓存很久，三个图标文件实测均 200，只能等

## 2026-10-07 zosc.com「打不开」= 正常的 NS 切换传播（更正同日早先的错误结论）

**结论：域名、注册商、注册局、Cloudflare 四处全部正确，无需任何操作，也不该找 Dynadot。**

```
RDAP 注册局记录   注册商 Dynadot Inc
                  NS = KEATON / WREN.NS.CLOUDFLARE.COM（只有这两条）
                  last changed 2026-10-06 16:26 SGT
父委派 TTL        172800s = 48h  →  最晚 2026-10-08 16:26 SGT 全部刷新
```

过户前查过本域名的解析器缓存着旧主人的 `dns17/18.hichina.com`，这是**每次换 NS 都会发生的
正常现象**，缓存一过期就回 `.com` 拿到 Cloudflare。残留的阿里云 zone 不在任何委派路径上。

**国内三大公共 DNS（223.5.5.5 / 119.29.29.29 / 180.76.76.76）当时已全部正确**，访客与爬虫不受影响。

### 我同日早先的错误结论（已作废，留档）
我先说「hichina 用自己的 NS 记录给旧委派续命，不会自己过期」，据此让用户改 Mac 的 DNS，
用户因此怀疑域名有缺陷、要找 Dynadot 退款。**那句话是推理，不是实测。** 两条证据当场就能证伪：
1. 本机缓存里旧 NS 的 TTL 在老实倒数（662 → 659 → 656），没有被续命；
2. `223.5.5.5` 是阿里自己的公共 DNS、最可能缓存 hichina，它当时已经是正确答案。

**教训：带「永远 / 不会自己好 / 必须人工干预」这类绝对判断的结论，说出口前必须有一条实测证据。
它会直接改变用户的行动——这次差点让他去跟注册商要退款。**
先查 RDAP 的 `last changed` 和父委派 TTL，算出传播窗口，再决定要不要喊「出问题了」。

### 对本会话仍然有效的一条
本机上游 Oracle 内网解析器 `169.254.169.254` 刷新慢，验证 zosc.com 一律用
`curl --resolve zosc.com:443:172.67.141.94`，不许拿本机 curl 失败当「线上挂了」，也不许写轮询脚本打它。

## 2026-10-06 收尾补记

- **GSC 地址更改已提交**（`zerb.net` → `zosc.com`，用户操作）。301 已就位，Google 的校验直接通过。
  **此后约 180 天内 `zerb.net` 的 301 绝对不能断**——断了权重迁移就中止，域名必须续费。
- **Footer 的 GitHub 链接漏改**：`github.com/ZerbLion` → `byzosc`。X / Steam 上一轮都改了唯独它没有，
  因为 GitHub 自己会跳转，点着没感觉。**教训：站内自述身份必须和 schema `sameAs` 逐条一致**，
  靠平台跳转掩盖的不一致，Google 看得见。本地 git remote 同样仍指旧仓库名，一并改掉。
- **Behance 姓名字段**：姓氏必填，定为 `zosc` + `lion`（显示 `zosc lion`）。
  **名字栏绝不能填 `Zos`**——拆词会毁掉裸词 `zosc` 的实体信号，那是整个 SEO 主线的根。

## 2026-10-06 域名与品牌迁移：zerb.net / ZERB → zosc.com / zosc（本轮全部完成）

**背景**：`zosc.com` 于 2026-10-05 过户到 Dynadot（万网过期竞价拍得，¥8,057.49 含一年续费，
到期 2028-08-04）。WHOIS 实测隐私保护生效——注册人姓名 REDACTED，地址/电话/邮箱全是 Dynadot 的，
用户真实信息零泄露。

### 做了什么

| 层 | 内容 |
|---|---|
| DNS | NS → `keaton/wren.ns.cloudflare.com`（**Cloudflare 按 zone 分配 NS，不是账号通用**，照抄 zerb.net 的 carlos/sydney 会永远 pending）。A → `76.76.21.21` 橙云代理，与 zerb.net 同配置 |
| Vercel | `net-website` 项目加 `zosc.com` + `www.zosc.com`；`zerb.net` / `www.zerb.net` 设 **301 → zosc.com**，逐页保留路径 |
| 站内 | 19 文件 `zerb`→`zosc`；核心是 `astro.config.mjs` 的 `site` —— 它决定 canonical/sitemap/og:url。改之前 zosc.com 每页 canonical 都指回 zerb.net，等于告诉 Google「zosc.com 只是副本」 |
| 品牌 | `ZERB LION` → `ZOSC LION` → 最终定为**小写 `zosc`**（用户 2026-10-06 拍板）。schema `name: 'zosc'`，别名保留 `byzosc / ZERB / ZERB LION / zerbLion` 供 Google 关联新旧实体 |
| GitHub | 用户名 `zerbLion` → `byzosc`（**无 API，只能网页端**）。profile 字段 name/blog/twitter/location 已用 API 更新 |
| 博客 | 绑 `blog.zosc.com`（Cloudflare CNAME → `byzosc.github.io`，灰云直连以便签证书）。**解除了对 GitHub 用户名的依赖**，以后改名只动一条 DNS |
| 邮件 | `hi@zosc.com` + catch-all → `zcbgood@gmail.com`；`zerb.net` 原三条规则一并改到新邮箱。MX/SPF 手动补齐 |
| 图标 | favicon 三个 PNG 改名对齐引用；`favicon.svg` 原来一直是 **Astro 默认 logo**，换成 Z 标；`favicon.ico` 重做 |

### 踩过的坑（下次别再犯）

1. **Cloudflare 的 NS 按 zone 分配**。我让用户照 zerb.net 填 carlos/sydney，导致 zone 一直 pending。
   正确做法：先 `GET /zones` 读该 zone 的 `name_servers`。
2. **全局替换必须保护真实资源**。受保护清单：`zerblion@gmail.com`（当时）、`zerblion.github.io`、
   `github.com/zerbLion`、`steamcommunity.com/id/zerblion`、`zerb.cc.cd`、`zerbnet-media`（R2 bucket）、
   `zerb-net-tools`、`zerb-logo.png`、`zerb-cc-cd`（项目 slug）。
   **`com.zerblion.motionpilot.cep` 绝对不能改**——Adobe CEP 扩展标识符，改了已上架版本作废。
3. **替换会造出死链**。`x.com/zoscLion` 是替换生成的，实测 404；真实 handle 是 `x.com/byzosc`。
   **替换后要逐条验证外链真实存在**。
4. **替换会造出「引用改了但文件没改名」**。favicon 三个 PNG 因此全 404 且无人发现。
   **全局替换后必须跑一遍「引用的资源文件是否真实存在」**。
5. **GitHub 改名会断 Pages**（仓库 URL 重定向，但 `<user>.github.io` 不重定向），
   且 **profile README 仓库名必须等于用户名**，否则主页介绍消失（已把 `ZerbLion` 仓库改名为 `byzosc`）。
6. **Cloudflare Email Routing 的权限分两层**：`Zone·Email Routing Rules`（规则）与
   `Account·Email Routing Addresses`（收件地址）。「启用」端点两者都不覆盖，
   但**启用的实质只是写规则 + 加 MX，这两件都能用 API 做完**，不必推给用户。
7. **本机 systemd-resolved 会缓存域名接通前的 NXDOMAIN**，导致自测 HTTP 000。
   验证时用 `--resolve` 指到边缘 IP，或查公共解析器；**别据此判断站点有问题**。

﻿# DONE.md

## 已完成的重要修改

以下内容只记录有意义的网站、页面、代码、资源、部署、结构变化。历史细节如无法准确确认，统一标注为“根据当前文件状态推断”。

## 网站结构

- 根据当前文件状态推断，已将 WordPress static export 整理为当前 `D:\net\net-website` 部署副本。
- 保留原始备份路径 `D:\net\net` 作为源参考。
- 已将 WordPress 静态导出所需的前端依赖集中迁移到 `assets/`，不再保留根目录下的 `wp-content` 和 `wp-includes`。
- 已将作品集图片和视频集中到 `media/`。
- 已将 `media/` 从原 WordPress 年/月层级重组为按资源类型和用途分组的目录：
  - `media/images/common/brand/`
  - `media/images/projects/<project-slug>/`
  - `media/images/blog/<post-slug>/`
  - `media/videos/projects/<project-slug>/`
- 已将公开路由整理为 `works/`、`project/<english-slug>/`、`blog/`、`resume/` 和 `404.html`。
- 已将旧 `portfolio/`、`project/page/*` 归档页移入 `reports/archived-routes/`，旧 URL 通过 redirect 跳到 `/works/`。
- 添加了 `reports/`，用于保存资源清理报告、归档路由备份和 MP4 文件清单。
- 文档结构调整为：
  - `README.md`
  - `AGENTS.md`
  - `docs/TODO.md`
  - `docs/DONE.md`
- 2026-06-08 已再次按当前会话状态梳理上述四个项目文档，确认状态、规则、待办和完成记录继续集中在这四个文件中维护。

## 运行和部署

- 根据当前文件状态推断，添加了本地静态预览脚本 `tools/local-server.mjs`。
- 本地预览地址为 `http://localhost:4173/` 或 `http://127.0.0.1:4173/`。
- 根据当前文件状态推断，添加了 Vercel 部署配置 `vercel.json`。
- 添加了 `.gitignore`。
- 添加并更新了 `robots.txt` 和 `sitemap.xml`。
- 添加了 `redirects.json`，用于记录旧 URL 到新 URL 的迁移关系。

## 页面和交互

- 2026-06-08 已撤销一次错误的首页头部下滑折叠隐藏交互。该交互会导致导航栏收起、不可点击，不符合用户期望。
- 2026-06-08 已将首页头部滚动动效修正为原主题式状态变化：头部保持顶部可见可点击，滚动后只切换 `headroom--top` / `headroom--not-top`，触发原 CSS 中的背景和 padding 过渡。
- 2026-06-08 已通过 Codex in-app Browser 验证首页头部滚动状态：顶部为 `headroom--top`，滚动后为 `headroom--not-top`，`rectTop` 保持 `0`，`transform` 为 `none`。
- 根据当前文件状态推断，首页和 `works/` 前两个 portfolio card 已改为外部链接：
  - `https://www.vivo.com/my/products/vivo-vision`
  - `https://www.jmgo.com/luna`
- 根据当前文件状态推断，为上述两个 card 添加 click-capture script，避免 WordPress portfolio/lightbox scripts 拦截点击。
- 根据当前文件状态推断，`project/vivo-xr/index.html` 和 `project/luna-os-sinus/index.html` 已回滚到空详情页状态。
- 根据当前文件状态推断，移除了 `project/vivo-xr/index.html` 和 `project/luna-os-sinus/index.html` 中曾误写入的字面文本 `` `n ``。
- 根据当前文件状态推断，旧 `/resume-2/` 已迁移到 `/resume/`，并通过 redirect 保留旧 URL。
- 根据当前文件状态推断，旧 404 目录页已整理为 `404.html`。
- 2026-06-08 修复 `project/time-garden/index.html` 为空文件的问题。已从原始备份 `D:\net\net\project\时间花园\index.html` 恢复 Organic Installation Art 页面内容，并适配当前媒体路径 `/media/images/projects/time-garden/...`、当前 canonical `/project/time-garden/` 和相邻项目导航。

## 资源清理

- 根据当前文件状态推断，已将 CSS、JS、字体资源集中到 `assets/css/`、`assets/js/`、`assets/fonts/`。
- 根据当前文件状态推断，已将作品集图片和视频集中到 `media/`。
- 已将当前仍被页面使用的图片和视频移动到用途型媒体目录，并批量更新 HTML 中的 `src`、`srcset`、`poster`、`background-image` 等媒体路径。
- 已删除 `media/2021/03/website-video.mp4` 所在的 `media/2021/03/` 目录。删除前确认页面没有引用该视频，只有 `reports/mp4-files.txt` 记录过它。
- 根据当前文件状态推断，删除了未被引用的 WordPress 自动生成缩略图。
- 根据当前文件状态推断，删除了未被引用的大图文件。
- 2026-06-08 已将当前媒体目录拆分为 `media/images/` 和 `media/videos/`，并同步更新页面中的图片和视频引用。
- 2026-06-08 已添加可复跑的媒体优化脚本 `tools/optimize-media.mjs`。脚本会将明显更小的 JPG 转成 WebP 并更新引用；MP4 会重新编码，只有新文件明显更小时才覆盖原文件。
- 2026-06-08 已执行一轮媒体自动优化：整体媒体体积约从 `90.25MB` 降到 `75.89MB`，节省约 `14.37MB`。
- 2026-06-08 图片约从 `12.32MB` 降到 `11.36MB`，节省约 `0.96MB`，本轮将 `144` 张 JPG 转成 WebP。
- 2026-06-08 视频约从 `77.95MB` 降到 `64.54MB`，节省约 `13.41MB`，本轮检查 `29` 个 MP4 并覆盖其中 `6` 个更小版本。
- 2026-06-08 已生成 `reports/optimize-media-results.json`，并更新 `reports/video-index-current.txt`。
- 2026-06-08 优化后已扫描 `419` 个媒体引用，缺失文件数为 `0`。
- 2026-06-08 优化后已通过 Codex in-app Browser 抽查首页、`works/`、`project/diy-motion-elements/`、`project/dynamic-weather-art/` 和 `project/wallpaper-universal-design/`，坏图数为 `0`，抽查视频 `readyState` 正常。
- 根据当前文件状态推断，MP4 已完成一轮保守压缩；后续仍需用户决定是否外链/CDN 托管或继续保留在仓库。
- 生成了 `reports/mp4-files.txt`。
- 生成了 `reports/deleted-unreferenced-thumbnails.txt`。
- 生成了 `reports/deleted-unreferenced-large-images.txt`。
- 当前没有单独保留 `media/README.md`。媒体目录用途说明已经集中到 `README.md`，避免项目文档入口分散。
- 媒体路径重组后曾出现一轮错误替换，把部分 `/media/projects/<slug>/<file>` 写成 `/media/projects <slug> <file>`，导致本地页面出现坏图。该问题已批量修复。
- 修复后已在 `http://localhost:4173/` 通过 Codex in-app Browser 刷新验证首页图片加载正常，浏览器检测 broken image 数量为 `0`。
- 修复后已抽查媒体 HTTP 响应，确认 logo 图片和项目 MP4 能返回 `200`，视频响应类型为 `video/mp4`。
- 修复后已扫描确认页面中不再存在 `/media/projects `、`/media/common `、`/media/blog ` 这类错误空格媒体路径。

## Astro 重构

- 2026-06-15 确定方向：把站点重构为 Astro，三大板块 Motion · Visual · Code，首页改长滚动 + 锚点；视频迁 Cloudflare R2；新增多 provider AI 问答。老静态站全程保留并行。
- 2026-06-15 完成 Phase 0 脚手架：
  - 在 `app/` 用 `create astro`（minimal 模板）建 Astro 6.4.6 项目，加 Tailwind v4（`@tailwindcss/vite`）和 `@astrojs/vercel` 适配器。
  - 建 `app/public/media` 目录 junction 指向根 `media/`，让开发服务器直接读现有图片；已在 `app/.gitignore` 忽略该 junction。
  - 设计系统：`app/src/styles/global.css` 定义暗色 token（ink/paper/accent 等）、Montserrat/Inter 字体、`.reveal` 滚动入场占位（带 prefers-reduced-motion 回退）。
  - 内容模型：`app/src/content.config.ts` 定义 projects collection（title/summary/pillars[motion|visual|code]/cover/year/order/externalUrl/draft）。
  - 用 `app/src/content/projects/*.md` 为 11 个项目建数据文件（先填标题/封面/pillars/简介占位，正文待 Phase 1 迁移）。
  - 组件：`Layout.astro`（含非阻塞 Google Fonts + IntersectionObserver reveal 脚本）、`Header.astro`（Motion/Visual/Code/About 锚点导航 + Ask AI 按钮 + headroom 式滚动变背景）、`Footer.astro`、`ProjectCard.astro`。
  - 首页 `app/src/pages/index.astro`：Hero（Motion. Visual. Code.）+ 三板块按 pillar tag 筛选渲染项目网格。
  - `npm run build` 通过；`npm run dev`（端口 4321）经 preview 截图确认 Hero 渲染正常。
  - 加 `.claude/launch.json`（astro / 4321）供本地预览。
- 2026-06-15 Phase 0 后按用户反馈修 UI：
  - `astro.config.mjs` 关闭 dev toolbar（`devToolbar.enabled=false`）；说明那是开发期调试条、非水印、不进生产构建；Astro 完全免费开源。
  - Header 左上角改用原 logo 图 `cropped-logo_high2.png`（替换文字 ZERB）；导航字体统一为 Montserrat（对齐原 Inspiro 主题）。
  - 实现移动端 Menu（全屏滑入面板，Menu/Close 切换）。
  - Ask AI 按钮接通：点击打开右侧滑入聊天面板 `AskAI.astro`（UI 壳 + 建议问题 + 输入框；真实多 provider 流式后端留到 Phase 4）。
  - 删除 Hero 顶部「ZERB — Portfolio」eyebrow 文案。
  - 作品卡片封面比例改为原作品页一致的 950×320 横幅（`ProjectCard` aspect-[950/320]）；并把 11 个项目封面、顺序、外链对齐原 `works/index.html`（vivo-xr→vivo.com，luna-os-sinus→jmgo.com 走 externalUrl）。
  - Code 板块暂空，渲染「More coming soon.」占位。
  - 浏览器验证：logo 与全部封面加载正常（broken=0），导航字体为 Montserrat，Ask AI 面板与移动菜单交互正常。

- 2026-06-15 Phase 1（项目详情迁移，进行中）：
  - 新增 `tools/extract-project-content.mjs`：从每个 `project/<slug>/index.html` 抽取 `entry-content` 正文 HTML，写到 `app/src/project-bodies/<slug>.html`，供 Astro 详情模板 `set:html` 渲染。已抽取 11/11。
  - 新增 Astro 详情模板 `app/src/pages/project/[slug].astro`：hero（标题/年份/pillars/封面）+ 迁移正文 + 上一个/下一个导航；外链项目（vivo-xr、luna-os-sinus）不生成详情页。生成 9 个详情页。
  - 详情正文加 `.entry-content` 作用域样式（figure/img/video/figcaption/spacer/链接）。
  - 浏览器验证：dynamic-weather-art 详情页 200、封面与 3 图 1 视频加载正常（视频 206 / video/mp4 / readyState 4）、prev/next 正确；nft-asset-design（17 媒体）与 luna-os-ar-theme（10 图）坏图/坏视频数为 0。
- 2026-06-15 Phase 1 第二轮 UI 反馈修复：
  - 重新启用 Astro dev toolbar（用户确认有用，仅开发期可见）。
  - favicon（浏览器缩略图）改回原站 `cropped-头像2-1-32x32.webp` / `192x192`。
  - 左上角 logo 放大（h-10 / md:h-12）。
  - 导航字体改 regular（font-normal），Ask AI 按钮 medium。
  - 修详情页 fixed header 与标题重叠：详情页 main 顶部留白加大（pt-36 / md:pt-44）。
  - 详情页末尾 prev/next 间距加大（py-16、mt-16），小屏单列、sm 起两列。
- 2026-06-15 Phase 1 完成（works / blog / resume / 404 迁移）：
  - 新增 `tools/extract-pages.mjs`，抽取 resume 和 2 篇博客正文到 `app/src/migrated/`。
  - 内容模型新增 blog collection（title/date/cover/excerpt）；`app/src/content/blog/*.md` 建 2 篇文章（和煦暴风、静默是永恒的主题）。
  - 新增页面：`works/index.astro`（按 motion/visual/code 过滤的作品网格）、`resume/index.astro`、`blog/index.astro`、`blog/[slug].astro`、`404.astro`。
  - 构建产出 16 页。浏览器验证：works/resume/blog/两篇博客全部 200、404 返回 404，全站坏图/坏视频数为 0；works 过滤交互正常（all 11 / motion 7 / code 0）。

- 2026-06-15 内容调整 + UI 优化（UI pass 第一轮）：
  - 板块重排：motion = VIVO XR、LUNA OS Sinus、China Mobile CAVE（按此顺序）；其余 8 个项目改为 visual；Code 板块新增项目。
  - 新增 Code 项目 `zerb-cc-cd`（外链工具，externalUrl 暂用 `https://zerb.cc.cd`，待用户确认），并原创设计契合暗色风格的 950×320 横幅封面 `media/images/projects/zerb-cc-cd/cover.svg`（代码片段 + 终端提示符 + wordmark + 强调色圆点）。
  - 页脚版权改为 `© 2026 ZERB LION. All rights reserved.`。
  - UI 优化：全局 `scroll-padding-top:96px`（锚点定位避开 fixed header）、自定义滚动条、`:focus-visible` 焦点态；首页 section 间距加大（py-28/md:py-36）+ 动画滚动提示；ProjectCard 升级 hover（遮罩 + 箭头徽标，外链显示外链箭头、内链显示前进箭头，标题 hover 变强调色）。
  - 浏览器验证：motion 3 / visual 8 / code 1（zerb.cc.cd 外链，封面 SVG 200/image+svg），版权文案正确，scroll-padding/箭头/滚动提示均生效。

- 2026-06-15 Phase 2（视频迁 Cloudflare R2，代码侧完成）：
  - 用户已建 R2 bucket `zerbnet-media`（自动/APAC，标准存储类），启用公共开发 URL：`https://pub-a0c77317c3024e5db24448b1f68cdada.r2.dev`。
  - 新增 root `package.json`（tools 用，装 `aws4fetch`）与脚本：`tools/lib/r2-media.mjs`（确定性 ASCII key 生成 + 视频枚举）、`tools/build-media-manifest.mjs`、`tools/apply-media-manifest.mjs`、`tools/upload-media.mjs`。
  - 新增 `.env.example`（R2 凭证模板），`.env` 已加入 `.gitignore`。
  - 生成 `media-manifest.json`：29 个本地视频 → R2 公共 URL 的确定性映射（中文文件名转 ASCII + 短 hash 防冲突）。
  - 已把 `app/src/project-bodies/*.html` 中 10 处实际引用的 `/media/videos/...` 重写为 R2 URL（5 个项目），无残留本地视频路径；构建 16 页通过。
  - 2026-06-15 用户填 `.env` 后已执行 `npm run media:upload`：29 个视频全部上传成功（Uploaded 29 / skipped 0 / failed 0）。
  - 浏览器验证：10 个被引用视频从 r2.dev 返回 206 / video/mp4；nft-asset-design 详情页 3 个视频 readyState 4、无错误。Phase 2 完成。
  - 已 commit/push 到 `origin/dev`（c5910d9）；`.env` 未入库。

- 2026-06-16 Phase 4（AI 问答，代码完成并验证到网络边界）：
  - `app/src/lib/knowledge.ts`：从 projects/blog collections + resume 编译 system prompt，话题锁定只答 ZERB/作品集相关。
  - `app/src/lib/providers.ts`：多 provider 流式抽象（Gemini/OpenAI/Anthropic），`AI_PROVIDER=auto` 按 gemini→openai→anthropic 选；统一 SSE 解析。
  - `app/src/lib/ratelimit.ts`：内存版限流（按 IP 每分钟/每天 + 全站每日上限）；生产可换 Vercel KV/Upstash。
  - `app/src/pages/api/chat.ts`：POST 接口，校验/限流/流式；`prerender=false`，走 Vercel 函数。
  - `astro.config.mjs` 加 `vite.envDir:'..'`，本地开发读根 `.env`。
  - `AskAI.astro` 前端接通流式：发问→流式渲染 bot 气泡，建议问题首问后消失，错误优雅降级。
  - 验证：校验路径 400、限流 6/分钟后 429（即时）、provider 解析与 key 读取正常、前端流式渲染链路通。
  - 已知网络限制：本机（中国 GFW）连不上 Google，Gemini 本地不可测；OpenAI/Anthropic 本机可达。生产 Vercel（海外区）调用 Gemini 不经 GFW，线上可用。本地测试需开 VPN 或临时用可达 provider。

- 2026-06-16 Phase 3（Motion 动效）：
  - 装 `lenis` + `gsap`；新增 `app/src/scripts/motion.ts`：Lenis 平滑滚动 + GSAP ScrollTrigger 滚动入场（`.reveal`）、Hero 进场 stagger（`[data-hero]`）、可选视差（`[data-parallax]`）；尊重 prefers-reduced-motion。
  - Layout 接入 Astro View Transitions（`ClientRouter`）；motion 在 `astro:page-load` 重建、`astro:before-swap` 拆除，幂等防重复。
  - 把 Header、AskAI 移到 Layout 统一渲染并加 `transition:persist`（site-header / askai），导航切换时持久不重建；移除各页面重复的 `<Header />`。
  - `.reveal` 改为 GSAP 控制（移除 CSS transition），加 `<noscript>` 回退保证无 JS 也可见。
  - 验证：Lenis 激活（html.lenis）、Hero 入场 opacity 1、16 个 reveal 均被 GSAP 接管（初始 opacity:0/translateY 30）、无 console error；View Transition 跳转到详情页后 Header 持久、Ask AI 按钮仍可用、Lenis/motion 正确重建。

- 2026-06-16 修 Hero 大字消失 bug（缩放/手机端触发，刷新不恢复）：
  - 根因：Hero 进场用 GSAP `from`/`fromTo`，而 `ScrollTrigger.refresh()` 在每次 resize 自动触发并会 revert from/fromTo 补间，把标题还原到 opacity:0 起始态并卡住（inline opacity:0）。
  - 修法：Hero 进场改为纯 CSS（`@keyframes heroIn` + `animation-fill-mode: forwards`，`[data-hero] > *`），完全脱离 GSAP/ScrollTrigger，resize 免疫；motion.ts 移除 Hero 补间。reduced-motion 媒体查询直接显示。
  - 验证：GSAP 不再给 Hero 设任何 inline 样式，连续 6 次 resize 后 Hero 仍无 inline opacity（bug 签名消失）；reveals/Lenis 不受影响，无 console error。（注：预览环境当前不产出动画帧，computed 动画进度无法可视化验证，但已确认无 JS 覆盖、CSS 规则正确。）

- 2026-06-16 Hero 小球动效（方案 A+C 结合）：
  - 三个强调点改为两层结构 `.hero-dot`（外层接鼠标磁吸）+ `.hero-dot-i`（内层性格动画），避免两个 transform 冲突。
  - 默认循环（CSS，全平台）：Motion = 带高光的滚动球（radial-gradient + dotRoll 旋转位移）；Visual = 柔光呼吸 + 色相漂移（dotGlow）；Code = 终端光标闪烁（dotBlink，圆角方块）。
  - 桌面交互：`pointermove` 磁吸（半径 170px，向光标位移），仅 `(hover:hover) and (pointer:fine)` 启用；hover 加速对应性格动画。
  - 移动端阉割（仿 frad.me）：触屏（pointer:coarse）不绑鼠标磁吸，仅保留轻量 CSS 循环。
  - reduced-motion：停止所有点动画。
  - 验证：3 个点结构正确、per-pillar 动画名（dotRoll/dotGlow/dotBlink）与 motion 高光渐变均生效、无 console error。（预览视口宽 0 + 不产帧，视觉效果需真实浏览器查看。）

- 2026-06-16 按反馈调性能与小球动效：
  - 去掉 Lenis 平滑滚动，回到原生滚动（解决"变卡/不大气"）；motion.ts 不再依赖 Lenis，ScrollTrigger 走原生滚动；卸载 `lenis` 依赖。
  - 移除 `.reveal` 的 `will-change`（减少常驻合成开销）；reveal 时长略缩短。
  - 小球重做：Motion = 立体球面（top-left 高光 + inset 阴影的 radial-gradient）+ 左右滚动；Visual = 干净的双层光环涟漪（dotHalo，transform/opacity，去掉之前的 filter/box-shadow 常驻重绘）；Code = 竖条状闪烁文本光标（dotBlink，0.09em×0.26em）。主色仍为橙偏红 `#e7503a`。
  - 桌面 hover 加速、移动端只保留 CSS 循环、reduced-motion 全停。
  - 验证：原生滚动恢复（无 .lenis）、三球动画名（dotRoll/dotHalo/dotBlink）生效、无 console error。视觉需真实浏览器确认（预览视口 0、不产帧）。
- 2026-06-16 按反馈回退/微调（上一条部分撤销）：
  - 误删 Lenis 系用户本意只是询问动效是否影响流畅性，已把带阻尼平滑滚动（Lenis）加回（重新安装依赖、motion.ts 恢复 Lenis raf + teardown）。结论：三个小球动效是极轻量 transform/opacity，不影响滚动流畅性。
  - 小球收敛 + 统一为圆点：Visual 由涟漪改为轻微 glow 呼吸（dotGlow）；Code 由竖条光标改回圆点 + 柔和闪烁（dotBlink，border-radius 50%）；Motion 立体球滚动幅度/转角收敛（translateX 16% / rotate 80°）。hover 磁吸保留并轻微减速放大。
  - 验证：dampedScroll 恢复、code 圆点（radius 50%）、visual=dotGlow、motion=dotRoll，无 console error。
- 2026-06-16 三球差异化 hover 性格：
  - Motion = 碰撞：磁吸逻辑里 motion 改为「被斥力弹开」（其余两球吸附），鼠标靠近时 motion 球反向位移（factor 0.55）。
  - Visual = 加强 glow：默认 glow 调强；hover 时停止呼吸、绽放成更亮更大的稳定光晕 + scale 1.12。
  - Code = 激活态快闪：hover 时 blink 时长降到 0.45s，像正在输入的光标。
  - 验证：构建产物含 visual:hover bloom、code:hover 0.45s、client JS 含 repel 逻辑，无 console error。视觉需真实浏览器确认。

- 2026-06-16 Hero 三段式进场（按 pillar 定制）+ visual hover 渐变：
  - 结构：每行拆为 `.hl > .hl-t + .hero-dot`；Code 文本运行时拆为 `.ch` 逐字。
  - GSAP 时间线（set+to，非 from，避免 resize 还原）：Motion 小球滚入→文字上浮；Visual 光球绽放→文字 blur 晕染渐显；Code 光标闪现→逐字打字。完成后加 `intro-ready` 去隐藏门并 clearProps。
  - 兜底（吸取大字消失教训）：head 内联脚本加 `js` 类（仅 JS 时隐藏进场元素），5s 后加 `hero-fallback` 用 `!important` 强制 opacity/filter/transform 复位——即使 GSAP 时间线卡死也绝不会卡成隐形。已验证：预览中 GSAP 时间线停滞时，5s 后文字+小球全部 opacity:1。
  - 磁吸在 `introFinished` 前不生效，避免与进场打架。
  - Visual hover glow 改为带 `transition` 的渐变增强（不再瞬间）。
  - 真实浏览器需确认进场观感（预览环境视口 0 且 GSAP 帧停滞，无法呈现动画）。

- 2026-06-16 进场重做 + 磁吸修复 + 自定义光标：
  - 进场改为并行错峰：三行同时开始（每行 delay 0.13s），三个标题都逐字打字（全部 .hl-t 拆 .ch），三个球都从左侧 x:-100 滚入（roll + rotate -360）到位，总时长约 1.3s。
  - 修 Motion 球磁吸"触发几次就卡死"：原因是用带自身 transform 的 getBoundingClientRect 算距离形成反馈累积；改为用静止基准中心（rect 中心减去已应用 transform）计算，WeakMap 记录 applied。
  - Visual hover glow 改为独立 `::after` + `transition: box-shadow 0.7s`，真正渐变（之前 animation:none 切换不触发 transition）。
  - 新增 frad.me 式自定义球形光标：`#cursor`（Layout 内、transition:persist），JS lerp 跟随（0.2），hover 交互元素放大并填充，桌面隐藏原生光标（输入框保留），触屏隐藏。
  - 失败兜底（5s→3.5s）：进场约 1.3s，正常远早于兜底；GSAP 卡死时 3.5s 强制可见，已验证。
  - 验证：三标题均拆字 [6,6,4]、光标元素存在且桌面激活、兜底后全可见、无 console error。动画观感需真实浏览器确认。

- 2026-06-16 进场改为三种不同方式 + 间隔拉大：
  - Motion = 羽化边缘蒙版擦出（CSS `[data-mask]` 渐变 mask，GSAP 动 `--mx` 100%→0%，仅在 intro 窗口生效）；Visual = 高斯模糊渐显（blur(18px)→0 + opacity）；Code = 逐字打字（仅 Code 拆 .ch，已确认 [0,0,4]）。
  - 三行间隔 gap 0.42（依次出现，比之前 0.13 明显拉大），每行内出现速度不变。
  - 失败兜底扩展：`hero-fallback` 同时强制 `mask-image:none`/`filter:none`/`opacity:1`/`transform:none`，已验证兜底后 motion mask 复位为 none、全部可见。
  - 修复用户本地 dev 预览中断：重启 `npm run dev --prefix app` 即可（4321）。

- 2026-06-16 进场节奏 + 磁吸根因修复 + 刷新头横线：
  - 进场间隔 gap 0.42→0.35：下一行在上一行进行到约一半时入场（重叠更自然）。
  - Motion 球磁吸"触发几次就不动"真正根因：`.hero-dot` 上有 `transition: transform 0.25s`，与每帧 JS 设 transform 打架——用带过渡中间值的 getBoundingClientRect 算静止中心 → 漂移累积卡死。修复：删掉该 CSS 过渡 + 磁吸改为持续 rAF lerp（每帧 owner transform，静止中心 = rect − 当前已应用 transform，精确无反馈）。
  - 刷新时头部横线：是 header 滚动态边框（`var(--color-line)`，滚动时本应出现）；刷新时浏览器恢复滚动位置瞬间触发它显示在顶部。修复：head 内联脚本 `history.scrollRestoration='manual'`，每次加载从顶部开始，不再闪现。
  - 验证：dot transition-duration 0s、scrollRestoration manual、滚动态边框逻辑正确、无 console error。磁吸/进场观感需真实浏览器（预览 rAF 停滞 + 视口 0）。

- 2026-06-16 再修头横线/反色/磁吸：
  - 头横线根因确认是 header 滚动态 border（`var(--color-line)`）；scrollRestoration 不足以根治，直接**移除 header 底部 border**，滚动态只用背景模糊区分，彻底无横线。
  - "三个小球反色"实为自定义光标 `mix-blend-mode:difference`（反色）划过小球时反相；移除 mix-blend，光标改为半透明描边 + hover 强调色填充。
  - Motion 磁吸"几次后卡死"在本轮才动到真根因（CSS `transition:transform` 冲突），改为持续 rAF lerp + 静止中心精确计算；用户上次测的是未含该修复的版本。
  - 验证：cursor mixBlend normal、滚动态 header 无 border-bottom、无 console error。

- 2026-06-16 磁吸真根因 + 光标反色范围 + 节奏：
  - **磁吸卡死真根因**：head 兜底 `hero-fallback` 是无条件 3.5s 触发的，其 CSS `transform:none !important` 在 3.5s 后持续覆盖磁吸 transform → 前几秒能动、之后失效。改为**仅当 intro 未完成才加 hero-fallback**（正常完成不再触发，磁吸不被覆盖）。
  - 磁吸再加固：新增永不被 transform 的测量层 `.hero-dot`（wrapper）→ `.hero-dot-m`（接 intro/磁吸 transform）→ `.hero-dot-i`（性格动画）。基准位置直接读 wrapper rect，零反算、零漂移。
  - 光标反色：恢复 `mix-blend-mode:difference`（划过图像/文字反相，要保留），但 `.hero-dot` 设 `z-index:300` 高于光标 200 → 三个小球不被反相。
  - 进场节奏 gap 0.35→0.45、dot 滚入 0.8→0.7，序列更分明、不那么平。
  - 验证：wrapper/magnet 层各 3、cursor mixBlend difference、dot z 300>200、无 console error。

- 2026-06-16 导航/页脚调整：
  - 顶部导航在 Ask AI 之前新增 Resume 链接（→ `/resume/`，内容来自备份 `app/src/migrated/resume.html`，已验证 200 + 内容）。
  - 页脚移除 Resume、Blog 文本链接；新增 X（x.com/lionzerb）、GitHub（github.com/ZerbLion）、Steam（steamcommunity.com/id/ZerbX）图标外链 + 保留 Email。
  - 注：`/blog/` 路由仍存在但已无站内入口（未删除，待用户确认是否彻底移除）。

- 2026-06-16 进场过冲 + header 玻璃统一 + 光标跨页持久：
  - 小球到位加 `back.out(2)` 过冲回弹，落定更有物理感。
  - Header 玻璃背景改为全局常驻 CSS（`#masthead` rgba(5,5,5,0.55)+blur(10px)），移除原"滚动才出现"的 JS（顶部透明导致子页内容透过 header 重叠）；已验证首页与子页 header 背景一致。
  - 光标跨页失效修复：rAF 循环每帧重新 `getElementById('cursor')`（即使 View Transition 重建元素也能跟随），并在 `astro:page-load` 重申 `cursor-on` 类；已验证导航到 /works/ 后光标元素与 cursor-on 仍在。
  - 本地预览服务器已重启（4321）。

- 2026-06-16 上线 + 字体自托管：
  - 已部署到 Vercel（Root Directory=app，GEMINI_API_KEY 配置）：https://net-website-mu.vercel.app/
  - 修首屏字体闪烁(FOUT)+ 国内 Google Fonts 慢/被墙：改用 `@fontsource-variable/montserrat` + `@fontsource-variable/inter` 自托管（woff2 打包进 `_astro/`，同源加载），移除所有 fonts.googleapis/gstatic 引用；token 改为 "Montserrat Variable"/"Inter Variable"。
  - 验证：无 Google 字体引用、12 个 @font-face 自托管、Montserrat 900 + Inter 400 均加载、hero/nav 字体解析正确、无 console error。

- 2026-06-17 修 View-Transition 类 bug + 光标/导航:
  - **Ask AI 导航后打不开**(去 resume 滑动再点无反应):根因是 AskAI `<script>` 顶层捕获 DOM 引用,View Transition 后失效。改为交互时重新查询 DOM + document 事件委托,已复现并验证 /resume/ 导航后能开能关。
  - 光标进文章后卡在 hover 大白球:`astro:page-load` 复位 `is-hover` + 清标签,已验证导航后回到光圈态。
  - 光标球 44→50px;跟随 lerp 0.2→0.35(减少滞后误点);外链标签 "Open"、内部 "Go/View"、logo "Home"。
  - 导航链接热区加大(`px-3 py-3`),修"点在文字附近不触发"。
  - 把本会话关键经验写入 `AGENTS.md`「Astro 重建版工作规则」:架构、View Transitions 大坑(脚本只跑一次/引用失效/`astro:page-load` 复位)、预览环境局限、部署延迟与硬刷新、国内访问与自定义域名、自定义光标注意点。

- 2026-06-17 内容英文化:用 `tools/i18n-en.mjs` 把站内中文（项目正文 `set:html`、博客、标题/简介）整体翻成英文,统一全站语言。

- 2026-06-17 R2 视频上传 + 上线验证:把 gitignore 的视频上传到 Cloudflare R2 `zerbnet-media`,跑 `media:manifest` + `media:apply` 把本地视频 src/poster 批量替换为 r2.dev 公共 URL;线上验证视频可播放、egress 免费。

- 2026-06-17 三板块改版 featured-first(Plan B)+ 卡片精简(更大气):
  - 每板块首个作品做整宽大横幅(featured,优先用 `coverLarge` 高清源),其余作品 2 列网格;dynamic-weather 配 1920×1080 大图。
  - `ProjectCard` 去掉 summary/tags,只留标题 + 年份(image-forward),标题字号缩小(`text-lg md:text-2xl`),featured 同款。
  - 「View all work」链到 `/works/?f=<pillar>` 深链;`works/` 页读 `?f=` 自动选中筛选 + 整网格柔和淡入切换(`opacity 0→1`);MotionSheet 作为 Code 外链卡(`externalUrl`)。

- 2026-06-17 正文字体 Montserrat→Mulish:token `--font-body` 改 Mulish;`.entry-content` 正文用 Mulish、标题仍 Montserrat;自托管 `mulish-latin.woff2` + `<link rel=preload>`(沿用 `font-display:block`,无 FOUT)。

- 2026-06-17 手机端目录真根因修复(反复反馈的老 bug):`#mobile-menu` 原在 `#masthead` 内,而 header 有 `backdrop-filter`——会成为其 `position:fixed` 子元素的 containing block,把本应全屏的菜单困在 header 高度(只露 72px 一条)。把菜单移出 `<header>` 到 body 级,`position:fixed; inset:0` 全视口;验证 parent=BODY、height=812。**经验**:`backdrop-filter`/`transform`/`filter` 祖先会改变 fixed 后代的定位基准,已写入 AGENTS.md。

- 2026-06-17 遮罩层级 + 锚点导航修复:
  - 开抽屉(mobile menu / Ask AI)时 `html.overlay-open` 隐藏高 z-index(300)的 hero 小球,避免穿透到遮罩上方。
  - 从子页点 `/#motion` 不再回首页顶部:`location.hash` 存在时跳过 `astro:after-swap` 的 `scrollTo(0,0)`,改用 `lenis.scrollTo(el,{offset:-96,immediate:true})` 精确定位(native scrollIntoView 会被 Lenis 重置)。

- 2026-06-17 内联 AI Ask 引导块(frad.me 式):首页 Code 板块下新增「AI Ask」整屏板块(大标题 + 输入框样式按钮 "Ask me anything…"),点击走 `[data-ask-ai]` 委托打开同一侧边栏。手机上可直接在首页流里唤起问答,不必先找右上角。

- 2026-06-18 Ask AI 打开时主页面横向错位修复:`body { overflow:hidden }` 锁滚动会移除滚动条导致页面右移。`html` 加 `scrollbar-gutter: stable` 常驻滚动条槽,开/关抽屉不再位移。

- 2026-06-18 Ask AI 面板加「← Back」回退按钮:面板左上角新增圆形 ← 按钮(原先只有右上角 ✕),手机上更易单手够到/回退;避免用户只能伸到右上角,或误用系统返回手势(会直接退出整页)。`data-askai-close` 复用现有关闭委托,验证点击即关。PC 体验不变。

- 2026-06-18 Ask AI 关闭键定向 + 去掉 ✕(承接上一条):
  - 既然已有箭头键,右上角 ✕ 冗余 → 移除,只保留一个关闭控件。
  - 方向修正:面板是右边缘抽屉,关闭时向右退出,所以箭头由 ← 改为指向退出方向的 **→**(`data-cursor` 也由 Back 改 Close)。
  - 曾加入「打开时从左淡入归位 + hover 向右轻推」的定向动效,结果触发**间歇性「点两次才关闭」**:动效让按钮/箭头在点击瞬间位移,`mousedown` 与 `mouseup` 落到不同元素,浏览器不触发 `click`。按用户要求回滚动效,关闭键改为**静态 → 字形 + 纯颜色 hover**,单击必关(已验证)。
  - **经验(已写入 AGENTS.md)**:可点击元素(及其可成为事件目标的子节点)上不要加 transform/动画;移动的命中目标会让 mousedown/mouseup 错位、吞掉 click。必须动就给子节点 `pointer-events:none`,或保持命中目标静止。这类时序 race 预览环境无法可靠复现,宁可保守。

- 2026-06-22 作品卡片改版(多轮迭代,最终定稿;备份标签 `pre-card-redesign`):
  - **featured 大卡高度**:先把桌面满宽 950/320(~470px)收窄到 `lg:aspect-[1600/430]`(~375px,更沉稳);手机端再加高到 `aspect-[3/2]`(3:1 太矮放不下叠字)。
  - **featured 叠字**:标题/年份压在图上,底部常驻**羽化深色渐变 `.proj-scrim`** 托住文字(白底图也读得清)。标题排版与小卡一致:`font-display text-lg font-bold md:text-2xl`(去掉过重的 font-black 和紧字距)。去掉左上角板块标签(与板块大标题重复,画蛇添足)。
  - **封面统一处理(中性黑遮罩)**:桌面(鼠标设备)静止盖一层 `#000`/40% 中性黑遮罩,hover 抬起 + 缓放大,让**多列网格调性统一**;**手机/触屏不加整图遮罩**(单列、无 hover,遮罩只会白白压暗作品)——featured 仅靠 scrim 托标题、小卡片全亮文字在下。`.proj-*` 在 global.css,遮罩 gated 到 `@media (hover:hover) and (pointer:fine)`。
  - **走过的弯路**:先试「灰度 + 橙色 soft-light tint」双色调,混出难看的灰橙被否、整体回滚;改用**纯黑中性遮罩**(无色相、无去饱和)重做。**经验**:要"统一调性"用中性明度(黑遮罩/降亮),别叠色相 tint。
  - 小卡片尺寸/布局不变(`aspect-[950/320]`、文字在下)。`works` 页用同一 `ProjectCard`(plain 变体),自动获得统一 hover。
  - 备注:featured 三个项目(VIVO XR / Dynamic Weather Art / MotionSheet)`.md` 里 `year` 未填,叠层暂不显示年份。

- 2026-06-22 AI 限流升级为可持久化(`app/src/lib/ratelimit.ts`):
  - 加 **Upstash Redis(REST)** 后端:固定窗口计数(IP+窗口桶,分钟/天/全站三层),用一次 pipeline 往返做 INCR+EXPIRE,**跨所有 serverless 实例共享**,生产环境真正生效。env 兼容 `UPSTASH_REDIS_REST_URL/TOKEN` 与 Vercel KV 的 `KV_REST_API_URL/TOKEN`。
  - 未配置 Redis → 自动**回退内存版**(原逻辑原样保留);Redis 出错 → **fail-open**(放行,不让限流故障打断问答),全站日上限 + provider 自身配额兜底。
  - `checkRateLimit` 改为 async,`api/chat.ts` 改 `await`;`.env.example` 补充 Upstash 变量与说明。
  - **验证**:`npm run build` 通过;dev 实测请求确实流经新 async 限流器(返回 ok 后继续走 provider)。注:Astro **dev 不加载本地 `.env` 私有变量到代码的 `process.env`/动态 `import.meta.env`**,故本地无法用 `.env` 改阈值测 429;429 拒绝路径与原工作版一致,且失败 fail-open,风险低。线上接 Upstash 后即真实跨实例生效。

- 2026-06-23 自定义域名上线 `zerb.net`:
  - 在 Vercel 项目 Domains 加 `zerb.net`(取消 apex→www 重定向,用裸域);Cloudflare DNS 把 `zerb.net A 76.76.21.21`(Vercel)留下、阿里云老站 A `47.242.122.164` 改名 `ali_old` 停车、删掉 `nas` 的 AAAA。
  - **关键坑**:Vercel A 记录起初是橙云(已代理),Vercel 验证不过、签不出证书 → 改 **灰云(仅DNS)** 后 Vercel 立即验证 + 签 HTTPS。**验证**:`nslookup zerb.net`→`76.76.21.21`,`curl https://zerb.net`→`Server: Vercel` + 标题 `ZERB — Motion · Visual · Code`,证书有效。
  - **国内访问**:灰云直连 Vercel 时,国内手机**图片全挂**(海外多图请求超时);**改回橙云(已代理)+ Cloudflare 缓存静态资源后,国内可正常访问**(SSL 模式 Full/Full(strict) 即可,别用 Flexible)。根因仍是海外托管,橙云缓存是免费下的最优解;要更快需国内 CDN/备案。
  - `ali_old.zerb.net` 只是把阿里云 IP 存档,因证书/vhost 是给 zerb.net 配的,直接访问基本打不开(正常,不影响)。

- 2026-06-23 版权 / License / 可见性:
  - 加 `LICENSE`:**全部「All Rights Reserved」**(代码 + 作品都不开源,仅 public 供参考);README/README.zh-CN 的许可段同步;`Layout.astro` 的 `<head>` 埋了**不可见 HTML 署名注释**(`© ZERB LION · zerb.net`)。
  - 经验:**Public ≠ 开源**。想"看得到但不让抄",用「All Rights Reserved」+ 公开仓库的 git 时间戳作者证明,不用打水印(拉低观感)。
  - README 已按 `zrxl_blog` 风格重写(徽章 + emoji 分节 + 中英双版),线上地址改 `zerb.net`。

- 2026-06-23 博客收尾(老博客 → 独立站 `zrxl_blog`):
  - 作品集 `/blog` 及旧文章 URL **301 重定向**到 `https://zerblion.github.io/zrxl_blog/`(`blog/index.astro`、`blog/[slug].astro` 改 SSR redirect)。
  - 两篇 2017 老文(和煦暴风 / 静默是永恒的主题)迁入 `zrxl_blog`:`posts/2017-06-06-gentle-gale`、`posts/2017-07-01-silence-is-an-eternal-theme`,**文件夹名 + frontmatter 保留原始日期**;图片拷进各自 `images/`;**中英双语**(`index.md` 英 + `translations:[zh]`,中文 `index.zh.md` 从 `D:\net\net` 备份原稿还原)。该博客用 `posts.json`(`scripts/gen-posts.mjs` 生成)做清单。
  - 导航 + 页脚都加了 **Blog** 外链;页脚由图标改为文字链接(X / GitHub / Steam / Blog / Email)。

- 2026-06-26 品牌换标 + 仓库公开 + 改名:
  - **新 Logo**:换成 ZERB 的「Z」闪电标。源图 `Vector.png`(白色透明)→ `media/images/common/brand/zerb-logo.png`(顶部 logo)。
  - **Favicon**:白「Z」合成到 ink(`#050505`)方底,生成 `zerb-favicon-32/180/192.png`,浅/深标签页都清晰;`Layout.astro` 的 icon/apple-touch-icon 指向新文件。
  - **顶部 logo 定位为「签名感」**:手机端纯白 `h-6`(24px,与展开菜单的白字一致),桌面端灰 `md:h-7`(28px,`md:opacity-65` ≈ 导航 `--color-mist`,hover 提亮)。刻意做小,避免抢 Motion/Visual/Code 主标题。(hero 标题 `transform:none`,从未被压,放大只是错觉。)
  - **仓库公开前安全审计**:全历史(56 提交)扫 `.env`/密钥前缀/赋值 → 干净;`.gitignore` 已忽略 `.env*`;本地 `.env` 从未提交。四个公开仓库均开启 **Secret scanning + Push protection**。
  - **仓库改名(统一连字符,主页仓库 `ZerbLion` 不动)**:`net-website→zerb-net`、`zrxl_blog→zero-build-blog`、`nas_monitoring→nas-monitoring`。所有交叉引用已修:本站博客外链/301 指向新 Pages、`zero-build-blog` 的 `app.js`(giscus+取文章)、主页 `update-blog` Action 的 `BLOG_REPO`、各 README。NAS 真实部署路径 `/volume1/docker/nas_monitoring/` 与本地目录 `D:\net\net-website` **保持不变**(那不是仓库名)。
  - **About 补全**:`zerb-net` 描述 + topics + 网址改 `https://zerb.net`;主页仓库描述/网址/topics 补齐。
  - 测试:新博客 Pages `zero-build-blog/` 返回 200、旧地址 404;旧仓库 URL 全部重定向;主页 `update-blog` Action 手动触发成功。

## WordPress 静态导出清理

- 根据当前文件状态推断，移除了部分 WordPress feed/API/archive 输出。
- 根据当前文件状态推断，移除了部分 WordPress runtime 痕迹，例如 `wp-json`、`xmlrpc`、REST nonce scripts 和 speculation rules。
- 根据当前文件状态推断，将部分旧 `https://zerb.net` 绝对链接改为本地/root-relative 链接。
- 根据当前文件状态推断，将旧 WordPress 中文 slug 或归档 URL 迁移到英文 slug 或聚合页 redirect。

## 文档维护

- 2026-06-08 已更新 `README.md`、`AGENTS.md`、`docs/TODO.md`、`docs/DONE.md`，记录当前项目状态、首页头部动效修复边界和后续 agent 操作注意事项。
- 2026-07-05 清理 `docs/TODO.md` 陈旧内容：删除已全部完成的「Astro 重构待办（Phase 1-5）」整段（完成记录见本文件「Astro 重构」节）；删除引用已删除的老根目录静态站、`D:\net` 路径、`reports/`、`tools/local-server.mjs`（4173 端口）的已知问题与「下一步」流程，改为 `cd app && npm run dev`（4321 端口）+ `npm run build` + R2 媒体脚本的现代流程；移除已解决的待办（「AI Ask」命名已统一、仓库已于 2026-06-26 转 public、作品集卡片改版、国内访问、旧 headroom 动效复查）；文档结构清单不再在 TODO 重复（以 `AGENTS.md` 为准）。仍有效的保留：Upstash 限流激活、媒体高清源、项目 `year` 未填、Code 板块、project-bodies 冗余 class 清理、R2 自定义域名、SEO 双线计划。

## 2026-07-04 SEO 修正与根目录清理

- **Search Console 邮件诊断**：三类"未编入索引"原因确认——"自动重定向"= /blog/* 301 到 zero-build-blog（故意）；"备用网页（有规范标记）"= vercel.app 域名 canonical 指向 zerb.net（正确行为）；"404" = 旧 WordPress URL 缺重定向（本轮已补）。"已发现/已抓取-尚未编入索引"15 页属新站正常。
- **sitemap 修正**：`@astrojs/sitemap` 加 filter 排除 `/blog/`（此前 sitemap 里列着一个 301 页面，是 GSC 报"重定向"的来源之一）。
- **WebSite 结构化数据**：`Layout.astro` 新增 WebSite JSON-LD（name "ZERB LION"，alternateName zerbLion/zerblion/Zerb Lion），影响谷歌 SERP 站点名显示。品牌词定为 zerblion/ZERB LION（"zerb"被一位音乐人占据）。
- **旧 URL 重定向迁移**：根目录 `vercel.json` 因 Vercel Root Directory=app 早已不生效，其中 8 条中文 slug、2 条 2017 博客 permalink、2 条 portfolio 翻页此前在线上是 404。已全部迁入 `app/astro.config.mjs` redirects（2017 permalink 直指 zero-build-blog，避免重定向链）。构建产物 `.vercel/output/config.json` 验证 23 条重定向路由全部生成。
- **根目录 WordPress 静态导出删除**（用户决定）：`index.html`、`404.html`、`assets/`、`blog/`、`project/`、`works/`、`resume/`、`media/`（旧图片副本，线上用的是 `app/public/media/`）、`robots.txt`、`sitemap.xml`、`redirects.json`、`vercel.json`、`reports/`，以及一次性迁移工具 `tools/local-server.mjs`、`extract-pages.mjs`、`extract-project-content.mjs`、`i18n-en.mjs`。保留：`tools/` 三个 R2 媒体脚本 + `lib/`、`optimize-media.mjs`、`media-manifest.json`、根 `package.json`。git 历史可全量找回。
- 线上验证：`robots.txt` 200（Cloudflare 托管版，搜索放行、AI 爬虫禁抓）、`sitemap-index.xml` 200。
- **重定向规则修补（同日跟进）**：线上验证发现 Astro 生成的重定向正则 `^/old$` 既不匹配带尾斜杠的旧链接、也不匹配中文 slug 的百分号编码路径（Vercel 按编码后的路径匹配）。新增 `app/patch-vercel-redirects.mjs` 构建后处理（挂在 `npm run build`），把 23 条重定向改写为「非 ASCII 百分号编码 + 尾斜杠可选（`/?$`）」，含防自环保护。

## 2026-07-05 resume 页改版为 about

- **/resume/ → /about/**：路由 `app/src/pages/resume/` 改为 `about/`，导航按钮 Resume→About，标题 `About — ZERB`。旧地址 301 重定向 `/resume/`、`/resume-2/` 均指向 `/about/`（astro.config.mjs）。
- **内容从简历升级为品牌 About 页**：`app/src/migrated/about.html` 顶部新增两段品牌自我介绍（以 "ZERB (Zerb Lion) is a China-based motion designer..." 开头，服务实体 SEO / 抢 "zerb" 词），保留全部履历（vivo MR 眼镜 / JMGO 旗舰 OS / 中国移动 / 格兰仕）、技能、认证；清掉了 WordPress 导出的乱码内联 <style> 和破损 <li>。联系方式改为 Email + Behance(@zerb) + GitHub(@zerbLion)。
- **AI 知识库同步**：`knowledge.ts` 引用 resume.html→about.html，system prompt 中 "resume" 措辞改为 "background / about"。
- 本地构建 + 预览验证：/about/ 200、h1=About、导航显示 About、sitemap 含 /about/ 不含 /resume/、24 条重定向含 resume→about。

## 2026-07-05 About 页调整（品牌/邮箱/隐私）

- **邮箱统一对外用 `zerblion@gmail.com`**：替换全站 5 处旧 `zcbgood@gmail.com`（Footer、AskAI 提示、chat.ts 限流/报错文案、knowledge.ts AI 知识库 CONTACT）。
- **About 开头改为 `ZERB (ZERB LION)`**（原 `Zerb Lion`）。
- **移除对外的 China 地域信息**（用户不想公开所在地）：About 正文、首页 meta description、about 页 meta description 去掉 "China-based"；README/README.zh-CN 的"被墙 Google Fonts""国内加速"改成中性表述（"third-party Google Fonts""global media delivery"）。保留 "China Mobile" 项目名（客户名，非个人地域）。
- **拓宽 dev/coding 定位**（原表述偏前端、太局限）：About 正文的 Code 段与 Skills 的 Development 项改为 full-stack web（TypeScript/Astro/React、serverless API、AI 集成）+ 实时引擎脚本（Unity C#/DOTween、UE Blueprints）；Person schema jobTitle 加 "Developer"；本站自身（含内置 AI 助手）作为 dev 能力实例点出。
- **Vercel Web Analytics 接入（2026-07-05）**：`app` 安装 `@vercel/analytics`，`Layout.astro` head 加 `<Analytics />`（Astro 专用组件，View Transitions 下自动跟踪路由切换）。前提：用户已在 Vercel 后台启用 Web Analytics。数据在 Vercel → 项目 → Analytics 标签查看。

## 2026-07-05 内容冲刺：12 个项目页全部有正文 + 外链项目转轻案例页

- **外链项目转"轻案例页"**（用户拍板）：`[slug].astro` 不再排除 `externalUrl` 项目——vivo XR / LUNA OS Sinus / MotionSheet 现在有自己的详情页（可被谷歌索引），页头带醒目的外链 CTA 按钮（schema 新增 `externalLabel`，默认 "View the product"，MotionSheet 为 "Open the tool"）。首页/works 卡片一律指向站内页（`hrefFor` 简化），`knowledge.ts` 同步。内容只用 About 已公开的信息，vivo 页明确注明 NDA、页面刻意从简。
- **9 个薄页扩写**：vivo-xr（175词，新写）、luna-os-sinus（176词，新写，含 3 个站内互链）、zerb-cc-cd/MotionSheet（139词，新写）、talos-principle（99词）、3d-ui-exploration（144词，链 luna-os-sinus）、diy-motion-elements、dynamic-weather-art（链 luna-os-sinus）、time-garden、wallpaper-universal-design、china-mobile-cave（补两个月工期/C4D+UE4 收尾段）。luna-os-ar-theme 和 nft-asset-design 原本已够厚未动。所有原有图片/视频/外部链接一律保留。
- **md 清理**：12 个 `_Content migration pending_` 占位符（不渲染、易误导）换成指向 `src/project-bodies/<slug>.html` 的注释；vivo-xr / luna-os-sinus 的 summary（= meta description）升级为具体的角色+成果描述。
- 构建验证：12 个项目页全部生成、sitemap 15 URL、works 页无外链卡片、两种 CTA 文案正确。
