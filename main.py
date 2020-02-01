#!/usr/bin/env python
# -*- coding: UTF-8 -*-.

import os
import coloredlogs, logging, logging.config
from acfun_uploader_cli.config import get_userinfo
from acfun_uploader_cli.channel import *
from acfun_uploader_cli.uploader import Acfun

# Refer to
#   1. https://stackoverflow.com/a/7507842/1677041
#   2. https://stackoverflow.com/a/49400680/1677041
#   3. https://docs.python.org/2/library/logging.config.html
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'colored': {
            '()': 'coloredlogs.ColoredFormatter',
            'format': "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            'datefmt': '%H:%M:%S',
        }
    },
    'handlers': {
        'default': {
            'level': 'DEBUG' if __debug__ else 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'console': {
            'level': 'DEBUG' if __debug__ else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': 'main.log',
            'maxBytes': 1024 * 1024,
            'backupCount': 10
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        },
        '__main__': {  # if __name__ == '__main__'
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'acfun_uploader_cli': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def main():
    logger.info('Debug is %s', 'on' if __debug__ else 'off')

    username, password = get_userinfo()

    if len(username) <= 0 or len(password) <= 0:
        logger.warning('Invalid user info for login.')
        return

    acer = Acfun(username, password)

    acer.check_login() or acer.login()
    acer.upload_video(
        title='acfun video poster',
        cover=os.path.expanduser('~/Desktop/test/demo-videos/demo-0001.png'),
        channel=u'生活',
        sub_channel=u'生活日常',
        tags=['a', 'b'],
        descriptions='balabala...',
        video=os.path.expanduser('~/Desktop/test/demo-videos/a.mp4')
    )

if __name__ == '__main__':
    main()
    # fetch_channel_info(True)
    # choose_channel()
