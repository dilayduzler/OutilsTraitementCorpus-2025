from transformers import pipeline
from pathlib import Path
import json

INPUT = Path("./data/generated_questions.json")
OUTPUT= Path("./data/qa_for_training.json")

# QA model
gen_qa = pipeline(
    "text2text-generation",
    model="allenai/unifiedqa-t5-small",
    device=-1
)

# question file
q_items = json.loads(INPUT.read_text(encoding="utf-8"))
flat = []

# generate answers
for item in q_items:
    context  = item["context"]
    question = item["question"]
    qid      = item["source_file"]

    inp = f"question: {question}  context: {context}"
    out = gen_qa(
        inp,
        max_length=100,
        min_length=3,
        do_sample=True,
        top_k=50,
        temperature=0.4,
        top_p=0.9,
        repetition_penalty=1.2,
        no_repeat_ngram_size=2
    )[0]["generated_text"].strip()

    answers = [a.strip() for a in out.split(";") if a.strip()]
    for ans in answers:
        start = context.find(ans)
        if start != -1:
            flat.append({
                "id": qid,
                "question": question,
                "context": context,
                "answer_text": ans,
                "answer_start": start
            })
            print(f"{qid} - {ans}")

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(flat, f, indent=2, ensure_ascii=False)

print(f"written to {OUTPUT}")
print(f"total number of answers: {len(flat)}")