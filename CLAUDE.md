# ai-coding-flow.com — SEO 站点

> AI 工具评测、对比、教程网站
> 技术栈：Astro + Vercel + Markdown
> 域名：ai-coding-flow.com

---

## 项目概况

| 维度 | 值 |
|------|------|
| 文章总数 | 240 篇 |
| 工具知识库 | 43 个工具，11 品类 |
| 内链数量 | 1199 条 |
| 变现 | AdSense (ca-pub-2874421792108730) + Affiliate |
| Git Remote | github.com/zhangaki/20260131_aicodingflow.git |
| 部署 | Vercel (git push 自动部署) |

---

## 内容类型

| 类型 | 数量 | 模板/生成器 | 示例 slug |
|------|------|-------------|-----------|
| Best-of 列表 | 15 | content_scaling.py | best-ai-tools-for-coding-2026 |
| 工具评测 | 43 | content_scaling.py | cursor-review-2026 |
| 使用教程 | 43 | content_scaling.py | how-to-use-cursor-for-building-a-full-stack-app-from-scratch-2026 |
| 工具对比 (PSEO) | 73 | pseo_generator_v3.py | cursor-vs-github-copilot-2026 |
| 原创深度 | 66 | 手动/早期生成 | ai-latency-optimization-2026 |

---

## 关键目录

```
projects/20260131_seo-site/
├── src/
│   ├── content/blog/          # 240 篇 MD 文章
│   ├── components/
│   │   ├── BaseHead.astro     # GA4 + AdSense 脚本
│   │   ├── AdPlaceholder.astro # 广告位组件
│   │   ├── AffiliateCard.astro # Affiliate 卡片
│   │   └── Footer.astro
│   ├── layouts/
│   │   └── BlogPost.astro     # 文章布局（含广告位）
│   └── pages/
│       ├── contact.astro      # 联系页面
│       └── privacy.md
├── scripts/
│   ├── content_scaling.py     # 批量生成: Best/Review/Tutorial
│   ├── pseo_generator_v3.py   # PSEO 对比文章生成
│   ├── internal_link_builder.py # 内链构建器
│   └── data/
│       └── product_knowledge_base.json  # 43 工具知识库
└── public/assets/             # 封面图片
```

---

## 开发命令

```bash
# 开发模式
npx astro dev

# 构建（部署前必须成功）
npx astro build

# 部署（推送到 main 自动触发 Vercel）
git push origin main
```

---

## 内容生成工作流

### 新增工具
1. 编辑 `scripts/data/product_knowledge_base.json`，添加工具信息
2. 运行 `python scripts/content_scaling.py` 生成 Review + Tutorial
3. 运行 `python scripts/pseo_generator_v3.py` 生成对比文章
4. 运行 `python scripts/internal_link_builder.py` 更新内链
5. `npx astro build` 验证无错误
6. `git push origin main` 部署

### 批量优化已有文章
1. GSC 数据分析（`gsc_auto_optimizer.py` 每日自动执行）
2. 识别排名 5-15 的关键词，优化对应文章的 title/meta/内容
3. 重新构建部署

---

## 待完成事项

- [ ] GA4 Measurement ID (G-XXXXXXXXXX) — 替换 BaseHead.astro 占位符
- [ ] Affiliate 链接 — 注册各工具 affiliate 计划后批量替换
- [ ] 社交分发首次运行 — 配置 Reddit/Twitter/Medium API keys
- [ ] Phase 5 自动迭代引擎 — 等索引数据积累

---

## 注意事项

- 文章 frontmatter 必须包含 `title`, `description`, `pubDate`, `category`
- 2027-2030 远未来文章已设 `noindex: true`，不要移除
- AdSense Publisher ID: `ca-pub-2874421792108730`，已在 BaseHead.astro 中
- HCU 审核工具: `skills/core/content-reviewer/scripts/auditor_hcu.py`
- 新文章生成后务必运行 `internal_link_builder.py` 更新内链网络
