import os, re, json, random
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from pathlib import Path

# Data manipulation libraries
import numpy as np
import pandas as pd

# Machine learning libraries
from joblib import dump, load
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)

from sklearn.utils import Bunch


def lprint(if_print: bool, *args):

    if if_print:
        print(*args)


def divider(if_print: bool = True):

    if if_print:
        print("=" * 50)


def line(if_print: bool = True):

    if if_print:
        print("\n")


def print_between_dividers(if_print: bool, *args):

    divider(if_print)
    lprint(if_print, *args)
    divider(if_print)
    print("\n")


def set_seed(seed: int = 67):

    random.seed(seed)
    np.random.seed(seed)


@dataclass
class TrainConfig:
    "Just all da stuff i need for training"

    LOGGING: bool = True
    MODEL_REPORTS_DIR: str = "model_reports"
    ROOT_DIR = Path(__file__).parent.parent
    DATA_PATH: str = ROOT_DIR / "data/data.csv"
    CLEANED_OUT: str = ROOT_DIR / "data/cleaned_data.csv"
    MAX_FEATURES: int = 200_000
    MIN_DF: int = 5
    NGRAM_RANGE: tuple[int, int] = (1, 2)
    TEST_SIZE: float = 0.2
    PENALTY: str = "elasticnet"
    L1_RATIO: float = 0.25
    C: float = 1.0
    SOLVER: str = "saga"
    MAX_ITER: int = 2000
    CLASS_WEIGHT: str = "balanced"
    LABEL_MAP: dict = None


# making vectorizer(basically converting text to numbers)
def build_vectorizer(config: TrainConfig) -> TfidfVectorizer:

    vec = TfidfVectorizer(
        tokenizer=str.split,
        lowercase=False,
        min_df=config.MIN_DF,
        ngram_range=config.NGRAM_RANGE,
        max_features=config.MAX_FEATURES,
        strip_accents="unicode",
        sublinear_tf=True,
    )

    return vec


def train_model(x_train, y_train, config: TrainConfig) -> LogisticRegression:

    clf = LogisticRegression(
        penalty=config.PENALTY,
        l1_ratio=config.L1_RATIO,
        C=config.C,
        solver=config.SOLVER,
        max_iter=config.MAX_ITER,
        class_weight=config.CLASS_WEIGHT,
        n_jobs=-1,
        verbose=1,
    )
    clf.fit(x_train, y_train)
    return clf


def evaluate_model(
    model: LogisticRegression,
    x_test,
    y_test,
    split_name: str = "Test",
    print_report: bool = True,
    return_report: bool = False,
) -> Dict[str, Any]:

    y_pred = model.predict(x_test)
    accuracy = accuracy_score(y_test, y_pred)

    unique_labels = np.unique(y_test)
    if len(unique_labels) == 2:
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, y_pred, average="binary", zero_division=0
    )
    else:

        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, y_pred, average="macro", zero_division=0
        )

    if print_report:

        print(f"\n {split_name} Set Evaluation Report:\n")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1-Score: {f1:.4f}\n")

        print("Classification Report:")
        print(classification_report(y_test, y_pred, zero_division=0))

        print("Confusion Matrix:")
        print(confusion_matrix(y_test, y_pred))

    if return_report:

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
        }


def save_model_report(
    vec: TfidfVectorizer, model: LogisticRegression, config: TrainConfig
):

    os.makedirs(config.MODEL_REPORTS_DIR, exist_ok=True)

    dump(vec, os.path.join(config.MODEL_REPORTS_DIR, "vectorizer.joblib"))
    dump(model, os.path.join(config.MODEL_REPORTS_DIR, "model.joblib"))

    label_map = {"negative": 0, "positive": 4}

    with open(
        os.path.join(config.MODEL_REPORTS_DIR, "label_map.json"), "w", encoding="utf-8"
    ) as f:

        json.dump(label_map, f, indent=2)

    import yaml

    with open(
        os.path.join(config.MODEL_REPORTS_DIR, "config.yaml"), "w", encoding="utf-8"
    ) as f:

        yaml.safe_dump(asdict(config), f, sort_keys=False)

    print(f"\n[ok] Saved artifacts to: {config.MODEL_REPORTS_DIR}")


def main():

    config = TrainConfig()
    set_seed()

    total_parts = 5

    if_print = config.LOGGING

    print_between_dividers(
        if_print, "Sentiment Analysis Model Training On Sentiment 140"
    )

    line(if_print)
    line(if_print)

    print_between_dividers(if_print, f"[1/{total_parts}] Loading and preparing data...")

    df = pd.read_csv(config.CLEANED_OUT)

    lprint(if_print, f"Success!   \n Total samples: {len(df)} \n \n")

    print_between_dividers(
        if_print, f"[2/{total_parts}] Splitting into train and test sets..."
    )

    X_train, X_test, y_train, y_test = train_test_split(
        df["cleaned_tweet"].values,
        df["sentiment"].values,
        test_size=config.TEST_SIZE,
        random_state=67,
        stratify=df["sentiment"].values,
    )

    lprint(
        if_print,
        f"Success!   \n Train samples: {len(X_train)} \n Test samples: {len(X_test)} \n \n",
    )

    print_between_dividers(if_print, f"[3/{total_parts}] Building vectorizer...")

    vec = build_vectorizer(config)

    lprint(if_print, "Success! \n")

    X_train_vec = vec.fit_transform(X_train)
    X_test_vec = vec.transform(X_test)

    lprint(if_print, "Vectorization complete! \n")

    print_between_dividers(if_print, f"[4/{total_parts}] Training model...")
    model = train_model(X_train_vec, y_train, config)

    lprint(if_print, "Model training complete! \n")

    print_between_dividers(if_print, f"[5/{total_parts}] Evaluating model...")

    evaluate_model(model, X_train_vec, y_train, split_name="Train")
    evaluate_model(model, X_test_vec, y_test, split_name="Test")

    lprint(if_print, "Evaluation complete! \n")

    print_between_dividers(if_print, f"[6/{total_parts}] Saving artifacts...")

    save_model_report(vec, model, config)

    lprint(if_print, "All done!")


if __name__ == "__main__":

    main()
