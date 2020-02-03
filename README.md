## acfun-uploader-cli

> Upload video to [acfun](https://www.acfun.cn) site.



#### Environment

* Python 3
* Chrome and [chromedriver](https://chromedriver.chromium.org/) 79+



#### Deployment

* Chrome/Chromium

  * macOS

  * Linux/Debian

    * ```
      apt-get install chromium
      # Refer to https://github.com/timgrossmann/InstaPy/issues/1245#issuecomment-358872721
      ```

    * ```
      wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
      dpkg -i google-chrome-stable_current_amd64.deb
      apt-get -fy install
      
      # Refer to https://github.com/timgrossmann/InstaPy/issues/1245#issuecomment-396515785
      ```

    * More references: [1](https://github.com/heroku/heroku-buildpack-google-chrome/issues/46) and [2](https://github.com/heroku/heroku-buildpack-google-chrome/issues/46)
  
* chromedriver

  1. Download the executable file from [here](https://chromedriver.chromium.org/downloads) and extract it.
  2. Move the executable file to `/usr/local/bin` to other environment paths (`$PATH`).



#### Usage

Run `python main.py` under the root directory to check the example usage.



#### Author

[Will Han](mailto:xingheng.hax@qq.com)

