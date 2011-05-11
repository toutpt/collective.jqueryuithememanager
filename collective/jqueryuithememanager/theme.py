import os
import zipfile
import StringIO

from urlparse import urlparse
from urllib import urlencode, quote, quote_plus, unquote, unquote_plus
from urllib2 import urlopen

from zope import component
from zope import interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.site.hooks import getSite

from plone.registry.interfaces import IRegistry
from plone.resource.interfaces import IResourceDirectory

from collective.jqueryuithememanager import config
from collective.jqueryuithememanager import interfaces
from collective.jqueryuithememanager import logger
from zExceptions import NotFound
from zExceptions import BadRequest

class JQueryUIThemeVocabularyFactory(object):
    """Vocabulary for jqueryui themes.
    """
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        """Retrieve available themes inside persistent resource and add
        sunburst and collective.js.jqueryui themes"""
        tm = ThemeManager()
        try:
            items = [(id, id) for id in tm.getThemeIds()]
            return SimpleVocabulary.fromItems(items)
        except TypeError:
            logger.info('kss inline validation ... getSite doesn t return Plone site')
            return SimpleVocabulary.fromItems(('sunburst','sunburst'))

JQueryUIThemeVocabulary = JQueryUIThemeVocabularyFactory()

class ThemeManager(object):
    """Theme manager"""
    interface.implements(interfaces.IJQueryUIThemeManager)

    def __init__(self):
        self._site = None
        self._themeid = None
        self._settings = None
        self._csstool = None
        self._themedirectory = None
    
    def site(self):
        if self._site is None:
            self._site = component.getSiteManager()
        return self._site

    def csstool(self):
        if self._csstool is None:
            site = self.site()
            self._csstool = site.portal_css
        return self._csstool

    def settings(self):
        if self._settings is None:
            self._settings = component.getUtility(IRegistry).forInterface(interfaces.IJQueryUIThemeSettings)
        return self._settings


    def getThemeDirectory(self):
        """Obtain the 'jqueryuitheme' persistent resource directory,
        creating it if necessary.
        """

        if self._themedirectory is None:
            persistentDirectory = component.getUtility(IResourceDirectory,
                                                       name="persistent")
            if config.THEME_RESOURCE_NAME not in persistentDirectory:
                persistentDirectory.makeDirectory(config.THEME_RESOURCE_NAME)
        
            self._themedirectory = persistentDirectory[config.THEME_RESOURCE_NAME]

        return self._themedirectory

    def getThemeIds(self):
        """Return the list of available themes"""
        themeContainer = self.getThemeDirectory()
        themes = themeContainer['css'].listDirectory()
        #TODO: add sunburst
        themes = map(str, themes)
        themes.insert(0,'sunburst')
        return themes
    
    def getThemeById(self, id):
        """Return IJQueryUITheme object"""
        if id == "sunburst":
            return SunburstTheme(id, self)

        return PersistentTheme(id, self)

    def getDefaultThemeId(self):
        """Return the configuration themeid currently used"""
        settings = self.settings()
        return settings.theme

    def setDefaultThemeId(self, themeid):
        """Set the current theme configuration to themeid"""
        settings = self.settings()
        settings.theme = themeid

    def downloadTheme(self, data):
        """Download the themezip directly from jqueryui.com
        """

        BASE = "http://jqueryui.com/download/"
        query = 'download=true'
    
        for file in config.FILES:
            query += '&files[]='+file
    
        query+= '&t-name='+data['name']
        query+= '&scope='
        query+='&ui-version='+config.VERSION
        datac = data.copy()
        del datac['name']
        for key in datac:
            if 'Texture' in key: datac[key] = '01_flat.png' #force to use flat
        theme = urlencode(datac).replace('%23','') # %23 is # and we don't want this in color code
        query+='&theme=%3F'+quote(theme)
        logger.info('download : %s/?%s'%(BASE, query))
        download = urlopen(BASE+'?'+query)
        code = download.getcode()
    
        if code != 200:
            raise Exception, 'Cant download the theme got %s code'%code
        if download.info().type != 'application/zip':
            raise Exception, 'Is not a zip file'
        content = download.read()
        sio = StringIO.StringIO(content)
        f = open('test.zip', 'wb')
        f.write(content)
        f.close()
        theme = self.getThemeFromZip(sio)
        return theme


#
#    def getThemesFromZip(self, themeArchive):
#        themes = []
#        themeZip = checkZipFile(themeArchive)
#        folder = self.getThemeDirectory()
#        cssids = []
#        isThemesFolder = False
#        for name in themeZip.namelist():
#            member = themeZip.getinfo(name)
#            path = member.filename.lstrip('/')
#            try:
#                isThemesFolder = path.split('/')[1] == "themes"
#            except IndexError:
#                pass
#
#
#            #check if it is a simple theme
#            starter = path.split('/')[0]
#            if starter =='css' and path.endswith('.custom.css'):
#                return [self.getThemeFromZip(themeArchive)]
#
#            if not isThemesFolder: continue
#            newpath = 'css/'+'/'.join(path.split('/')[2:])
#            if newpath.endswith('/'):
#                folder.makeDirectory(newpath)
#            else:
#                data = themeZip.open(member).read()
#                folder.writeFile(newpath, data)
#            if newpath.endswith('/jquery-ui.css'):
#                cssids.append('portal_resources/jqueryuitheme/'+newpath)
#        
#        csstool = self.csstool()
#        resources = csstool.getResourcesDict()
#        for stylesheetid in cssids:
#            stylesheet = resources.get(stylesheetid, None)
#            if stylesheet is None:
#                csstool.registerStylesheet(stylesheetid)
#            themeid = stylesheetid.split('/')[3]
#            theme = self.getThemeById(themeid)
#            theme.unactivate()
#            themes.append(theme)
#
#        return themes
    
    def getThemeFromZip(self, themeArchive):
        """Extract archive and store into container. set values of theme from it
        
        """
        themeZip = checkZipFile(themeArchive)
        themes = []
        themeids = []
        folder = self.getThemeDirectory()

        for name in themeZip.namelist():
            member = themeZip.getinfo(name)
            path = member.filename.lstrip('/')
            path_splited = path.split('/')
            if path_splited[0] != 'developpement-bundle':continue
            if len(path_splited)<2:continue
            if path_splited[1] != 'themes':continue
            themeid = path_splited[2]
            if themeid not in themeids:
                themeids.append(themeid)
            newpath = 'portal_resources/jqueryuitheme/' + themeid + '/'
            folder.makeDirectory(newpath)
            folder.makeDirectory(newpath+'images')
            if path.endswith('.png'):
                data = themeZip.open(member).read()
                folder.writeFile(newpath+'images/'+path_splited[-1], data)
            elif path.endswith('.custom.css') or path.endswith('jquery-ui.css'):
                data = themeZip.open(member).read()
                folder.writeFile(newpath+'jquery-ui.css', data)

        return map(self.getThemeById, themeids)

    def deleteTheme(self, themeid):
        """Delete and unregister the theme"""
        theme = self.getThemeById(themeid)
        folder = self.getThemeDirectory()
        css = folder['css']
        del css[themeid]

        csstool = self.csstool()
        csstool.unregisterResource(theme.stylesheetid) #resource already re cooked



class SunburstTheme(object):
    """The theme provided by collective.js.jqueryui"""
    interface.implements(interfaces.IJQueryUITheme)

    def __init__(self, id, manager):
        if id != "sunburst":raise ValueError("Not Sunburst theme")
        self.id = "sunburst"
        self.manager = manager
        self.stylesheetid = self.START_CSS_ID%config.VERSION

    def activate(self):
        csstool = self.manager.csstool()
        stylesheets = csstool.getResourcesDict()
        for stylesheetid in stylesheets:
            if stylesheetid.startswith('++resource++jquery-ui-themes/sunburst'):
                stylesheet = stylesheets[self.stylesheetid]
                stylesheet.setEnabled(True)
        csstool.cookResources()
        return

    def unactivate(self):
        csstool = self.manager.csstool()
        stylesheets = csstool.getResourcesDict()
        try:
            stylesheet = stylesheets[self.stylesheetid]
            stylesheet.setEnabled(False)
            csstool.cookResources()
        except NotFound:
            logger.error("Sunburst resource not found: %s"%self.stylesheetid)


class PersistentTheme(object):
    """A theme store in plone.Resource
    
    The css must in portal_resources/jqueryuithemes/themeid/jqueryui.css
    """
    interface.implements(interfaces.IJQueryUITheme)

    CSS_ID = "portal_resources/jqueryuitheme/%s/jqueryui.css"

    def __init__(self, id, manager):
        self.id = id
        self.manager = manager
        self._site = None
        self.stylesheetid = self.CSS_ID%id

    def activate(self):
        csstool = self.manager.csstool()
        try:
            stylesheet = csstool.getResourcesDict().get(self.stylesheetid, None)
            if not stylesheet:
                csstool.registerStylesheet(self.stylesheetid)
                stylesheet = csstool.getResourcesDict()[self.stylesheetid]
            stylesheet.setApplyPrefix(True)
            stylesheet.setEnabled(True)
            csstool.cookResources()
        except NotFound, e:
            logger.info('the new theme has not been found in resource directory')

    def unactivate(self):
        csstool = self.manager.csstool()
        try:
            stylesheet = csstool.getResourcesDict().get(self.stylesheetid, None)
            if stylesheet:
                csstool.unregisterStylesheet(self.stylesheetid)
                csstool.cookResources()
        except KeyError, e:
            logger.info('the old theme has not been found in resource directory')

def checkZipFile(archive):
    """Raise exception if not a zip"""
    try:
        themeZip = zipfile.ZipFile(archive)
    except (zipfile.BadZipfile, zipfile.LargeZipFile,):
        logger.exception("Could not read zip file")
        raise TypeError('error_invalid_zip')
    return themeZip
