import toml
from typing import List


class Config:
    def __init__(self, d):
        self.aws = AWSConfig(d['aws'])
        self.db = DBConfig(d['db'])
        self.web = WebConfig(d['web'])
        self.mail = MailConfig(d['mail'])


class AWSConfig:
    def __init__(self, d):
        self.access_key: str = d['access_key']
        self.secret_key: str = d['secret_key']
        self.sendmail_url: str = d['sendmail_url']


class DBConfig:
    def __init__(self, d):
        self.db_file: str = d['db_file']


class WebConfig:
    def __init__(self, d):
        self.secret_key: str = d['secret_key']
        self.review_session_ttl: int = d['review_session_ttl']


class MailConfig:
    def __init__(self, d):
        self.notification_schedule: str = d['notification_schedule']
        self.reminder_schedule: str = d['reminder_schedule']
        self.spam_threshold: int = d['spam_threshold']
        self.new_requests = MailTemplate(d['new_requests'])
        self.spam_detected = MailTemplate(d['spam_detected'])
        self.reminder = MailTemplate(d['reminder'])
        self.request_approved = MailTemplate(d['request_approved'])
        self.request_denied = MailTemplate(d['request_denied'])


class MailTemplate:
    def __init__(self, d):
        self.to_addresses: List[str] = d['to_addresses']
        self.from_address: str = d['from_address']
        self.subject_template: str = d['subject_template']

        with open(d['body_template_file']) as f:
            self.body_template: str = f.read()


config = Config(toml.load('config.toml'))
