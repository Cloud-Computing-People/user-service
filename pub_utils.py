from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

app = Celery(
    "user_worker",
    broker="redis://localhost:6379/0",
)

def publish_event(event):
    app.send_task("graphql_subscriber.process_event", args=[event])