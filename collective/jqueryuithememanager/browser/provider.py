from zope import component
from zope import interface

from collective.jqueryuithememanager import config
from collective.jqueryuithememanager import interfaces
from collective.jqueryuithememanager import logger
from collective.jqueryuithememanager import theme

class BrowserResourceThemeProvider(object):
    """Browser resource directory base theme provider"""
    interface.implements(interfaces.IThemesProvider)
    RESOURCE_NAME = 'jqueryuithememanager'
    BASE_PATH = '++resource++'+RESOURCE_NAME+'/'
    THEME_IDS = ['base']
    THEME_ROLLER = {'base':'http://jqueryui.com/themeroller'}
    THEME_CLASS = theme.BaseTheme
    VERSION='1.8.12'

    def __init__(self):
        self.manager = self._getThemeManager()

    def getThemeIds(self):
        return self.THEME_IDS

    def getThemeById(self, id):
        return self.THEME_CLASS(id, self)

    def getThemes(self):
        return map(self.getThemeById, self.getThemeIds())

    def _getThemeManager(self):
        return component.getUtility(interfaces.IJQueryUIThemeManager)
