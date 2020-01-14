# -*- coding: UTF-8 -*-.

import os, pickle
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from .logger import *
from .config import *

logger = getLogger(__name__)

class Acfun(object):

    def __init__(self, username, password):
        super().__init__()
        self.driver = webdriver.Chrome()
        self.waiter = WebDriverWait(self.driver, 10)
        self.username = username
        self.password = password

        self.driver.get("https://www.acfun.cn/")

        if os.path.exists(COOKIE_FILE):
            with open(COOKIE_FILE, 'rb') as f:
                for cookie in pickle.load(f):
                    # Remove the invalid `expiry` key.
                    # https://stackoverflow.com/a/57122470/1677041
                    if 'expiry' in cookie:
                        del cookie['expiry']

                    self.driver.add_cookie(cookie)

            self.driver.refresh()
            self.wait()

    def wait(self, seconds=1):
        # self.driver.implicitly_wait(seconds)
        sleep(seconds)

    def login(self):
        logger.info('Start to login')
        self.driver.get('https://www.acfun.cn/login/')
        self.driver.find_element_by_id('login-switch').click()

        logger.info('Switching to the username/password mode')
        user_element = self.driver.find_element_by_id('ipt-account-login')
        user_element.clear()
        user_element.send_keys(self.username)
        password_element = self.driver.find_element_by_id('ipt-pwd-login')
        password_element.clear()
        password_element.send_keys(self.password)

        self.driver.find_element_by_class_name('btn-login').click()
        self.check_login()

        with open(COOKIE_FILE, 'wb') as f:
            pickle.dump(self.driver.get_cookies(), f)
        logger.info('Saved the user cookies for reuse')

    def check_login(self):
        logger.info('Checking user login status')
        self.driver.get('https://www.acfun.cn/member/')
        self.wait()

        result = u'登录' not in self.driver.title
        logger.info('Login status: %s' % ('yes' if result else 'no'))
        return result

    def upload_video(self, title, cover, channel, sub_channel, video):
        logger.info('Start to upload video')
        self.driver.get('https://www.acfun.cn/member/#area=upload-video')
        self.driver.implicitly_wait(5)

        logger.info('Fill video title')
        title_element = self.driver.find_element_by_id('title')
        title_element.clear()
        title_element.send_keys(title)

        logger.info('Select the video source type')
        self.driver.find_element_by_css_selector('#uploadVideo > div.up-info.fl > div.up-detail > div.up-type.must > label:nth-child(6)').click()

        logger.info('Upload video cover')
        self.wait()
        self.driver.find_element_by_css_selector('#up-pic > img').click()
        self.wait()
        self.driver.find_element_by_css_selector('#filePicker > div:nth-child(2) > input').send_keys(cover)
        self.wait()
        self.driver.find_element_by_id('uploadOk').click()

        logger.info('Select the channel')
        # self.waiter.until(EC.presence_of_element_located((By.NAME, 'channel'))).click()
        self.wait(5)
        self.driver.find_element_by_name('channel').click()
        Select(self.driver.find_element_by_name('channel')).select_by_visible_text(channel)
        self.driver.find_element_by_name('subject').click()
        self.wait()
        Select(self.driver.find_element_by_name('subject')).select_by_visible_text(sub_channel)
        self.driver.find_element_by_id('tagator_inputTagator').click()

        logger.info('Uploading video files')
        self.driver.find_element_by_name('file').send_keys(video)

        self.driver.find_element_by_css_selector('#uploadVideo > div.dividers.pos-rel > div > label').click()
        # self.driver.find_element_by_id("up-submit").click()

    def __del__(self):
        self.driver.close()
        logger.info('Bye!')
