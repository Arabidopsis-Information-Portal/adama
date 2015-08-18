class FetchWorker(object):

    def run(self):
        with Channel(name=SERVICE_NAME,
                     connection_type=RabbitConnection,
                     uri=RABBIT_URI) as listen:
            while True:
                job = listen.get()
                
        


class ProcessWorker(object):
    pass


