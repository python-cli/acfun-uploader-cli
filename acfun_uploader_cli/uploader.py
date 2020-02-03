# -*- coding: UTF-8 -*-.

import logging
import os, pickle
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoAlertPresentException

logger = logging.getLogger(__name__)

class Acfun(object):

    def __init__(self, username, password, use_cookie=False):
        super().__init__()
        chrome_options = Options()
        __debug__ or chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.waiter = WebDriverWait(self.driver, 30)
        self.username = username
        self.password = password
        self.use_cookie = use_cookie

        self.driver.get("https://www.acfun.cn/")

        if use_cookie and os.path.exists(COOKIE_FILE):
            with open(COOKIE_FILE, 'rb') as f:
                for cookie in pickle.load(f):
                    # Remove the invalid `expiry` key.
                    # https://stackoverflow.com/a/57122470/1677041
                    if 'expiry' in cookie:
                        del cookie['expiry']

                    self.driver.add_cookie(cookie)

            self.driver.refresh()
            self.wait()

    def wait(self, multiplier=1):
        seconds = multiplier * (5 if __debug__ else 10)
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

        if self.use_cookie:
            with open(COOKIE_FILE, 'wb') as f:
                pickle.dump(self.driver.get_cookies(), f)
            logger.info('Saved the user cookies for reuse')

    def check_login(self):
        logger.info('Checking user login status')
        self.driver.get('https://www.acfun.cn/member/')
        self.wait(2)

        title = self.driver.title
        logger.debug('Title: %s', title)
        result = u'登录' not in self.driver.title
        logger.info('Login status: %s' % ('yes' if result else 'no'))
        return result

    def upload_video(self, title, cover, channel, sub_channel, tags, descriptions, video):
        result = False

        logger.info('Start to upload video')
        self.wait()

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
        self.wait(3)
        self.driver.find_element_by_name('channel').click()
        Select(self.driver.find_element_by_name('channel')).select_by_visible_text(channel)
        self.driver.find_element_by_name('subject').click()
        self.wait(3)
        Select(self.driver.find_element_by_name('subject')).select_by_visible_text(sub_channel)
        self.driver.find_element_by_id('tagator_inputTagator').click()

        logger.info('Input the tags')
        tagator = self.driver.find_element_by_xpath('//div[@id="tagator_inputTagator"]/input')
        tagator.click()

        for tag in tags:
            logger.debug('Input tag [%s]', tag)
            tagator.send_keys(tag)
            tagator.send_keys(Keys.ENTER)
            self.wait()

        logger.info('Input the descriptions')
        self.driver.find_element_by_xpath('//*[@id="up-descr"]').send_keys(descriptions)

        self.wait(2)
        logger.info('Uploading video files')
        self.driver.find_element_by_name('file').send_keys(video)

        # self.wait(2)
        # logger.info('Check the auto-publish switcher')
        # self.driver.find_element_by_css_selector('#uploadVideo > div.dividers.pos-rel > div > label').click()

        logger.info('Waiting for the upload progress completed')
        uploding_progress_done, submit_done = False, False
        last_info_text = None

        while True:
            if not submit_done:
                if uploding_progress_done:
                    self.wait()
                    self.driver.find_element_by_xpath('//input[@class="ptitles fl"]').send_keys('p1')
                    self.wait(2)
                    self.driver.find_element_by_id("up-submit").click()
                    submit_done = True
                else:
                    try:
                        progress_span = self.driver.find_element_by_xpath('//div[@class="pbox"]/div/span[@class="ptime"]')

                        if progress_span:
                            progress = progress_span.text
                            logger.debug('progress: %s' % progress)
                            uploding_progress_done = progress == '100%'
                    except NoSuchElementException as e:
                        pass
                    except StaleElementReferenceException as e:
                        pass

            # print and check the notification info.
            try:
                info_element = self.driver.find_element_by_xpath('//*[@id="area-info"]/div')

                if info_element:
                    text = info_element.text

                    if len(text) <= 0:
                        continue
                    elif text == last_info_text:
                        continue
                    else:
                        last_info_text = text

                    if 'error' in info_element.get_attribute("class"):
                        logger.error(text)

                        if u'投稿失败' in text:
                            result = False
                            break
                    else:
                        logger.info(text)
            except NoSuchElementException as e:
                pass
            except StaleElementReferenceException as e:
                pass

            try:
                success_div = self.driver.find_element_by_xpath('//*[@id="videoSuccess"]')
                if success_div.is_displayed():
                    logger.info('Uploaded the video successfully.')
                    result = True
                    break
            except NoSuchElementException as e:
                pass

            if '#area=upload-video' not in self.driver.current_url:
                logger.info('Page navigated!')
                # Undefined result!
                break

            # self.wait()

        logger.info('Finish the uploading')
        self.wait(5)

        return result

    def __del__(self):
        self.driver.quit()
        logger.info('Bye!')
