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

#        items = getThemes()
#        items = [(i, i) for i in items]
        items = [('jqueryui', 'jqueryui'),
                 ('sunburst', 'sunburst')]
        return SimpleVocabulary.fromItems(items)

JQueryUIThemeVocabulary = JQueryUIThemeVocabularyFactory()

class ThemeManager(object):
    """Theme manager"""
    interface.implements(interfaces.IJQueryUIThemeManager)

    def __init__(self):
        self._site = None
        self._themeid = None
        self._settings = None
        self._csstool = None
        self._currentTheme = None
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


    def importTheme(self, themeArchive):
        """Import a zipfile as persistent resource"""
        pass

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
        items = []
        site = self.site()
        themeContainer = self.getThemeDirectory()
        themes = themeContainer['css'].listDirectory()
        #TODO: add sunburst
        return map(str, themes)
    
    def getThemeById(self, id):
        """Return IJQueryUITheme object"""
        if id == "sunburst":
            return SunburstTheme(id, self)

        return PersistentTheme(id, self, folder=self.getThemeDirectory())

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
        query+='&ui-version='+data['version']
        datac = data.copy()
        del datac['name']
        del datac['version']
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

    def getThemeFromZip(self, themeArchive):
        """Extract archive and store into container. set values of theme from it"""
        try:
            themeZip = zipfile.ZipFile(themeArchive)
        except (zipfile.BadZipfile, zipfile.LargeZipFile,):
            logger.exception("Could not read zip file")
            raise TypeError('error_invalid_zip')

        version = None
        folder = self.getThemeDirectory()
        themeid = None
        stylesheetid = None

        for name in themeZip.namelist():
            member = themeZip.getinfo(name)
            path = member.filename.lstrip('/')
            starter = path.split('/')[0]
            if starter =='css' and path.endswith('.custom.css') and themeid is None:
                themeid = path.split('/')[1]
                stylesheetid = 'portal_resources/jqueryuitheme/'+path
            if starter == 'js' and version is None:
                basename = os.path.basename(path)
                if basename.startswith('jquery-ui'):
                    version = basename[len('jquery-ui-'):-len('.custom.min.js')]

        if version is None:
            raise ValueError('Not a JQueryUI package')


        folder.importZip(themeZip)
        #register stylesheet and make it disabled
        csstool = self.csstool()
        stylesheet = csstool.getResourcesDict().get(stylesheetid, None)
        if stylesheet is None:
            csstool.registerStylesheet(stylesheetid)
        
        theme = self.getThemeById(themeid)

        for i in ('index.html', 'development-bundle', 'js'):
            try:
                del folder[i]
            except BadRequest, e:
                raise TypeError('Not a JQueryUI package')

        theme.unactivate()
        return theme

class SunburstTheme(object):
    """The theme provided by collective.js.jqueryui"""
    interface.implements(interfaces.IJQueryUITheme)

    START_CSS_ID = "++resource++jquery-ui-themes/sunburst/jquery-ui-"

    def __init__(self, id, manager):
        if id != "sunburst":raise ValueError("Not Sunburst theme")
        self.id = "sunburst"
        self.manager = manager
        self.stylesheetid = None
        self.version = None
        self.initialize()
    
    def initialize(self):
        csstool = self.manager.csstool()
        stylesheets = csstool.getResourcesDict()
        for sid in stylesheets:
            if sid.startswith(self.START_CSS_ID):
                self.stylesheetid = sid
                stylesheet = stylesheets[self.stylesheetid]
                self.version = sid[len(self.START_CSS_ID):-len(".custom.css")]
                break

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
    """A theme store in plone.Resource"""
    interface.implements(interfaces.IJQueryUITheme)
    def __init__(self, id, manager, folder=None):
        self.id = id
        self.version = None
        self.manager = manager
        self._site = None
        self._folder = folder
        self.stylesheetid = None
        self.initialize()

    def initialize(self):
        csstool = self.manager.csstool()
        stylesheets = csstool.getResourcesDict()
        startid = 'portal_resources/jqueryuitheme/css/%s'%self.id
        for sid in stylesheets:
            if not sid.startswith(startid):continue
            self.stylesheetid = sid
            break

        if self.stylesheetid is None:
            logger.info('theme not existing in portal_resource')
            return

        start_index = len('portal_resources/jqueryuitheme/css/%s/jquery-ui-'%self.id)
        end_index = len('.custom.css')
        self.version = self.stylesheetid[start_index:end_index]


    def activate(self):
        csstool = self.manager.csstool()
        try:
            stylesheet = csstool.getResourcesDict()[self.stylesheetid]
            stylesheet.setApplyPrefix(True)
            stylesheet.setEnabled(True)
            csstool.cookResources()
        except NotFound, e:
            logger.info('the new theme has not been found in resource directory')

    def unactivate(self):
        csstool = self.manager.csstool()
        try:
            stylesheet = csstool.getResourcesDict()[self.stylesheetid]
            stylesheet.setEnabled(False)
            csstool.cookResources()
        except KeyError, e:
            logger.info('the old theme has not been found in resource directory')
