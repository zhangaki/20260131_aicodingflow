"""
全量内容质量扫描器

扫描所有博客文章，检测：
1. 跨文章重复句子（模板复制粘贴）
2. 虚构定价/统计数据
3. AI 模板填充语句
4. 过时的模型/版本引用

输出每篇文章的风险评分，按严重程度排序。

Usage:
    python content_quality_scan.py              # 扫描并输出报告
    python content_quality_scan.py --export     # 导出 CSV
"""

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
BLOG_DIR = PROJECT_ROOT / "projects" / "20260131_seo-site" / "src" / "content" / "blog"

# ============================================================
# 检测规则
# ============================================================

# AI 模板填充句（精确匹配这些模式说明是模板生成）
TEMPLATE_PATTERNS = [
    r"has carved out a strong position",
    r"in our internal production environment",
    r"the feedback has been overwhelmingly positive",
    r"it's been a mainstay in our stack ever since",
    r"we first discovered .+ during a hackathon",
    r"always verify ai-generated output before using",
    r"alone can justify the subscription cost",
    r"delivers tangible productivity improvements",
    r"genuinely useful in daily workflows",
    r"features that seemed simple on the surface had surprising power",
    r"nobody on the team wanted to switch back",
    r"in today'?s rapidly evolving",
    r"in the (ever-evolving|rapidly changing|fast-paced) (world|landscape) of",
    r"let'?s (dive|delve) (in|into|deeper)",
    r"without further ado",
    r"game.?changer for",
    r"revolutioniz(e|ing|ed) the way",
    r"paradigm shift",
    r"stands out as a (beacon|leader|pioneer)",
    r"whether you'?re a .+ or a .+, this",
]

# 虚构数据模式
FAKE_DATA_PATTERNS = [
    (r"\b\d+% (success|accuracy|improvement|reduction|increase) rate\b", "unverified percentage claim"),
    (r"\bavg rating: \d\.\d/5\b", "fabricated rating"),
    (r"\b(based on|according to) (developer surveys|online reviews|our testing)\b", "vague source attribution"),
    (r"\bcatches .+ (\d+-\d+ hours|days) before\b", "fabricated prediction claim"),
]

# 过时模型引用（2026 年文章不应引用这些为"最新"）
OUTDATED_REFS = [
    (r"claude 3\.5 sonnet.{0,30}(best|top|leading|recommended)", "Claude 3.5 Sonnet listed as current best"),
    (r"grok 2\b(?!.*grok 3)", "References Grok 2 without mentioning Grok 3"),
    (r"gpt-4o?\b(?!.*gpt-4\.\d|.*o1|.*o3)", "References GPT-4 without newer models"),
    (r"model-as-code platform", "Wrong MCP definition (should be Model Context Protocol)"),
]


def extract_body(content):
    """去掉 frontmatter，只留正文"""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2]
    return content


def extract_sentences(text):
    """提取所有有意义的句子（>= 10 词）"""
    # 去掉 markdown 语法
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # links
    text = re.sub(r'[#*>`\-]', ' ', text)  # markdown
    text = re.sub(r'\s+', ' ', text)

    sentences = re.split(r'[.!?]\s+', text)
    return [s.strip().lower() for s in sentences if len(s.split()) >= 10]


def scan_article(filepath, all_sentences_index):
    """扫描单篇文章，返回问题列表和分数"""
    content = filepath.read_text(encoding="utf-8")
    body = extract_body(content)
    body_lower = body.lower()
    slug = filepath.stem

    issues = []
    score = 0  # 越高越差

    # 1. 模板填充检测
    template_hits = 0
    for pattern in TEMPLATE_PATTERNS:
        matches = re.findall(pattern, body_lower)
        if matches:
            template_hits += len(matches)
            issues.append(f"TEMPLATE: '{pattern}' matched {len(matches)}x")
    score += template_hits * 5

    # 2. 虚构数据检测
    fake_hits = 0
    for pattern, desc in FAKE_DATA_PATTERNS:
        matches = re.findall(pattern, body_lower)
        if matches:
            fake_hits += len(matches)
            issues.append(f"FAKE_DATA: {desc} ({len(matches)}x)")
    score += fake_hits * 3

    # 3. 过时引用检测
    outdated_hits = 0
    for pattern, desc in OUTDATED_REFS:
        matches = re.findall(pattern, body_lower)
        if matches:
            outdated_hits += 1
            issues.append(f"OUTDATED: {desc}")
    score += outdated_hits * 4

    # 4. 跨文章重复句子检测
    sentences = extract_sentences(body)
    dup_count = 0
    for sent in sentences:
        if sent in all_sentences_index and len(all_sentences_index[sent]) > 1:
            other_files = [f for f in all_sentences_index[sent] if f != slug]
            if other_files:
                dup_count += 1
    if dup_count > 0:
        issues.append(f"DUPLICATE: {dup_count} sentences found in other articles")
        score += dup_count * 2

    # 5. 内容空洞度（文章太短 or FAQ 占比太高）
    word_count = len(body.split())
    if word_count < 800:
        issues.append(f"THIN: only {word_count} words")
        score += 10

    # 6. 虚构定价检测（$X/month 模式过多）
    price_claims = re.findall(r'\$\d+(?:\.\d+)?/(?:month|mo|user|seat)', body_lower)
    if len(price_claims) > 5:
        issues.append(f"PRICING: {len(price_claims)} price claims (likely unverified)")
        score += len(price_claims)

    return {
        "slug": slug,
        "word_count": word_count,
        "score": score,
        "template_hits": template_hits,
        "fake_hits": fake_hits,
        "outdated_hits": outdated_hits,
        "dup_count": dup_count,
        "issues": issues,
    }


def build_sentence_index(articles):
    """建立跨文章句子索引，用于检测重复"""
    index = defaultdict(set)
    for filepath in articles:
        content = filepath.read_text(encoding="utf-8")
        body = extract_body(content)
        slug = filepath.stem
        for sent in extract_sentences(body):
            index[sent].add(slug)
    return index


def main():
    export = "--export" in sys.argv

    articles = sorted(BLOG_DIR.glob("*.md")) + sorted(BLOG_DIR.glob("*.mdx"))
    if not articles:
        print("未找到文章")
        return

    print(f"扫描 {len(articles)} 篇文章...\n")

    # Phase 1: 建立跨文章句子索引
    print("Phase 1: 建立跨文章句子索引...")
    sentence_index = build_sentence_index(articles)

    # 统计重复句子数量
    dup_sentences = {s: files for s, files in sentence_index.items() if len(files) > 1}
    print(f"  发现 {len(dup_sentences)} 个重复句子（出现在 2+ 篇文章中）")

    # Phase 2: 逐篇扫描
    print("Phase 2: 逐篇扫描...")
    results = []
    for filepath in articles:
        result = scan_article(filepath, sentence_index)
        results.append(result)

    # 按风险分排序
    results.sort(key=lambda x: x["score"], reverse=True)

    # 分级
    critical = [r for r in results if r["score"] >= 20]
    warning = [r for r in results if 10 <= r["score"] < 20]
    ok = [r for r in results if r["score"] < 10]

    # 输出报告
    print("\n" + "=" * 70)
    print(f"  内容质量扫描报告")
    print("=" * 70)
    print(f"\n  总计: {len(articles)} 篇文章")
    print(f"  🔴 严重 (score >= 20): {len(critical)} 篇")
    print(f"  🟡 警告 (score 10-19): {len(warning)} 篇")
    print(f"  🟢 正常 (score < 10):  {len(ok)} 篇")

    if critical:
        print(f"\n{'─' * 70}")
        print("  🔴 严重问题文章（建议 noindex 或重写）:")
        print(f"{'─' * 70}")
        for r in critical:
            print(f"\n  [{r['score']:3d}] {r['slug']}")
            print(f"        {r['word_count']} 词 | 模板:{r['template_hits']} 虚构:{r['fake_hits']} 过时:{r['outdated_hits']} 重复句:{r['dup_count']}")
            for issue in r["issues"][:5]:
                print(f"        - {issue}")

    if warning:
        print(f"\n{'─' * 70}")
        print("  🟡 需关注文章:")
        print(f"{'─' * 70}")
        for r in warning:
            print(f"\n  [{r['score']:3d}] {r['slug']}")
            print(f"        {r['word_count']} 词 | 模板:{r['template_hits']} 虚构:{r['fake_hits']} 过时:{r['outdated_hits']} 重复句:{r['dup_count']}")
            for issue in r["issues"][:3]:
                print(f"        - {issue}")

    # 最常见的重复句子 Top 10
    print(f"\n{'─' * 70}")
    print("  跨文章重复最多的句子 (Top 10):")
    print(f"{'─' * 70}")
    sorted_dups = sorted(dup_sentences.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for sent, files in sorted_dups:
        print(f"\n  [{len(files)} 篇] \"{sent[:80]}...\"")
        print(f"        出现在: {', '.join(sorted(files)[:5])}")
        if len(files) > 5:
            print(f"        ... 还有 {len(files) - 5} 篇")

    # 导出
    if export:
        export_path = PROJECT_ROOT / "data" / "content_quality_scan.csv"
        with open(export_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "slug", "score", "word_count", "template_hits", "fake_hits",
                "outdated_hits", "dup_count", "issues"
            ])
            writer.writeheader()
            for r in results:
                row = {**r, "issues": " | ".join(r["issues"])}
                writer.writerow(row)
        print(f"\n📄 已导出: {export_path}")

    print()


if __name__ == "__main__":
    main()
