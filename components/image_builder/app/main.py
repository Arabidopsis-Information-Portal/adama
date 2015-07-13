import os

from channelpy import Channel


URI = os.environ.get('BROKER', 'amqp://172.17.42.1:5672')

def main():
    listen = Channel(uri=URI)
    while True:
        job = listen.get()
        args = job['args']
        namespace = job['namespace']
        reply_to = job['reply_to']
        reply_to.put('will process {} and {}'.format(args, namespace))


if __name__ == '__main__':
    main()