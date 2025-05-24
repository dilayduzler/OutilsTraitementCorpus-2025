import re
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from wordcloud import WordCloud

# config
CONTEXTS_DIR = Path("./data/contexts_split")
FIGURES_DIR  = Path("./figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def load_corpus(contexts_dir: Path) -> pd.DataFrame:
    records = []
    for npc_dir in contexts_dir.iterdir():
        if not npc_dir.is_dir(): continue
        npc = npc_dir.name
        for f in npc_dir.glob(f"{npc}-*.txt"):
            label     = f.stem.split("-",1)[1]
            category  = label.split("_")[0]
            text      = f.read_text(encoding="utf-8")
            tokens    = re.findall(r"\w+", text.lower())
            sentences = [s for s in re.split(r"[.!?]", text) if s.strip()]
            records.append({
                "npc": npc,
                "category": category,
                "text": text,
                "tokens": tokens,
                "num_tokens": len(tokens),
                "num_sentences": len(sentences)
            })
    return pd.DataFrame(records)

df = load_corpus(CONTEXTS_DIR)

# type token ratio
df["ttr"] = df.apply(
    lambda r: len(set(r["tokens"]))/r["num_tokens"] if r["num_tokens"]>0 else 0,
    axis=1
)
fig, ax = plt.subplots(figsize=(8,5))
df.boxplot(
    column="ttr", by="category", ax=ax, patch_artist=True,
    boxprops=dict(facecolor="lightblue", edgecolor="navy"),
    medianprops=dict(color="red"),
    whiskerprops=dict(color="navy"),
    capprops=dict(color="navy"),
    flierprops=dict(marker="o", markerfacecolor="gray", markersize=4)
)
ax.set_title("Lexical Diversity (Type/Token Ratio) by Category")
ax.set_xlabel("Category")
ax.set_ylabel("Type/Token Ratio")
ax.set_ylim(0,1.05)
fig.suptitle("")
fig.tight_layout()
fig.savefig(FIGURES_DIR/"ttr_by_category.png")
plt.close(fig)

# heatmap for schedules
sched = df[df["category"]=="schedule"]
heat_rows = []
for _, r in sched.iterrows():
    for m in re.finditer(r"(\d{1,2}):\d{2}\s*(AM|PM)", r["text"]):
        h, ampm = int(m.group(1)), m.group(2)
        if ampm=="PM" and h!=12: h+=12
        if ampm=="AM" and h==12: h=0
        heat_rows.append({"npc": r["npc"], "hour": h})
heat_df = pd.DataFrame(heat_rows)

if not heat_df.empty:
    pivot = heat_df.pivot_table(index="hour", columns="npc", aggfunc="size", fill_value=0)
    fig, ax = plt.subplots(figsize=(10,6))
    im = ax.imshow(pivot, aspect="auto", cmap="YlGnBu", origin="lower")
    fig.colorbar(im, label="Event Count")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
    ax.set_yticks(range(24))
    ax.set_yticklabels(range(24))
    ax.set_title("Schedule Activity Heatmap: Hour vs NPC")
    ax.set_xlabel("NPC")
    ax.set_ylabel("Hour of Day")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR/"schedule_heatmap.png")
    plt.close(fig)
else:
    print("No schedule found")


# contexts count for each npc
counts = df.groupby("npc").size().sort_index()
fig, ax = plt.subplots(figsize=(8,4))
ax.bar(counts.index, counts.values, color="skyblue", edgecolor="black")
ax.set_title("Total Number of Contexts per NPC")
ax.set_xlabel("NPC")
ax.set_ylabel("Context Count")
ax.set_xticklabels(counts.index, rotation=45, ha="right")
fig.tight_layout()
fig.savefig(FIGURES_DIR/"contexts_per_npc.png")
plt.close(fig)

# category word clouds
for cat in df["category"].unique():
    text = " ".join(df[df["category"]==cat]["text"])
    wc   = WordCloud(width=400, height=300, background_color="white").generate(text)
    
    fig, ax = plt.subplots(figsize=(5,4))
    ax.imshow(wc, interpolation="bilinear")  
    ax.axis("off")
    ax.set_title(f"Word Cloud: {cat}", fontsize=12)
    fig.tight_layout()
    
    fig.savefig(FIGURES_DIR / f"wordcloud_{cat}.png")
    plt.close(fig)