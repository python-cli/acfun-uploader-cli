#!/usr/bin/env python
# -*- coding: UTF-8 -*-.

import os
from acfun_uploader_cli.config import get_userinfo
from acfun_uploader_cli.channel import *
from acfun_uploader_cli.uploader import Acfun

def main():
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
        video=os.path.expanduser('~/Desktop/test/demo-videos/a.mp4')
    )

if __name__ == '__main__':
    main()
    # fetch_channel_info(True)
    # choose_channel()
