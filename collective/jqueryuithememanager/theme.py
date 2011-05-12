import os
import zipfile
import StringIO

from urlparse import urlparse, parse_qs
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

class PersistentThemeVocabularyFactory(object):
    """Vocabulary for jqueryui themes.
    """
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        """Retrieve available themes inside persistent resource and add
        sunburst and collective.js.jqueryui themes"""
        tm = ThemeManager()
        try:
            items = [(id, id) for id in tm.getThemeIds()\
                     if id not in ('sunburst','', None)]
            return SimpleVocabulary.fromItems(items)
        except TypeError:
            logger.info('kss inline validation ... getSite doesn t return Plone site')
            return SimpleVocabulary.fromItems([])

PersistentThemeVocabulary = PersistentThemeVocabularyFactory()


class JQueryUIThemeVocabularyFactory(object):
    """Add sunburst theme to persistent"""
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        """Retrieve available themes inside persistent resource and add
        sunburst and collective.js.jqueryui themes"""
        tm = ThemeManager()
        try:
            items = [(id, id) for id in tm.getThemeIds() if id]
            return SimpleVocabulary.fromItems(items)
        except TypeError:
            logger.info('kss inline validation ... getSite doesn t return Plone site')
            return SimpleVocabulary.fromItems([('sunburst','sunburst')])

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
            self._settings = component.getUtility(IRegistry).forInterface(interfaces.IDefaultThemeFormSchema)
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
        themes = themeContainer.listDirectory()
        themes = map(str, themes)
        if 'sunburst' not in themes:
            themes.insert(0,'sunburst')
        providers = self.getThemesProviders()
        for provider in providers:
            ids = provider.getThemeIds()
            for id in ids:
                if id not in themes:
                    themes.append(id)
        return themes

    def getThemes(self):
        """Return the list of themes"""
        themeids = self.getThemeIds()
        return map(self.getThemeById, themeids)
    
    def getThemeById(self, id):
        """Return IJQueryUITheme object"""

        if id == "sunburst":
            return SunburstTheme(id, self)

        #Check if it is in peristent folder
        themeContainer = self.getThemeDirectory()
        if id in themeContainer.listDirectory():
            return PersistentTheme(id, self)

        #Return from provider
        providers = self.getThemesProviders()
        for provider in providers:
            if id in provider.getThemeIds():
                return provider.getThemeById(id)


    def getThemesProviders(self):
        providers = []
        utilities = sorted(component.getUtilitiesFor(interfaces.IThemesProvider))
        for utility in utilities:
            pid, provider = utility
            providers.append(provider)
        return providers

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
#        logger.info('download : %s/?%s'%(BASE, query))
        download = urlopen(BASE+'?'+query)
        code = download.getcode()
    
        if code != 200:
            raise Exception, 'Cant download the theme got %s code'%code
        if download.info().type != 'application/zip':
            raise Exception, 'Is not a zip file'
        content = download.read()
        sio = StringIO.StringIO(content)
        theme = self.getThemesFromZip(sio)
        return theme

    def getThemesFromZip(self, themeArchive):
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
            version = ''
            link = '' #get the link to rebuild this theme
            if path_splited[0] != 'development-bundle' and \
               not path_splited[0].startswith('jquery-ui-themes-'):
                continue
            if path.endswith('version.txt'):
                version = themeZip.open(member).read()
                continue
            if len(path_splited)<2:
                continue
            if path_splited[1] != 'themes':
                continue
            themeid = path_splited[2]
            if not themeid:
                continue
            if themeid not in themeids:
                themeids.append(themeid)
            newpath = themeid + '/'
            folder.makeDirectory(newpath)
            folder.makeDirectory(newpath+'images/')
            if path.endswith('.png'):
                data = themeZip.open(member).read()
                folder.writeFile(newpath+'images/'+path_splited[-1], data)
            elif path.endswith('.custom.css') or path.endswith('jquery-ui.css'):
                data = themeZip.open(member).read()
                folder.writeFile(newpath+'jqueryui.css', data)
                if not version:
                    #TODO: find version in the css itself
                    data_splited = data.split('\n')
                    version = ''.join(data_splited[1][len(" * jQuery UI CSS Framework "):])
                    for line in data_splited:
                        if "http://jqueryui.com/themeroller/" in line:
                            link = line[line.index('http'):]
            if version:
                folder.writeFile(newpath+'version.txt',version)
            elif version:
                logger.error('no version.txt found')
            if link:
                folder.writeFile(newpath+'link.txt', link)
            elif version:
                logger.error('no link found')

        return map(self.getThemeById, themeids)

    def deleteTheme(self, themeid):
        """Delete and unregister the theme"""
        #First we check if the delete theme is called on current used theme
        currentTheme = self.getDefaultThemeId()
        if currentTheme == themeid:
            self.setDefaultThemeId('sunburst')

        theme = self.getThemeById(themeid)
        folder = self.getThemeDirectory()
        del folder[themeid]


    def updateTheme(self, id):
        theme = self.getThemeById(id)
        params = theme.getParams()
        params['name']=id
        self.downloadTheme(params)

def checkZipFile(archive):
    """Raise exception if not a zip"""
    try:
        themeZip = zipfile.ZipFile(archive)
    except (zipfile.BadZipfile, zipfile.LargeZipFile,):
        logger.exception("Could not read zip file")
        raise TypeError('error_invalid_zip')
    return themeZip



class BaseTheme(object):
    """A theme that works with browser:resourceDirectory"""
    interface.implements(interfaces.IJQueryUITheme)
    BASE_PATH = ''
    VERSION = ''

    def __init__(self, id, manager, provider=None):
        self.id = id
        self.manager = manager
        self.provider = provider
        if provider:
            self.stylesheetid = provider.BASE_PATH+id+'/jqueryui.css'
            self.version = provider.VERSION
        else:
            self.stylesheetid = self.BASE_PATH+id+'/jqueryui.css'
            self.version = self.VERSION

    def activate(self):
        csstool = self.manager.csstool()
        stylesheet = csstool.getResourcesDict().get(self.stylesheetid, None)
        if not stylesheet:
            csstool.registerStylesheet(self.stylesheetid)
            stylesheet = csstool.getResourcesDict()[self.stylesheetid]
        stylesheet.setApplyPrefix(True)
        stylesheet.setEnabled(True)
        csstool.cookResources()

    def unactivate(self):
        csstool = self.manager.csstool()
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
            link = self.provider.THEME_ROLLER.get(self.id,None)
            if link is not None: return link
        #don t find in metadata, lets extract from the css
        csstool = self.manager.csstool()
        site = component.getSiteManager()
        #Weird code, .GET broke the page, I don't find an other way to get the content of the CSS
        path = site.restrictedTraverse(self.stylesheetid).context.path
        f = open(path,'rb')
        data = f.read()
        f.close()
        data_splited = data.split('\n')
        for line in data_splited:
            if "http://jqueryui.com/themeroller/" in line:
                link = line[line.index('http'):]
        return link


class BaseThemeProvider(object):
    """Browser resource directory base theme provider"""
    interface.implements(interfaces.IThemesProvider)
    RESOURCE_NAME = 'jqueryuithememanager'
    BASE_PATH = '++resource++'+RESOURCE_NAME+'/'
    THEME_IDS = ['base']
    THEME_ROLLER = {'base':'http://jqueryui.com/themeroller'}
    THEME_CLASS = BaseTheme
    VERSION='1.8.12'

    def __init__(self):
        self.manager = ThemeManager()

    def getThemeIds(self):
        return self.THEME_IDS

    def getThemeById(self, id):
        return self.THEME_CLASS(id, self.manager, self)

    def getThemes(self):
        return map(self.getThemeById, self.getThemeIds())


class SunburstTheme(BaseTheme):
    """The theme provided by collective.js.jqueryui"""
    interface.implements(interfaces.IJQueryUITheme)

    def __init__(self, id, manager):
        if id != "sunburst":raise ValueError("Not Sunburst theme")
        self.id = id
        self.manager = manager
        self.stylesheetid = config.SUNBURST_CSS_ID
        self.version = config.VERSION
        self.provider = None

    def activate(self):
        csstool = self.manager.csstool()
        try:
            stylesheets = csstool.getResourcesDict()
            stylesheet = csstool.getResourcesDict()[self.stylesheetid]
            stylesheet.setEnabled(True)
            patch = stylesheets.get('++resource++jquery-ui-themes/sunburst-patch.css', None)
            if patch is not None:
                patch.setEnabled(True)
            csstool.cookResources()
        except NotFound, e:
            logger.info('the new theme has not been found in resource directory')

    def unactivate(self):
        csstool = self.manager.csstool()
        try:
            stylesheets = csstool.getResourcesDict()
            stylesheet = csstool.getResourcesDict()[self.stylesheetid]
            stylesheet.setEnabled(False)
            patch = stylesheets.get('++resource++jquery-ui-themes/sunburst-patch.css', None)
            if patch is not None:
                patch.setEnabled(False)
            csstool.cookResources()

        except KeyError, e:
            logger.info('the old theme has not been found in resource directory')



class PersistentTheme(BaseTheme):
    """A theme store in plone.Resource
    
    The css must in portal_resources/jqueryuithemes/themeid/jqueryui.css
    """
    interface.implements(interfaces.IJQueryUITheme)

    BASE_PATH = "portal_resources/jqueryuitheme/"

    def __init__(self, id, manager):
        super(PersistentTheme, self).__init__(id, manager)
        self.version = ''
        self.initialize()
    
    def initialize(self):
        themeDirectory = self.manager.getThemeDirectory()
        if self.id in themeDirectory.listDirectory():
            folder = themeDirectory[self.id]
            if 'version.txt' in folder.listDirectory():
                self.version = folder.readFile('version.txt')

    def getThemeRollerLink(self):
        themeDirectory = self.manager.getThemeDirectory()
        if self.id in themeDirectory.listDirectory():
            folder = themeDirectory[self.id]
            if 'link.txt' in folder.listDirectory():
                link = folder.readFile('link.txt')
        return link

