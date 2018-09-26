"""
The flask_mail seems not to be working under all circumstances. Not sure why.
I will just implement my own one
"""
import smtplib

from flask import current_app

MAIL_HEADER="""From: {0}
To: {1}
Content-Type: text/html
Subject: {2}

"""


class Mail:

    def __init__(self, verbose=True):
        # get the config
        self.v = verbose
        self.smtp = current_app.config.get('MAIL_SERVER', 'http://localhost')
        self.username = current_app.config.get('MAIL_USERNAME', '')
        self.password = current_app.config.get('MAIL_PASSWORD', '')
        self.sender = current_app.config.get('MAIL_DEFAULT_SENDER')
        self.port = current_app.config.get('MAIL_PORT', 587)

        # Connect
        if self.v:
            print('Connecting %s:%d ...' % (self.smtp, self.port))
        self.server = smtplib.SMTP(self.smtp, self.port)

        # use TLS and connect
        s, m = self.server.starttls()
        if self.v:
            print('[{}]: {}'.format(s, m))
        s, m = self.server.login(self.username, self.password)
        if self.v:
            print('[{}]: {}'.format(s, m))

    def send(self, _to, subject, message):
        body = MAIL_HEADER.format(self.sender, _to, subject)
        body += message

        self.server.sendmail(self.sender, _to, body)

    def close(self):
        self.server.quit()