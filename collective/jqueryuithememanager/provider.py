import zipfile

from StringIO import StringIO

from urlparse import urlparse
from urllib import urlencode, quote, quote_plus, unquote, unquote_plus
from urllib2 import urlopen

from zope import component
from zope import interface

from plone.resource.interfaces import IResourceDirectory

from collective.jqueryuithememanager import config
from collective.jqueryuithememanager import interfaces
from collective.jqueryuithememanager import logger
from collective.jqueryuithememanager import theme


class PersistentThemeProvider(object):
    """The persistent theme provider"""
    interface.implements(interfaces.IPersistentThemesProvider)
    BASE_PATH = 'portal_resources/jqueryuitheme/'
    VERSION = ''
    THEME_CLASS = theme.PersistentTheme

    def __init__(self):
        self._site = None
        self._themeid = None
        self._settings = None
        self._csstool = None
        self._themedirectory = None


    def getThemeIds(self):

        themeContainer = self.getThemeDirectory()
        themes = themeContainer.listDirectory()
        themes = map(str, themes)
        return themes
    
    def getThemeById(self, id):

        themeContainer = self.getThemeDirectory()
        if id in themeContainer.listDirectory():
            return self.THEME_CLASS(id, self)

        return self.THEME_CLASS(id, self)

    def getThemes(self):
        themes = []
        themeContainer = self.getThemeDirectory()

        for id in themeContainer.listDirectory():
            themes.append(self.THEME_CLASS(id, self))

        return themes


    def downloadTheme(self, data):

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
        sio = StringIO(content)

        theme = self.importThemes(sio)
        return theme

    def importThemes(self, themeArchive):
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

    def deleteTheme(self, id):
        theme = self.getThemeById(id)
        folder = self.getThemeDirectory()
        del folder[id]
        #TODO: add notification

    def updateTheme(self, id):
        #We want to support update of every provided theme
        tm = component.getUtility(interfaces.IJQueryUIThemeManager)
        theme = tm.getThemeById(id)
        params = theme.getParams()
        params['name']=id
        self.downloadTheme(params)

    def getThemeDirectory(self):

        if self._themedirectory is None:
            folder = component.getUtility(IResourceDirectory,
                                          name="persistent")
            if config.THEME_RESOURCE_NAME not in folder:
                folder.makeDirectory(config.THEME_RESOURCE_NAME)
            self._themedirectory = folder[config.THEME_RESOURCE_NAME]

        return self._themedirectory

def checkZipFile(archive):
    """Raise exception if not a zip"""
    try:
        themeZip = zipfile.ZipFile(archive)
    except (zipfile.BadZipfile, zipfile.LargeZipFile,):
        logger.exception("Could not read zip file")
        raise TypeError('error_invalid_zip')
    return themeZip

