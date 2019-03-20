from gmail import GMail, Message
from flask import Flask


class BaseMailer():
    def init_app(self, app: Flask):
        username = app.config.get('GMAIL_USERNAME')
        password = app.config.get('GMAIL_PASSWORD')
        mail_from = app.config.get('MAIL_FROM')

        self.mailer = GMail(f'{mail_from} <{username}>', password)


class Gmail(BaseMailer):
    def init(self):
        self.send_from = None
        self.username = None
        self.password = None

    def send(self, message: Message):
        self.mailer.send(message)
