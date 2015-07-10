#!/usr/bin/env python

import smtplib
import email
import email.mime.text
import ConfigParser
import os
import traceback
import json

import requests


def config():
    parser = ConfigParser.ConfigParser()
    here = os.path.dirname(os.path.abspath(__file__))
    parser.read(os.path.join(here, 'monitor.conf'))
    return parser


CONFIG = config()


class SendMail(object):

    def __init__(self, smarthost, port, user, password):
        """Create a SMTP object connected to smarthost.

        :type smarthost: str
        :type port: int
        :type user: str
        :type password: str
        :rtype: None
        """

        self.smarthost = smarthost
        self.port = port
        self.user = user
        self.password = password

        self.smtp = smtplib.SMTP_SSL(self.smarthost, self.port)
        self.smtp.login(self.user, self.password)

    def send(self, addresses, subject, message):
        """Send a message to all addresses.

        :type addresses: List[str]
        :type subject: str
        :type message: str
        :rtype: None
        """

        from_ = 'Adama <no-reply@tacc.utexas.edu>'
        mime = email.mime.text.MIMEText(message)
        mime['Subject'] = subject
        mime['From'] = from_
        mime['To'] = ', '.join(addresses)
        self.smtp.sendmail(from_, addresses, mime.as_string())
        self.smtp.quit()


def sendmail(subject, message):
    """Send a message to all addresses using config.

    :type subject: str
    :type message: str
    :rtype: None
    """
    mail = SendMail(CONFIG.get('mail', 'smarthost'),
                    CONFIG.getint('mail', 'port'),
                    CONFIG.get('mail', 'user'),
                    CONFIG.get('mail', 'password'))
    notify_to = [addr.strip()
                 for addr in CONFIG.get('monitor', 'notify').split(',')]
    mail.send(notify_to, subject, message)


def main():
    headers = {
        'Authorization': 'Bearer {}'.format(CONFIG.get('api', 'token'))
    }
    try:
        health = requests.get(CONFIG.get('api', 'url') + '/health',
                              headers=headers).json()
        if health['status'] != 'success':
            sendmail('status = error, while checking health',
                     json.dumps(health, indent=4))
            return
        if health['result']:
            sendmail('there are unhealthy workers',
                     json.dumps(health['result'], indent=4))
            return
    except Exception:
        # any error here must be notified
        sendmail('Exception while checking health', traceback.format_exc())
        return


if __name__ == '__main__':
    main()
