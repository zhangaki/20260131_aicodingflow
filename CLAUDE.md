# ai-coding-flow.com — SEO 站点

> AI 工具评测、对比、教程英文网站
> 技术栈：Astro 5 + Vercel + Markdown
> 域名：ai-coding-flow.com（非 www，www 已 308 重定向到裸域）
> 目标：2026 年 3 月达到 $300-1000/月（AdSense + Affiliate）

---

## 项目概况 (2026-02-10 更新)

| 维度 | 值 |
|------|------|
| 文章总数 | 249 篇 |
| Indexable 文章 | 214 篇（35 篇 noindex） |
| 平均字数 | 1,730 字 |
| 总字数 | 430,935 字 |
| 内链数量 | ~1,630 条 |
| 工具知识库 | 43 个工具，11 品类 |
| 变现 | AdSense (ca-pub-2874421792108730) + Affiliate（待配置） |
| GA4 | G-DBF2K42BPC（已部署） |
| Git Remote | github.com/zhangaki/20260131_aicodingflow.git |
| 部署 | Vercel（git push origin main 自动部署） |

---

## 当前 SEO 状态 (2026-02-10)

### GSC 数据（有 2 天延迟）
- **索引状态**: sitemap 提交 249 页，已索引 ~0 页（等待 Google 重新抓取）
- **14 天总计**: 5 点击, 1,837 展示, 0.27% CTR, 平均排名 5.8
- **趋势**: 展示量下降中（698→155），但 2/10 做了大规模内容质量升级，效果预计 3-7 天显现

### 有展示的 Top 页面（这些是最重要的页面）
| 页面 slug | 展示 | 排名 | 字数 | 状态 |
|-----------|------|------|------|------|
| offline-ai-remote-work-2026 | 497 | 5.2 | 2,822 | 已优化标题+扩充 |
| multi-agent-orchestration-2026 | 185 | 6.1 | 2,090 | 已优化标题+扩充 |
| synthetic-data-ml-2026 | 152 | 3.5 | 2,432 | 已扩充 |
| multimodal-ai-fusion-2026 | 140 | 6.1 | 2,741 | 已优化标题+扩充 |
| ai-memory-context-persistence-2026 | 114 | 5.1 | 2,636 | 已优化标题+扩充 |
| private-ai-hardware-2026 | 82 | 5.0 | 1,949 | 已扩充 |
| local-llm-knowledge-base-2026 | 80 | 6.6 | 2,495 | 已扩充 |
| apple-intelligence-audit-2026 | 62 | 5.7 | 1,687 | 未优化 |
| legal-ai-bias-auditing-2026 | 53 | 6.8 | 2,222 | 已扩充 |
| generative-ai-pharma-2026 | 50 | 6.3 | 2,505 | 已扩充 |

### Top GSC 搜索词（这些是用户实际搜索的词）
- "ai chatbots with persistent memory across sessions 2026" (13 展示)
- "anthropic ai tools" (10 展示)
- "llama-4-coder model" (9 展示)
- "multi-agent orchestration research 2026" (4 展示)
- "best local offline ai assistant for searching personal files" (多个变体, 2-4 展示)
- "home assistant local ai integration offline 2026" (1 展示)

---

## 内容类型分布

| 类型 | 数量 | 平均字数 | 生成器 |
|------|------|----------|--------|
| Best-of 列表 | 15 | ~1,400 | content_scaling.py |
| 工具评测 (Review) | 44 | ~1,350 | content_scaling.py |
| 使用教程 (How-to) | 43 | ~1,976 | content_scaling.py |
| 工具对比 (PSEO) | 79 | ~1,700 | pseo_generator_v3.py → expand_pseo_articles.py |
| 深度支柱文章 (Pillar) | 5 | ~3,174 | generate_pillar_articles.py |
| GSC 目标文章 | 3 | ~2,253 | generate_gsc_targeted_articles.py |
| 原创深度文章 | ~60 | ~2,100 | 早期生成 + expand_thin_originals.py |

### 字数分布
| 范围 | 数量 | 占比 |
|------|------|------|
| <500 字 | 12 | 4.8%（全部已 noindex）|
| 500-999 字 | 18 | 7.2%（大部分已 noindex）|
| 1000-1499 字 | 41 | 16.5% |
| 1500-1999 字 | 87 | 34.9% |
| 2000-2999 字 | 88 | 35.3% |
| 3000+ 字 | 3 | 1.2% |

---

## 关键目录结构

```
projects/20260131_seo-site/          ← 独立 git 仓库！
├── src/
│   ├── content/blog/                # 249 篇 MD 文章
│   ├── components/
│   │   ├── BaseHead.astro           # GA4 (G-DBF2K42BPC) + AdSense 脚本
│   │   ├── AdPlaceholder.astro      # 广告位组件
│   │   ├── AffiliateCard.astro      # Affiliate 卡片组件
│   │   ├── SocialShare.astro        # 社交分享按钮
│   │   └── Footer.astro
│   ├── layouts/
│   │   └── BlogPost.astro           # 文章布局（含 BlogPosting + FAQPage Schema、广告位、相关文章）
│   └── pages/
│       ├── blog/[...slug].astro     # 文章动态路由
│       ├── contact.astro            # 联系页面
│       ├── about.astro              # 关于页面
│       ├── privacy.md               # 隐私政策
│       └── terms.md                 # 服务条款
├── scripts/
│   ├── content_scaling.py           # 批量生成: Best/Review/Tutorial（43 工具 × 3 类型）
│   ├── pseo_generator_v3.py         # PSEO 对比文章生成器
│   ├── generate_pillar_articles.py  # 5 篇深度支柱文章（3000+ 字）
│   ├── generate_gsc_targeted_articles.py  # 针对 GSC 搜索词的目标文章
│   ├── expand_pseo_articles.py      # 批量扩充薄 PSEO 对比文章
│   ├── expand_top_articles.py       # 扩充 Top GSC 页面
│   ├── expand_thin_originals.py     # 扩充薄原创文章
│   ├── internal_link_builder.py     # 内链构建器（每篇最多 5 条相关链接）
│   ├── fix_pubdates.py              # 分散文章发布日期
│   ├── noindex_thin.py              # 给 <500 字文章加 noindex
│   └── data/
│       └── product_knowledge_base.json  # 43 工具知识库
├── public/assets/                   # 封面图片
├── astro.config.mjs                 # site: https://ai-coding-flow.com
├── vercel.json                      # www→裸域 301 重定向 + 缓存配置
└── CLAUDE.md                        # ← 你正在读的文件
```

### 父仓库脚本（在 super-individual/ 根目录下）

```
scripts/
├── monitoring/
│   ├── gsc_monitor.py               # GSC 数据获取 + 日报 + 全量导出
│   ├── gsc_auto_optimizer.py        # 全自动闭环（GSC→分析→优化→部署）每天 9:30 cron
│   ├── gsc_auth_setup.py            # OAuth 设置
│   └── batch_index_submit.py        # 批量提交 URL 到 Indexing API
├── distribution/
│   ├── reddit_poster.py             # Reddit 分发（需 API keys）
│   ├── twitter_poster.py            # Twitter/X 分发（需 API keys）
│   └── medium_syndicator.py         # Medium 分发（需 API keys）
data/
├── gsc_token.json                   # GSC OAuth token
├── gsc_client_secret.json           # GSC client secret
├── gsc_exports/                     # GSC 导出的 CSV 数据
└── super_individual.db              # SQLite 数据库
```

---

## 开发命令

```bash
# 进入项目目录
cd /Users/mac/code/super-individual/projects/20260131_seo-site

# 开发模式
npx astro dev

# 构建（部署前必须成功，0 错误）
npx astro build

# 部署（推送到 main 自动触发 Vercel）
git push origin main

# 激活 Python 虚拟环境（用于运行脚本）
cd /Users/mac/code/super-individual && source .venv/bin/activate
```

---

## 自动化系统

### GSC 自动优化器（每天 9:30 自动运行）
- **脚本**: `scripts/monitoring/gsc_auto_optimizer.py`
- **Cron**: `30 9 * * * cd /Users/mac/code/super-individual && .venv/bin/python scripts/monitoring/gsc_auto_optimizer.py`
- **pmset**: 每天 9:25 唤醒 Mac
- **功能**: GSC 数据获取 → Gemini 分析 → Meta 优化（最多 3 篇）→ 新文章生成（最多 2 篇）→ 内链更新 → 构建 → 自动 git push 部署
- **限制**: Indexing API 每天 200 次提交配额

### GSC 数据获取
```bash
# 日报
python scripts/monitoring/gsc_monitor.py

# 全量导出（14 天）
python scripts/monitoring/gsc_monitor.py --full-export --days 14

# 批量提交索引（每天限 200 次）
python scripts/monitoring/batch_index_submit.py --limit 200
```

---

## 已完成的优化历史

### 2026-02-08（Phase 0-4）
- [x] 240 篇文章上线（15 Best + 43 Review + 43 Tutorial + 73 PSEO + 66 原创）
- [x] 1,199 条内链
- [x] GA4 部署（G-DBF2K42BPC）
- [x] AdSense 代码部署
- [x] 社交分发脚本编写（reddit/twitter/medium）
- [x] www → 裸域 308 重定向（Vercel Dashboard 配置）
- [x] Schema author 修复（"Alex Zhang" + ai-coding-flow.com/about/）
- [x] 文章日期分散（172 篇从 Feb 08 分散到 Dec 2025 - Feb 2026）
- [x] 14 篇 <500 字文章 noindex
- [x] 21 篇 2027-2030 远未来文章 noindex
- [x] 200 个 URL 提交到 Indexing API

### 2026-02-10（内容质量大升级）
- [x] 7 篇 Top GSC 页面标题/描述优化（精确匹配搜索词）
- [x] 5 篇 Top 页面扩充（900→2500 字）
- [x] 65 篇 PSEO 对比文章扩充（540→1700 字）
- [x] 19 篇原创薄文章扩充（800→2200 字）
- [x] 5 篇深度支柱文章生成（3000+ 字）
- [x] 3 篇 GSC 目标文章生成（anthropic-ai-tools, home-assistant-local-ai, llama-4-coder）
- [x] FAQPage JSON-LD Schema 自动化（BlogPost.astro 自动检测 FAQ 段落）
- [x] 阅读时间改为实际字数计算
- [x] +430 条新内链
- [x] 总字数从 ~295,000 提升到 430,935

---

## 待完成事项（按优先级）

### P0 — 紧急
- [ ] **等待 Google 重新抓取**（2/10 大更新后，预计 3-7 天见效）
- [ ] **Indexing API 剩余 URL**（明天 9:30 自动优化器会继续提交）

### P1 — 高价值
- [ ] **社交分发首次运行** — 需要用户配置 Reddit/Twitter/Medium API keys
- [ ] **Affiliate 链接** — 需要用户注册 Cursor/Jasper/GitHub Copilot 等 affiliate 计划
- [ ] **封面图片多样化** — 186 篇用 blog-fallback.jpg，需 AI 生图或图库

### P2 — 中等价值
- [ ] **扩充剩余薄内容** — 还有 ~18 篇 500-1000 字（大部分已 noindex）
- [ ] **外链建设** — Reddit/HN/ProductHunt 发帖引流
- [ ] **Category Hub 页面** — 按品类创建聚合页，改善站内结构
- [ ] **HowTo Schema** — 给 43 篇 Tutorial 文章加 HowTo 结构化数据

### P3 — 未来
- [ ] **Phase 5 自动迭代引擎** — AdSense API + 收入追踪 + 竞品监控
- [ ] **Core Web Vitals 优化** — 页面速度调优
- [ ] **多语言** — 中文版本

## 内容标准与规范
所有产出的内容（无论是生成还是手动编写）均须符合项目规范：
- **标准详情**: [Article Review & Quality Standards](file:///Users/mac/code/super-individual/projects/20260131_seo-site/.agent/standards/article-quality.md)
- **自动化执行**: 运行 `python scripts/pipeline.py` 进行全量审计与优化。

---

## 内容生成工作流

### 新增工具（端到端）
1. 编辑 `scripts/data/product_knowledge_base.json`，添加工具信息
2. `python scripts/content_scaling.py` — 生成 Review + Tutorial
3. `python scripts/pseo_generator_v3.py` — 生成对比文章
4. `python scripts/internal_link_builder.py` — 更新内链
5. `npx astro build` — 验证 0 错误
6. `git push origin main` — 部署

### 优化已有文章（GSC 数据驱动）
1. `python scripts/monitoring/gsc_monitor.py --full-export --days 14` — 导出数据
2. 分析 `data/gsc_exports/` 中的 CSV — 找高展示低 CTR 的页面
3. 优化标题/描述匹配搜索词，扩充薄内容
4. `python scripts/internal_link_builder.py` → `npx astro build` → `git push origin main`

### 批量扩充薄文章
- PSEO 对比文章: `python scripts/expand_pseo_articles.py`
- 原创文章: `python scripts/expand_thin_originals.py`
- Top GSC 页面: `python scripts/expand_top_articles.py`

---

## 重要注意事项

1. **独立 Git 仓库** — 这个 SEO 站点是独立 git 仓库，push 到自己的 remote，不是父仓库的子模块
2. **父仓库无 remote** — super-individual 仓库仅本地，不要尝试 push
3. **Noindex 文章不要移除** — 2027-2030 远未来文章和 <500 字文章已 noindex
4. **Gemini API** — 内容生成使用 Gemini 2.0 Flash，API key 在 `.env` 文件中（`Gemini_api_key`）
5. **Indexing API 配额** — 每天 200 次，自动优化器会用掉，手动提交前检查配额
6. **构建前必须成功** — `npx astro build` 必须 0 错误才能 push
7. **内链必须更新** — 新增/修改文章后务必运行 `internal_link_builder.py`
