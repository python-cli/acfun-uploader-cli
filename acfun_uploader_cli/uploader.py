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
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import InvalidSessionIdException

from selenium.webdriver.firefox.options import Options as FFOptions
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from pyvirtualdisplay import Display

from .config import *

logger = logging.getLogger(__name__)

# Suppress all the exceptions from this method.
original_send_keys = WebElement.send_keys

def safe_send_keys(self, *value):
    try:
        original_send_keys(self, *value)
    except:
        pass

WebElement.send_keys = safe_send_keys


class Acfun(object):

    def __init__(self, username, password, headless=True, use_cookie=False):
        super().__init__()

        if should_use_virtual_display():
            logger.info('Initialize a virtual display')
            self.display = Display(visible=0, size=(1024, 768))
            self.display.start()

        # Disable the chrome driver support because of this:
        # https://stackoverflow.com/q/67699765/1677041
        # executable = find_executable('chromedriver')
        executable = False

        if executable:
            logger.info('Initialize chrome driver')

            # https://stackoverflow.com/a/53970825/1677041
            chrome_options = Options()
            headless and chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')

            self.driver = webdriver.Chrome(executable, options=chrome_options)
        else:
            logger.info('Initialize firefox with geckodriver')

            ff_entry = find_executable('firefox-esr')
            executable = find_executable('geckodriver')

            if ff_entry is None:
                logger.error('firefox is not install!')

            if executable is None:
                logger.error('geckodriver is not installed!')

            firefox_options = FFOptions()
            firefox_options.add_argument('--headless')

            binary = FirefoxBinary(ff_entry)

            # https://stackoverflow.com/a/47785513/1677041
            cap = DesiredCapabilities().FIREFOX
            cap["marionette"] = False

            self.driver = webdriver.Firefox(executable_path=executable, firefox_options=firefox_options, firefox_binary=binary, capabilities=cap)

        if self.driver is None:
            logger.error('chromedriver or firefox/geckodriver is required!\n'
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

        logger.debug('waiting %ld second(s)' % seconds)
        sleep(seconds)
        logger.debug('waiting done')
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
        result = u'个人中心' in title
        logger.info('Login status: %s' % ('yes' if result else 'no'))
        return result

    def upload_video(self, title, cover, channel, sub_channel, tags, descriptions, video):
        result = False

        logger.info('Start to upload video')
        self.wait()

        self.driver.get('https://member.acfun.cn/upload-video')
        self.wait(5)

        logger.info('Fill video title: %s', title)
        title_element = self.waiter.until(EC.presence_of_element_located((By.XPATH, '//div[@class="video-select-container video-select-title fl"]/div/div/div/textarea')))
        title_element.clear()
        title_element.send_keys(title)

        logger.info('Select the video source type')
        self.driver.find_element(By.XPATH, '//div[@class="video-select-container fl"]/div/div/div/label/span/input').click()

        logger.info('Upload video cover: %s', cover)
        self.wait()
        logger.debug('Sending the cover file to input field')
        cover_element = self.driver.find_element(By.XPATH, '//div[@class="video-cover-tool fl"]/div/div/input')
        cover_element.send_keys(cover)
        self.wait(5)
        logger.debug('Confirm to finished the cover uploading')
        self.driver.find_element(By.XPATH, '//div[@class="ivu-modal-footer"]/div/button').click()
        self.wait(5)

        logger.info('Select the channel: [%s] - [%s]', channel, sub_channel)

        self.waiter.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="el-cascader video-channel-area"]'))).click()

        self.wait()
        # Wait for the dropdown menu list to show
        self.waiter.until(EC.visibility_of_element_located((By.XPATH, f'//div[@class="el-popper el-cascader__dropdown"]')))

        logger.debug('Locating the main channel')

        channel_element = self.waiter.until(EC.element_to_be_clickable((By.XPATH, f'//div[@class="el-cascader-panel"]//ul/li[./span/span[text()="{channel}"]]')))

        webdriver.ActionChains(self.driver).move_to_element(channel_element).click().perform()
        self.wait()

        logger.debug('Locating the sub channel')

        sub_channel_element = self.waiter.until(EC.presence_of_element_located((By.XPATH, f'//div[@class="el-cascader-panel"]/div[@class="el-scrollbar el-cascader-menu"]//li[./span/span[text()="{sub_channel}"]]')))
        sub_channel_element.click()

        logger.info('Input the tags')

        tagator = self.driver.find_element(By.XPATH, '//div[@class="video-select-container fl"]//input[@class="video-input-box-val"]')
        tagator.click()

        for i in range(min(4, len(tags))):
            tag = tags[i]
            logger.info('Tag: [%s]', tag)
            tagator.send_keys(tag)
            tagator.send_keys(Keys.ENTER)
            self.wait()

        tagator.send_keys(Keys.ESCAPE)

        logger.info('Input the video descriptions')
        self.driver.find_element(By.XPATH, '//div[@class="video-info-container clearfix" and ./div/h3[text()="简介"]]//textarea').send_keys(descriptions)

        logger.info('Input the fans descriptions')
        self.driver.find_element(By.XPATH, '//div[@class="video-info-container clearfix" and ./div/h3[text()="粉丝动态"]]//textarea').send_keys(descriptions)
        self.wait(2)

        logger.info('Uploading video file: %s', video)
        self.driver.find_element(By.XPATH, '//div[@class="upload-video-file fr"]//input[@type="file" and @name="file"]').send_keys(video)

        result = self._wait_video_upload_completed()
        self.wait(5)

        if result:
            self.wait()
            logger.debug('Filling the video file title')
            self.driver.find_element(By.XPATH, '//div[@class="video-upload-list"]//input').send_keys('p1')
            self.wait(2)
            logger.debug('Confirm to post the video')
            self.driver.find_element(By.XPATH, '//div[@class="video-submit-container fl"]/button').click()

        if result:
            logger.info('Upload video file [%s] successfully.', video)
        else:
            logger.error('Upload video file [%s] failed.', video)

        return result

    def _wait_video_upload_completed(self):
        logger.info('Waiting for the video upload progress completed')

        result = False
        last_info_text, last_progress = None, None
        start_time = datetime.now()

        while True:
            duration = (datetime.now() - start_time).total_seconds()

            if duration > 12 * 3600:
                logger.error('The upload operation time out!')
                break # timeout

            if not result:
                try:
                    result, progress = self._check_progress()

                    if progress and last_progress != progress:
                        last_progress = progress
                        logger.info('progress: %s' % progress)

                    if result:
                        logger.debug('The uploads should be completed since the progress bar finished.')
                        break
                except InvalidSessionIdException as e:
                    logger.exception(f'Found a webdriver exception when checking progress: {e}')
                    return False
                except (NoSuchElementException, StaleElementReferenceException) as e:
                    logger.exception(e)

        return result

    def _check_progress(self):
        result, progress = False, None

        progress_span = self.driver.find_element(By.XPATH, '//div[@class="video-upload-list"]//span[@class="video-upload-item-status"]')

        if progress_span:
            progress_text = progress_span.text
            result = progress_text == '上传完成'

            if progress_text and len(progress_text) > 0:
                progress = progress_text

        return result, progress

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
