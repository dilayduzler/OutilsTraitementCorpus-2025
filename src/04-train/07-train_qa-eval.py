from datasets import DatasetDict, Dataset
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, TrainingArguments, Trainer, pipeline
from sklearn.model_selection import train_test_split
from collections import defaultdict
import json
import os
import evaluate

# config
DATA_PATH = "./data/qa_for_training.json"
OUTPUT_DIR = "./models"
MODEL_NAME = "deepset/roberta-base-squad2"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    raw = json.load(f)

# stratified split based on the number of examples for each NPC
buckets = defaultdict(list)
for ex in raw:
    npc = ex["id"].split("/")[0]
    buckets[npc].append(ex)

train_list, eval_list = [], []
for npc, items in buckets.items():
    if len(items) < 5:
        train_list.extend(items)
    else:
        tr, ev = train_test_split(items, test_size=0.2, random_state=42)
        train_list.extend(tr)
        eval_list.extend(ev)

dataset = DatasetDict({
    "train": Dataset.from_list(train_list),
    "eval": Dataset.from_list(eval_list)
})

# model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForQuestionAnswering.from_pretrained(MODEL_NAME)

# preprocessing function
def preprocess_function(examples):
    tokenized = tokenizer(
        examples["question"],
        examples["context"],
        truncation="only_second",
        max_length=512,
        stride=128,
        return_overflowing_tokens=True,
        return_offsets_mapping=True,
        padding="max_length"
    )
    sample_map   = tokenized.pop("overflow_to_sample_mapping")
    offsets_map  = tokenized.pop("offset_mapping")

    starts, ends = [], []
    for i, offsets in enumerate(offsets_map):
        sample_idx   = sample_map[i]
        start_char   = examples["answer_start"][sample_idx]
        end_char     = start_char + len(examples["answer_text"][sample_idx])
        seq_ids      = tokenized.sequence_ids(i)

        s_idx = e_idx = 0
        for idx, (s, e) in enumerate(offsets):
            if seq_ids[idx] != 1:
                continue
            if s <= start_char < e:
                s_idx = idx
            if s < end_char <= e:
                e_idx = idx
        starts.append(s_idx)
        ends.append(e_idx)

    tokenized["start_positions"] = starts
    tokenized["end_positions"] = ends
    return tokenized

remove_cols = ["id", "question", "context", "answer_text", "answer_start"]
tokenized_dataset = DatasetDict({
    "train": dataset["train"].map(preprocess_function, batched=True, remove_columns=remove_cols),
    "eval":  dataset["eval"].map(preprocess_function, batched=True, remove_columns=remove_cols),
})

# training model 
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    eval_strategy="epoch",
    save_strategy="no",
    logging_strategy="epoch",
    learning_rate=2e-5,
    num_train_epochs=3,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    weight_decay=0.01,
    fp16=False,
    dataloader_num_workers=0,
    report_to="none",
    disable_tqdm=False,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["eval"],
    tokenizer=tokenizer
)

trainer.train()

# EVAL -------------------

trainer_results = trainer.evaluate()

# f1 and exact match

qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)
metric = evaluate.load("squad")

for example in dataset["eval"]:
    context  = example["context"]
    question = example["question"]
    answers  = [example["answer_text"]]
    answer_start = example["answer_start"]

    prediction = qa_pipeline({
        "context": context,
        "question": question
    })["answer"]

    metric.add(
        prediction={"id": example["id"], "prediction_text": prediction},
        reference={"id": example["id"], "answers": {"text": answers, "answer_start": [answer_start]}}
    )

qa_scores = metric.compute()

combined_results = {**trainer_results, **qa_scores}

eval_path = os.path.join(OUTPUT_DIR, "eval_results.json")
with open(eval_path, "w", encoding="utf-8") as f:
    json.dump(combined_results, f, indent=2, ensure_ascii=False)


# SAVE -----------------
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)