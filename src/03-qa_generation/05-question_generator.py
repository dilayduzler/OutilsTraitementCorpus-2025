from transformers import pipeline
from pathlib import Path
import json
import random
import torch

# config
CONTEXTS_DIR = Path("./data/contexts_split")
OUTPUT_PATH = Path("./data/generated_questions.json")
SEED = 42

# gpu control pipeline
qg_pipe = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",
    device_map="auto",
    torch_dtype=torch.float16
)

# all files now
all_txt = list(CONTEXTS_DIR.rglob("*.txt"))
random.seed(SEED)
random.shuffle(all_txt)
selected = all_txt 

# settings and prompt
out = []
for fn in selected:
    ctx = fn.read_text(encoding="utf-8").strip()

    prompt = (
        "Read the paragraph below. It may describe:\n"
        " - a daily schedule (season, day, time and activity),\n"
        " - a heart event (trigger conditions and cutscene details),\n"
        " - or a list of gifts (names and descriptions).\n\n"
        "Generate exactly ONE clear, non-trivial question about this paragraph.\n"
        "Include any relevant season or event name if present.\n\n"
        "Paragraph:\n\"\"\"\n"
        f"{ctx}\n"
        "\"\"\"\n\n"
        "Question:"
    )

    res = qg_pipe(
        prompt,
        max_length=80,
        min_length=10,
        num_beams=4,
        length_penalty=1.3,
        no_repeat_ngram_size=3,
        early_stopping=True
    )[0]["generated_text"].strip()

    out.append({
        "source_file": str(fn.relative_to(CONTEXTS_DIR)),
        "context":     ctx,
        "question":    res
    })
    print(f"{fn.name} - {res}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(f"\n{len(out)} questions saved to: {OUTPUT_PATH}")