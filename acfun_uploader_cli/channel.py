# -*- coding: UTF-8 -*-.

import logging
import requests
import json

from os.path import exists
from .config import CHANNEL_FILE

logger = logging.getLogger(__name__)

def fetch_channel_info(force_update=False):
    'Fetch the channel info from acfun site.'

    try:
        url = 'https://www.acfun.cn/rest/pc-direct/page/queryNavigators'

        if exists(CHANNEL_FILE) and not force_update:
            logger.info('Found existing channel file, reusing it...')
            return

        logger.info('Fetching channels')
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
        })

        if response.status_code != requests.codes.ok:
            logger.error('Failed to fetch channel with error: %s' % response.text)
            return

        res = response.json()
        channels = {}

        for entity in res.get('data'):
            items = [item.get('navName') for item in entity.get('children')]
            channels[entity.get('navName')] = items

        with open(CHANNEL_FILE, 'w') as f:
            json.dump(channels, f, indent=4)
            logger.info('Updated the channel info.')

    except requests.RequestException as e:
        logger.exception(e)

def load_channels():
    'Load and return the local channel info.'
    channels = None

    with open(CHANNEL_FILE, 'r') as f:
        channels = json.load(f)

    return channels

def choose_channel(printer=print):
    channels = load_channels()
    message = ''
    number = 0

    for channel, children in channels.items():
        message += '\n%s:' % channel

        for child in children:
            number += 1
            message += '\n%d\t%s' % (number, child)

        message += '\n'

    printer(message)
    printer('Please choose one channel: ', end='')

    while True:
        try:
            chosen_number = int(input())

            if chosen_number > 0 and chosen_number <= number:
                break
        except:
            pass

        printer('Invalid number, should be in range [1, %d]' % number)

    chosen_channel, chosen_subchannel = None, None

    for channel, children in channels.items():
        if chosen_number > len(children):
            chosen_number -= len(children)
        else:
            chosen_channel = channel
            chosen_subchannel = children[chosen_number - 1]
            break

    logger.debug('You chosen: %s - %s' % (chosen_channel, chosen_subchannel))
    return chosen_channel, chosen_subchannel
