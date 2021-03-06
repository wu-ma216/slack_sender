import email
import textwrap
from slack_sdk.webhook import WebhookClient

class NotificationData:

    def __init__(self, stdin, url):
        # セッターを使う。はず。
        self.raw_mail = stdin
        self.url = url

    # 受信したメール本文。
    @property
    def raw_mail(self):
        return self._raw_mail

    @raw_mail.setter
    def raw_mail(self, raw_mail):
        self._raw_mail = raw_mail

    # Slack API URL
    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    def generate_message(self):
        # メールをパース
        msg = email.message_from_string(self.raw_mail)

        format_list = { "date": msg.get('Date'),
                        "from": msg.get('From'),
                        "return_path": msg.get('Return-Path'),
                        "x_original_to": msg.get('X-Original-To'),
                        "to": msg.get('To'),
                        "subject": msg.get('Subject') }

        # 本文以外を作る
        body = textwrap.dedent("""
        Date: {date}
        From: {from}
        Return-Path: {return_path}
        X-Original-To: {x_original_to}
        To: {to}
        Subject: {subject}

        # body
        -------------------------------
        """.format(**format_list)).strip()

        # 本文を作って連結する。
        body = body + '\n' + msg.get_payload(decode = False) + '\n' + '-------------------------------'

        return body

    def send_slack(self):

        text = self.generate_message()
        url = self.url

        webhook = WebhookClient(url)
        
        response = webhook.send(text = text)
 
        assert response.status_code == 200
        assert response.body == "ok"
