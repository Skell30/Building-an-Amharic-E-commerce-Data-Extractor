import os
import pandas as pd
import re

# ==== Settings ====
DATA_DIR = "./data"
OUTPUT_FILE = "./labeled/labeled.conll"
SAMPLE_SIZE = 50  # You can change this
VALID_TAGS = [
    "O",
    "B-Product", "I-Product",
    "B-Price", "I-Price",
    "B-Location", "I-Location",
    "B-Delivery", "I-Delivery",
    "B-Contact", "I-Contact"
]

# Amharic & English keyword examples
LOCATION_KEYWORDS = ["ቦሌ", "ሜክሲኮ", "bole", "mexico"]
DELIVERY_KEYWORDS = ["ዲሊቨሪ", "እናደርሳለን", "Free"]
PROMO_KEYWORDS = ["ቅናሽ", "እንኳን", "Eid"]

# ==== Load Data ====
all_dfs = []
for file in os.listdir(DATA_DIR):
    if file.endswith(".csv"):
        df = pd.read_csv(os.path.join(DATA_DIR, file))
        df['channel'] = file.replace("_messages.csv", "")
        all_dfs.append(df)

df = pd.concat(all_dfs, ignore_index=True)
df = df.rename(columns={"message": "text", "id": "message_id"})
df = df[["message_id", "channel", "text"]]
df.dropna(subset=["text"], inplace=True)
df = df[~df['text'].str.contains('|'.join(PROMO_KEYWORDS), na=False)]
df = df.sample(n=min(SAMPLE_SIZE, len(df)), random_state=42).reset_index(drop=True)

# ==== Label Function ====
def tokenize(text):
    text = re.sub(r"^\.+|\.+$", "", str(text).strip())
    return text.strip().split()

def label_message(row):
    message_id, channel, text = row["message_id"], row["channel"], row["text"]
    print(f"\n🔹 Message ID: {message_id} | Channel: {channel}")
    print(f"🔸 Text: {text}")
    tokens = tokenize(text)
    labeled = []
    prev_tag = ""
    for i, token in enumerate(tokens):
        suggested_tag = "O"
        if token.startswith("@") or re.match(r"^(09|251|\+251)\d{8}$", token.replace("+", "")):
            suggested_tag = "B-Contact"
        elif token in LOCATION_KEYWORDS:
            suggested_tag = "B-Location"
        elif token in DELIVERY_KEYWORDS:
            suggested_tag = "B-Delivery"
        elif re.match(r"^\d{2,3}(,\d{3})?$", token) or token == "ብር":
            suggested_tag = "B-Price"
        elif i == 0:
            suggested_tag = "B-Product"

        print(f"\nToken {i+1}: {token} | Suggested: {suggested_tag}")
        user_tag = input(f"Enter tag [{suggested_tag}]: ").strip()
        tag = user_tag if user_tag else suggested_tag
        while tag not in VALID_TAGS:
            print(f"❌ Invalid tag. Valid options: {', '.join(VALID_TAGS)}")
            tag = input(f"Enter tag for '{token}': ").strip() or suggested_tag

        labeled.append((token, tag))
        prev_tag = tag
    return (message_id, channel, text, labeled)

# ==== Labeling ====
labeled_all = []
for _, row in df.iterrows():
    labeled_all.append(label_message(row))

# ==== Save to CoNLL ====
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for msg_id, channel, text, tokens_tags in labeled_all:
        f.write(f"# message_id: {msg_id}\n")
        f.write(f"# channel: {channel}\n")
        f.write(f"# text: {text}\n")
        for token, tag in tokens_tags:
            f.write(f"{token} {tag}\n")
        f.write("\n")

print(f"\n✅ Saved labeled data to {OUTPUT_FILE}")
