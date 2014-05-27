from celery import Celery

app = Celery('tasks', backend='amqp://', broker='amqp://')

@app.task
def add(x, y):
    return x + y
