import os

os.environ['SEARX_DEBUG'] = '1'
os.environ['SEARX_DISABLE_ETC_SETTINGS'] = '1'
os.environ.pop('SEARX_SETTINGS_PATH', None)
