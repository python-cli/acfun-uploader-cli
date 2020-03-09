from os import makedirs
from os.path import join, exists, expanduser
import configparser
import json

_root = expanduser('~/.config/acfun-uploader-cli')
exists(_root) or makedirs(_root)

_config = None

CONFIG_FILE = join(_root, 'config')
COOKIE_FILE = join(_root, 'cookies')
CHANNEL_FILE = join(_root, 'channels')
DATABASE_FILE = join(_root, 'data.sqlite3')

_SECTION_GENERAL = 'GENERAL'
_SECTION_USER = 'USER'

def _load_config():
    global _config

    if _config is None:
        _config = configparser.ConfigParser()

        if exists(CONFIG_FILE):
            _config.read(CONFIG_FILE)
        else:
            _config.add_section(_SECTION_GENERAL)
            _config.set(_SECTION_GENERAL, 'virtual-display', '0')
            _config.set(_SECTION_GENERAL, 'wait-intervals', '5')
            _config.set(_SECTION_GENERAL, 'timeout', '60')

            _config.add_section(_SECTION_USER)
            _config.set(_SECTION_USER, 'username', '')
            _config.set(_SECTION_USER, 'password', '')

            with open(CONFIG_FILE, 'w') as f:
                _config.write(f)

    return _config

def pretty_json_string(dic):
    return json.dumps(dic, sort_keys=True, indent=4)

def get_raw_config():
    output = ''
    config = _load_config()

    for section in config.sections():
        output += '%s: \n' % section
        output += pretty_json_string(dict(config.items(section)))
        output += '\n\n'

    output += 'PATH: %s' % CONFIG_FILE

    return output

def should_use_virtual_display():
    return _load_config().get(_SECTION_GENERAL, 'virtual-display') != '0'

def get_wait_intervals():
    return int(_load_config().get(_SECTION_GENERAL, 'wait-intervals'))

def get_timeout_intervals():
    return int(_load_config().get(_SECTION_GENERAL, 'timeout'))

def get_userinfo():
    config = _load_config()
    return config.get(_SECTION_USER, 'username'), config.get(_SECTION_USER, 'password')
