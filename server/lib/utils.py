import os
import logging
import pytz


from datetime import datetime

logger = logging.getLogger('utils')


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


def read_env(env_file):
    logger.info('Trying to read %s environment file', env_file)
    if os.path.exists(env_file):
        logger.info('Located environment file. Reading from it.')
        with open(env_file, mode='rt') as fd:
            for line in fd.readlines():
                line = line.rstrip('\n')
                key, value = line.split('=')
                if key not in os.environ:
                    os.environ[key] = value
        logger.info('Successfully read %s environment file.', env_file)
    else:
        logger.warning('Environment file %s not found. Skipping populating os.environ')


def parse_dtm(x):
    return int(pytz.UTC.localize(datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ')).timestamp())
