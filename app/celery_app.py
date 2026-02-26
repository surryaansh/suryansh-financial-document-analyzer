import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "financial_analyzer",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.worker_tasks"],  # 👈 Explicitly register task module
)

# Serialization settings
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]

# Track task state transitions (PENDING → STARTED → SUCCESS)
celery_app.conf.task_track_started = True