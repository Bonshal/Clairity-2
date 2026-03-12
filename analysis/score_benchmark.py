"""Score the benchmark results — output to file."""
import asyncio
import numpy as np
import sys

RESULTS = {
    "1. TF-IDF bigrams": [
        "ai tools", "tools like", "ai agents", "using ai", "use ai",
        "tools ai", "ai generated", "ai tools like", "using ai tools", "ai powered",
        "open source", "using tools", "ai coding", "ai tool", "coding tools",
        "real world", "code review", "claude code", "new ai", "tools help",
    ],
    "2. YAKE statistical": [
        "tools makes research", "tools guilds building", "on-chain tools makes",
        "digital power tools", "agents internal tools", "building tools anymore",
        "agent type tools", "type tools agent", "tools agent recommended",
        "detection tools confirm", "building tools aide", "tools automation productivity",
        "unstable tools mwx", "tools empowering innovation", "reporting tools make",
        "play tools work", "source tools full", "building real capabilities",
        "video tools optimized", "tools open-source platform",
    ],
    "4. KeyBERT semantic": [
        "ai builders looking", "futuretech technews aitools",
        "lantern accessory ai", "quality effortlessly leveraging",
        "apple intelligence", "features emerging fully", "haloterm hardware",
        "vibe xai tools", "tech robotics emollick", "digitally generated visual",
        "management tools 2026", "new craft", "minimax_ai kimi_moonshot",
        "adoption speculation aiforsmes", "similar clips fabricated",
        "growth tech food", "runway ml luma", "clear authenticity automated",
        "retouched photos melissa", "shawnife founder insight",
    ],
    "5. BERTopic clusters": [
        "ai tools for", "mwxai smes mwx", "crypto is defi",
        "aigenerated image photo", "aigenerated video appears",
        "security agents and", "xai to on", "was variant to",
        "etv se pradesh", "spam calls filters", "amp tools betting",
        "vibe coding is", "editing music take", "saas cloudfuze cloudmigration",
        "xs report accounts", "konnexworld robots stablecoins",
        "webmcp browser agents", "revenues indian services",
        "meta earnings fcf", "web3 hub ainft",
    ],
}

NICHE_TERMS = [
    "AI tools", "content creation", "market research",
    "social media analytics", "machine learning",
    "competitor analysis", "trend detection",
    "startup", "SaaS", "automation",
]

JUNK_WORDS = {
    "code", "model", "ai", "ml", "llm", "app", "tool", "data", "web",
    "use", "new", "best", "top", "good", "great", "real", "don", "doesn",
    "get", "make", "way", "lot", "time", "thing", "stuff", "kind",
    "people", "work", "need", "help", "want", "like", "know", "think",
}


def specificity(kws):
    return sum(1 for k in kws if len(k.split()) >= 2) / len(kws)


def junk_rate(kws):
    junk = 0
    for kw in kws:
        words = kw.lower().split()
        if len(words) == 1 and words[0] in JUNK_WORDS:
            junk += 1
    return junk / len(kws)


def niche_relevance(kws, niche):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    kw_emb = model.encode(kws, show_progress_bar=False)
    niche_emb = model.encode(niche, show_progress_bar=False)
    kw_norm = kw_emb / np.linalg.norm(kw_emb, axis=1, keepdims=True)
    niche_norm = niche_emb / np.linalg.norm(niche_emb, axis=1, keepdims=True)
    sim = kw_norm @ niche_norm.T
    return float(np.mean(sim.max(axis=1)))


def human_quality(kws):
    good = 0
    for kw in kws:
        words = kw.split()
        if 2 <= len(words) <= 4 and "_" not in kw and len(kw) > 5:
            good += 1
    return good / len(kws)


def main():
    lines = []
    lines.append("BENCHMARK SCORES")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"{'Technique':<25} {'Specificity':>12} {'Junk%':>8} {'NicheSim':>10} {'HumanQ':>8} {'SCORE':>8}")
    lines.append("-" * 75)

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    niche_emb = model.encode(NICHE_TERMS, show_progress_bar=False)
    niche_norm = niche_emb / np.linalg.norm(niche_emb, axis=1, keepdims=True)

    best_name = ""
    best_score = -1

    for name, kws in RESULTS.items():
        s = specificity(kws)
        j = junk_rate(kws)
        h = human_quality(kws)

        kw_emb = model.encode(kws, show_progress_bar=False)
        kw_norm = kw_emb / np.linalg.norm(kw_emb, axis=1, keepdims=True)
        sim = kw_norm @ niche_norm.T
        r = float(np.mean(sim.max(axis=1)))

        score = (s * 0.25) + (r * 0.30) + (h * 0.25) + ((1 - j) * 0.20)
        
        if score > best_score:
            best_score = score
            best_name = name

        lines.append(f"{name:<25} {s:>11.0%} {j:>7.0%} {r:>9.2f} {h:>7.0%} {score:>7.2f}")

    lines.append("-" * 75)
    lines.append("")
    lines.append(f"WINNER: {best_name} (score: {best_score:.2f})")
    lines.append("")
    lines.append("Metrics explanation:")
    lines.append("  Specificity: % multi-word phrases (higher = more descriptive)")
    lines.append("  Junk%: % single generic words (lower = better)")
    lines.append("  NicheSim: Avg semantic similarity to niche terms (higher = more relevant)")
    lines.append("  HumanQ: % keywords a human would find useful as dashboard labels (higher = better)")
    lines.append("  SCORE: Weighted composite (higher = better)")

    output = "\n".join(lines)
    with open("benchmark_results.txt", "w") as f:
        f.write(output)
    print(output)

main()
