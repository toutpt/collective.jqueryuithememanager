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

BASE = "http://jqueryui.com/themeroller/?ctl=themeroller&"
SUNBURST_CSS_ID = "++resource++jquery-ui-themes/sunburst/jquery-ui-1.8.9.custom.css"

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

def importTheme(themeArchive):
    """Import a zipfile as persistent resource"""
    try:
        themeZip = zipfile.ZipFile(themeArchive)
    except (zipfile.BadZipfile, zipfile.LargeZipFile,):
        logger.exception("Could not read zip file")
        raise TypeError('error_invalid_zip')

    infos = {}
    for name in themeZip.namelist():
        member = themeZip.getinfo(name)
        path = member.filename.lstrip('/')
        starter = path.split('/')[0]
        if starter =='css' and 'name' not in infos:
            infos['name'] = path.split('/')[1]
        if starter == 'js' and 'version' not in infos:
            basename = os.path.basename(path)
            if basename.startswith('jquery-ui'):
                infos['version'] = basename[len('jquery-ui-'):len('.custom.min.js')]
        themeContainer = getThemeDirectory()
    themeContainer.importZip(themeZip)
    for i in ('index.html', 'development-bundle', 'js'):
        del themeContainer[i]
    oldTheme = getCurrentThemeId()
    unregisterTheme(oldTheme)
    registerTheme(infos['name'])
    setCurrentThemeId(infos['name'])

def getThemeDirectory():
    """Obtain the 'jqueryuitheme' persistent resource directory,
    creating it if necessary.
    """
    persistentDirectory = component.getUtility(IResourceDirectory, name="persistent")
    if interfaces.THEME_RESOURCE_NAME not in persistentDirectory:
        persistentDirectory.makeDirectory(interfaces.THEME_RESOURCE_NAME)

    return persistentDirectory[interfaces.THEME_RESOURCE_NAME]

def getThemes():
    """Return the list of available themes"""
    items = []
    site = getSite()
    themeContainer = getThemeDirectory()
    themes = themeContainer['css'].listDirectory()
    return map(str, themes)

def getCurrentThemeId():
    """Return the configuration themeid currently used"""
    registry = component.getUtility(IRegistry).forInterface(interfaces.IJQueryUIThemeSettings)
    return registry.theme

def setCurrentThemeId(themeid):
    """Set the current theme configuration to themeid"""
    registry = component.getUtility(IRegistry).forInterface(interfaces.IJQueryUIThemeSettings)
    registry.theme = themeid

def unregisterTheme(themeid):
    """Disable stylesheet corresponding to the theme"""
    logger.info('unregisterTheme %s'%themeid)
    plone = component.getSiteManager()
    csstool = plone.portal_css
    if themeid in ('collective.js.jqueryui','sunburst'):
        stylesheet = csstool.getResourcesDict()[SUNBURST_CSS_ID]
        stylesheet.setEnabled(False)
        csstool.cookResources()
        return

    #a theme in persistent directory
    BASE = 'portal_resources/%s/css/'%interfaces.THEME_RESOURCE_NAME
    themeContainer = getThemeDirectory()
    try:
        ids = themeContainer['css'][themeid].listDirectory()
        css_id = None
        for id in ids:
            if id.endswith('css'):
                css_id = id
        old_resource = BASE+themeid+'/'+css_id
        stylesheet = csstool.getResourcesDict()[old_resource]
        stylesheet.setEnabled(False)
        csstool.cookResources()
    except NotFound, e:
        logger.info('the old theme has not been found in resource directory')
    except Exception, e:
        logger.error(e)

def registerTheme(themeid):
    """Check if the css is already registred in the css tool.
    If already registred -> just activate it
    else register it and activate it
    """
    logger.info('registerTheme %s'%themeid)
    plone = component.getSiteManager()
    csstool = plone.portal_css
    
    if themeid in ('collective.js.jqueryui', 'sunburst'):
        #just activate it
        stylesheet = csstool.getResourcesDict()[SUNBURST_CSS_ID]
        stylesheet.setEnabled(True)
        csstool.cookResources()
        return

    #a theme in persistent directory
    BASE = 'portal_resources/%s/css/'%interfaces.THEME_RESOURCE_NAME
    themeContainer = getThemeDirectory()
    try:
        ids = themeContainer['css'][themeid].listDirectory()
        css_id = None
        for id in ids:
            if id.endswith('css'):
                css_id = id
        resource = BASE+themeid+'/'+css_id
        #check if already registred
        stylesheet = csstool.getResourcesDict().get(resource, None)
        if stylesheet is None:
            csstool.registerStylesheet(resource)
        stylesheet = csstool.getResourcesDict().get(resource, None)
        stylesheet.setApplyPrefix(True)
        stylesheet.setEnabled(True)
        csstool.cookResources()
    except NotFound, e:
        logger.info('the new theme has not been found in resource directory')
    except Exception, e:
        logger.error(e)

def download_theme(data):
    """Download the themezip directly from jqueryui.com
    """

    BASE = "http://jqueryui.com/download/?download=true"
    query = ''

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
    theme = urlencode(datac).replace('%23','')
    query+='&theme=?'+quote(theme)

    download = urlopen(BASE, query)
    code = download.getcode()

    if code != 200:
        raise Exception, 'Cant download the theme got %s code'%code
    if download.info().type != 'application/zip':
        raise Exception, 'Is not a zip file'
    content = download.read()
    sio = StringIO.StringIO(content)
    importTheme(sio)
