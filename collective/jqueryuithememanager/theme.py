from urlparse import urlparse, parse_qs

from zope import component
from zope import interface

from collective.jqueryuithememanager import config
from collective.jqueryuithememanager import interfaces
from collective.jqueryuithememanager import logger
from zExceptions import NotFound
from zExceptions import BadRequest


class Theme(object):
    """A theme that works with browser:resourceDirectory"""
    interface.implements(interfaces.IJQueryUITheme)
    BASE_PATH = ''
    VERSION = ''

    def __init__(self, id, provider):
        self.id = id
        self.provider = provider
        self._manager = None
        self.stylesheetid = provider.BASE_PATH+id+'/jqueryui.css'
        self.version = provider.VERSION

    def activate(self):
        manager = self.getThemeManager()
        csstool = manager.getCSSRegistry()
        stylesheet = csstool.getResourcesDict().get(self.stylesheetid, None)
        if not stylesheet:
            csstool.registerStylesheet(self.stylesheetid)
            stylesheet = csstool.getResourcesDict()[self.stylesheetid]
        stylesheet.setApplyPrefix(True)
        stylesheet.setEnabled(True)
        csstool.cookResources()

    def unactivate(self):
        manager = self.getThemeManager()
        csstool = manager.getCSSRegistry()
        stylesheet = csstool.getResourcesDict().get(self.stylesheetid, None)
        if stylesheet:
            csstool.unregisterResource(self.stylesheetid)
            csstool.cookResources()
        else:
            logger.info('can t unactivate %s'%self.stylesheetid)

    def getParams(self):
        link = self.getThemeRollerLink()
        query_string = urlparse(link).query
        query = parse_qs(query_string)
        return query

    def getThemeRollerLink(self):
        link = None
        if self.provider is not None:
            if hasattr(self.provider, 'THEME_ROLLER'):
                link = self.provider.THEME_ROLLER.get(self.id,None)
                if link is not None: return link
        #don t find in metadata, lets extract from the css
        manager = self.getThemeManager()
        csstool = manager.getCSSRegistry()
        site = component.getSiteManager()
        path = site.restrictedTraverse(self.stylesheetid).context.path
        f = open(path,'rb')
        data = f.read()
        f.close()
        data_splited = data.split('\n')
        for line in data_splited:
            if "http://jqueryui.com/themeroller/" in line:
                link = line[line.index('http'):]
                break
        return link

    def getThemeManager(self):
        if self._manager is None:
            self._manager = component.getUtility(interfaces.IJQueryUIThemeManager)
        return self._manager



class PersistentTheme(Theme):
    """A theme store in plone.Resource
    
    The css must in portal_resources/jqueryuithemes/themeid/jqueryui.css
    """
    interface.implements(interfaces.IJQueryUITheme)

    def __init__(self, id, provider):
        super(PersistentTheme, self).__init__(id, provider)
        self.version = ''
        self.initialize()
    
    def initialize(self):
        themeDirectory = self.provider.getThemeDirectory()
        if self.id in themeDirectory.listDirectory():
            folder = themeDirectory[self.id]
            if 'version.txt' in folder.listDirectory():
                self.version = folder.readFile('version.txt')

    def getThemeRollerLink(self):
        themeDirectory = self.provider.getThemeDirectory()
        if self.id in themeDirectory.listDirectory():
            folder = themeDirectory[self.id]
            if 'link.txt' in folder.listDirectory():
                link = folder.readFile('link.txt')
        return link

