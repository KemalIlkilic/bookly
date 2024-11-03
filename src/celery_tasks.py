from celery import Celery
from src.mail import mail, create_message
from asgiref.sync import async_to_sync

c_app = Celery()

c_app.config_from_object("src.config")

#for celery worker
#celery -A src.celery_tasks.c_app worker
#for flower
#celery -A src.celery_tasks.c_app flower

@c_app.task()
def send_email(recipients: list[str], subject: str, body: str):

    message = create_message(recipients=recipients, subject=subject, body=body)

    #This creates a new synchronized function from the async one
    sync_send_message = async_to_sync(mail.send_message)
    sync_send_message(message)
    print("Email sent")