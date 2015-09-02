    
def main():
    with Channel(name='worker_manager', persist=False,
                 connection_type=RabbitConnection,
                 uri=RABBIT_URI) as listen:
        while True:
            job = listen.get()
            print('will process job:', flush=True)
            print(job, flush=True)
            t = threading.Thread(target=process, args=(job,))
            t.start()


def process(job):
    """
    :type job: Dict
    """

    with job['reply_to'] as reply_to:
        try:
            args = job['value']['args']
        except KeyError:
            error("missing 'args': {}".format(job),
                  400, reply_to)
            return

        guid = uuid.uuid4().hex
        try:
            srv = Service(guid, **args)
            if srv.identifier in stores.service_store:
                raise ServiceException('service {} already registered'
                                       .format(srv.identifier))
            stores.registration_store.mutex_acquire(srv.identifier)
            reply_to.put({
                'message': guid,
                'status': 'success'
            })
            srv.register()
        except ServiceException as exc:
            reply_to.put({
                'message': str(exc),
                'status': 'error'
            })
        except StoreMutexException:
            reply_to.put({
                'message': ('service "{}" is in process of registration'
                            .format(srv.identifier)),
                'status': 'error'
            })
        finally:
            stores.registration_store.mutex_release(srv.identifier)


if __name__ == '__main__':
    main()
