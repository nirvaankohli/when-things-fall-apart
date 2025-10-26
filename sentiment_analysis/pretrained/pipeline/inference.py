import torch
from transformers import pipeline


class infer_sentiment:

    def __init__(self):

        self.model_id = "cardiffnlp/twitter-roberta-base-sentiment-latest"

        self.pipe = pipeline(
            task="text-classification",
            model=self.model_id,
            device=0 if torch.cuda.is_available() else -1,
            torch_dtype=torch.float16 if torch.cuda.is_available() else None,
        )

    def batch(self, texts):

        return self.pipe(texts, batch_size=128, truncation=True, top_k=1)

    def single(self, text):

        return self.pipe([text], truncation=True, top_k=1)
    
    def batch_scores(self, texts, neg_alpha=0.85, pos_beta=1.2):
        outs = self.pipe(
            texts,
            batch_size=128,
            truncation=True,
            top_k=None,
            return_all_scores=True
        )
        scores = []
        for dist in outs:
            probs = {d["label"].lower(): d["score"] for d in dist}
            e = (-1.0 * probs.get("negative", 0.0)
                 + 0.0 * probs.get("neutral", 0.0)
                 + 1.0 * probs.get("positive", 0.0))
            if e < 0:
                e = - (abs(e) ** neg_alpha)
            else:
                e = e ** pos_beta
            scores.append(max(-1.0, min(1.0, e)))
        return scores
