from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

app = Celery(
    "user_worker",
    broker=f"{os.getenv('CELERY_BROKER_URL')}",
)

def publish_event(event):
    app.send_task("graphql_subscriber.process_event", args=[event])