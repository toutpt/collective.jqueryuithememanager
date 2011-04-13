import urllib2
import os
from collective.jqueryuithememanager import config

for preloaded in config.PRELOADEDS:
    folder = 'static/css/%s/'%preloaded
    try:
        os.mkdir(folder)
    except OSError:
        pass
    url = config.URL%preloaded
    css = urllib2.urlopen(url)
    css_str = css.read()
    target = open(folder+'jquery-ui.css','w')
    target.write(css_str)
    target.close()
