# -*- coding: UTF-8 -*-.

import logging
import os, pickle
from distutils.spawn import find_executable
from time import sleep
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoAlertPresentException

from selenium.webdriver.firefox.options import Options as FFOptions
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from pyvirtualdisplay import Display

from .config import *

logger = logging.getLogger(__name__)

class Acfun(object):

    def __init__(self, username, password, headless=True, use_cookie=False):
        super().__init__()

        if should_use_virtual_display():
            self.display = Display(visible=0, size=(1024, 768))
            self.display.start()

        executable = find_executable('chromedriver')

        if executable:
            # https://stackoverflow.com/a/53970825/1677041
            chrome_options = Options()
            headless and chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')

            self.driver = webdriver.Chrome(executable, options=chrome_options)
        else:
            ff_entry = find_executable('firefox-esr')
            executable = find_executable('geckodriver')

            firefox_options = FFOptions()
            firefox_options.add_argument('--headless')

            binary = FirefoxBinary(ff_entry)

            # https://stackoverflow.com/a/47785513/1677041
            cap = DesiredCapabilities().FIREFOX
            cap["marionette"] = False

            self.driver = webdriver.Firefox(executable_path=executable, firefox_options=firefox_options, firefox_binary=binary, capabilities=cap)

        if self.driver is None:
            logger.error('chromedriver is required!\n'
            'Go to install it first and make sure it could be found in your $PATH.')
            return

        timeout = get_timeout_intervals()

        self.driver.set_page_load_timeout(timeout)
        self.waiter = WebDriverWait(self.driver, timeout)
        self.username = username
        self.password = password
        self.use_cookie = use_cookie

        self.driver.get("https://www.acfun.cn/")

        if use_cookie and os.path.exists(COOKIE_FILE):
            with open(COOKIE_FILE, 'rb') as f:
                for cookie in pickle.load(f):
                    if 'expiry' in cookie:
                        # https://stackoverflow.com/a/57122470/1677041
                        # del cookie['expiry']

                        # https://stackoverflow.com/a/60193504/1677041
                        cookie['expiry'] = int(cookie['expiry'])

                    self.driver.add_cookie(cookie)

            self.driver.refresh()
            self.wait()

    def wait(self, multiplier=1):
        seconds = multiplier * get_wait_intervals()
        sleep(seconds)
        # self.driver.implicitly_wait(seconds)

    def login(self):
        logger.info('Starting to login')
        self.driver.get('https://www.acfun.cn/login/')
        self.wait(5)
        self.driver.find_element(By.ID, 'login-account-switch').click()

        logger.info('Switching to the username/password mode')
        user_element = self.driver.find_element(By.ID, 'ipt-account-login')
        user_element.clear()
        user_element.send_keys(self.username)
        password_element = self.driver.find_element(By.ID, 'ipt-pwd-login')
        password_element.clear()
        password_element.send_keys(self.password)

        self.driver.find_element(By.CLASS_NAME, 'btn-login').click()
        self.waiter.until_not(EC.presence_of_element_located((By.ID, 'login')))

        self.check_login()

        if self.use_cookie:
            with open(COOKIE_FILE, 'wb') as f:
                pickle.dump(self.driver.get_cookies(), f)
            logger.info('Saved the user cookies for reuse')

    def check_login(self):
        logger.info('Checking user login status')
        self.driver.get('https://www.acfun.cn/member/')
        self.wait(5)

        title = self.driver.title
        logger.debug('Title: %s', title)
        result = u'欢迎' in title or u'用户中心' in title
        logger.info('Login status: %s' % ('yes' if result else 'no'))
        return result

    def upload_video(self, title, cover, channel, sub_channel, tags, descriptions, video):
        result = False

        logger.info('Start to upload video')
        self.wait()

        self.driver.get('https://www.acfun.cn/member/#area=upload-video')
        self.wait(5)

        logger.info('Fill video title: %s', title)
        title_element = self.waiter.until(EC.presence_of_element_located((By.ID, 'title')))
        title_element.clear()
        title_element.send_keys(title)

        logger.info('Select the video source type')
        self.driver.find_element(By.CSS_SELECTOR, '#uploadVideo > div.up-info.fl > div.up-detail > div.up-type.must > label:nth-child(6)').click()

        logger.info('Upload video cover: %s', cover)
        self.wait()
        self.driver.find_element(By.CSS_SELECTOR, '#up-pic > img').click()
        self.wait()
        cover_element = self.waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#filePicker > div:nth-child(2) > input')))
        cover_element.send_keys(cover)
        self.wait()
        self.driver.find_element(By.ID, 'uploadOk').click()

        logger.info('Select the channel: [%s] - [%s]', channel, sub_channel)
        channel_element = self.waiter.until(EC.visibility_of_element_located((By.NAME, 'channel')))
        self.wait()
        # channel_element = self.driver.find_element(By.NAME, 'channel').click()
        Select(channel_element).select_by_visible_text(channel)
        subject_element = self.driver.find_element(By.NAME, 'subject')
        self.wait()
        Select(subject_element).select_by_visible_text(sub_channel)

        logger.info('Input the tags')
        tagator = self.waiter.until(EC.presence_of_element_located((By.XPATH, '//div[@id="tagator_inputTagator"]/input')))
        # tagator.click()
        self.driver.execute_script("arguments[0].click();", tagator)

        for i in range(min(4, len(tags))):
            tag = tags[i]
            logger.info('Tag: [%s]', tag)
            tagator.send_keys(tag)
            tagator.send_keys(Keys.ENTER)
            self.wait()

        tagator.send_keys(Keys.ESCAPE)

        logger.info('Input the descriptions')
        self.driver.find_element(By.XPATH, '//*[@id="up-descr"]').send_keys(descriptions)

        self.wait(2)
        logger.info('Uploading video file: %s', video)
        self.driver.find_element(By.NAME, 'file').send_keys(video)

        # self.wait(2)
        # logger.info('Check the auto-publish switcher')
        # self.driver.find_element(By.CSS_SELECTOR, '#uploadVideo > div.dividers.pos-rel > div > label').click()

        result = self._wait_upload_completed()
        self.wait(5)

        if result:
            self.wait()
            self.driver.find_element(By.XPATH, '//input[@class="ptitles fl"]').send_keys('p1')
            self.wait(2)
            self.driver.find_element(By.ID, "up-submit").click()

        if result:
            logger.info('Upload video file [%s] successfully.', video)
        else:
            logger.error('Upload video file [%s] failed.', video)

        return result

    def _wait_upload_completed(self):
        logger.info('Waiting for the upload progress completed')

        result = False
        last_info_text, last_progress = None, None
        start_time = datetime.now()

        while True:
            duration = (datetime.now() - start_time).total_seconds()

            if duration > 12 * 3600:
                logger.error('The upload operation time out!')
                break # timeout

            if not result:
                res, progress = self._check_progress()

                if progress and last_progress != progress:
                    last_progress = progress
                    logger.info('progress: %s' % progress)

                if res:
                    result = True
                    logger.debug('The uploads should be completed since the progress bar finished.')
                    break

            res, text = self._check_notification()

            if text and last_info_text != text:
                last_info_text = text
                logger.info('Received notification: %s', text)

            if res:
                result = True
                logger.debug('The uploads should be completed since success notification was received.')
                break

            if self._check_upload_status():
                logger.debug('The uploads should be completed since it navigates to success page.')
                result = True
                break

        return result

    def _check_progress(self):
        result, progress = False, None

        try:
            progress_span = self.driver.find_element(By.XPATH, '//div[@class="pbox"]/div/span[@class="ptime"]')

            if progress_span:
                progress_text = progress_span.text
                result = progress_text == '100%'

                if len(progress_text) > 0:
                    progress = progress_text
        except NoSuchElementException as e:
            pass
        except StaleElementReferenceException as e:
            pass

        return result, progress

    def _check_notification(self):
        '''
        print and check the notification info.

        return True if received upload succeed notification, False if upload failed notification, None if none of signal be found.
        '''
        text = None

        try:
            info_element = self.driver.find_element(By.XPATH, '//*[@id="area-info"]/div')

            if info_element:
                text = info_element.text

                if len(text) > 0:
                    if u'投稿失败' in text:
                        return False
                    elif u'成功' in text:
                        return True
                else:
                    text = None
        except NoSuchElementException as e:
            pass
        except StaleElementReferenceException as e:
            pass

        return None, text

    def _check_upload_status(self):
        # Signal 1:
        try:
            success_div = self.driver.find_element(By.XPATH, '//*[@id="videoSuccess"]')
            if success_div.is_displayed():
                logger.info('Switch to the video success layer.')
                return True
        except NoSuchElementException as e:
            pass

        # Signal 2:
        current_url = self.driver.current_url

        if '#area=video-success' in current_url:
            logger.info('Page navigated to %s!', current_url)
            return True
        elif '#area=upload-video' not in current_url:
            logger.warning('Page navigated to %s!', current_url)
            # Undefined result!

        # self.wait()
        return False

    def __del__(self):
        try:
            if getattr(self, 'driver', None):
                self.driver.close()
                self.driver.quit()

            if getattr(self, 'display', None):
                self.display.stop()
        except:
            pass
        finally:
            logger.info('Bye!')
