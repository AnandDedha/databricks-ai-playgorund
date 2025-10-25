from transformers import pipeline
analyzer = pipeline("sentiment-analysis")
def analyze_sentiment(review: str) -> str:
    return analyzer(review)[0]['label']
print(analyze_sentiment("The delivery was fast and smooth!"))
