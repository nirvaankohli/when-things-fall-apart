from pretrained.pipeline.inference import infer_sentiment


def test_sentiment_pipeline():

    sentiment_infer = infer_sentiment()

    texts = ["I love programming!", "meh", "this is terrible"]

    batch_output = sentiment_infer.batch(texts)
    single_output = sentiment_infer.single("I love programming!")
    batch_output_scores = sentiment_infer.batch_scores(texts)
    print("Batch Output:", batch_output)
    print("Single Output:", single_output)
    print("Batch Scores:", batch_output_scores)


if __name__ == "__main__":

    test_sentiment_pipeline()
