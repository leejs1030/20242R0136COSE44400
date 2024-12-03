import boto3
from textblob import TextBlob
import datetime
import json

student_number = "2020320125"

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(f"reviews-{student_number}")
ses = boto3.client("ses")


def get_sentiment(polarity):
    if polarity >= 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    # else:
    #     return "Neutral"


def lambda_handler(event, context):
    body = json.loads(event["body"])
    user_name = body["user_name"]
    review_text = body["review"]
    timestamp = datetime.datetime.now().isoformat()

    # Sentiment Analysis
    polarity = TextBlob(review_text).sentiment.polarity
    """
    Todo1: Use the Polarity value to determine the sentiment of the review, 
    with the standard set to 0.
    """
    sentiment = get_sentiment(polarity)

    # Save to DynamoDB
    table.put_item(
        Item={
            "user_name": user_name,
            "review": review_text,
            "timestamp": timestamp,
            "sentiment": sentiment,
        }
    )

    # Send Email for Positive Reviews
    my_email = "leejs1030@korea.ac.kr"
    if sentiment == "Positive":
        ses.send_email(
            Source=my_email,
            Destination={"ToAddresses": [my_email]},
            Message={
                "Subject": {"Data": f"Positive Review from {user_name}"},
                "Body": {"Text": {"Data": f"{user_name} wrote: {review_text}"}},
            },
        )

    return {"statusCode": 200, "body": f"Review processed for {user_name}"}
