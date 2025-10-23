from transformers import pipeline
import torch

model_id = "cardiffnlp/twitter-roberta-base-sentiment-latest"

pipe = pipeline(
    task="text-classification",
    model=model_id,
    device=0 if torch.cuda.is_available() else -1,
    torch_dtype=torch.float16 if torch.cuda.is_available() else None,
)

texts = ["I love programming!", "meh", "this is terrible"]

out = pipe(texts, batch_size=32, truncation=True, top_k=1)

print(out)
