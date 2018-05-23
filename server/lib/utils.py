import pytz

from datetime import datetime


def attach_message(msg, text, color='#F35A00'):
    if isinstance(msg, dict):
        msg['attachments'] = [
            {
                'fallback': text,
                'text': text,
                'color': color
            }
        ]
        return msg
    else:
        return msg


def parse_dtm(x):
    return int(pytz.UTC.localize(datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ')).timestamp())
