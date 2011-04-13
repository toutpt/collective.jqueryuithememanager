import os
import zipfile
import StringIO

from urlparse import urlparse
from urllib import urlencode
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

def unregisterTheme(themeid):
    plone = component.getSiteManager()
    csstool = plone.portal_css

    if themeid == 'sunburst':
        return
    elif themeid == 'collective.js.jqueryui':
        css.unregisterResource('++resource++jquery.ui.all.css')
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
        csstool.unregisterResource(old_resource)
    except NotFound, e:
        logger.info('the new theme has not been found in resource directory')
    except Exception, e:
        logger.error(e)

def registerTheme(themeid):
    if themeid == 'sunburst':
        return
    elif themeid == 'collective.js.jqueryui':
        css.unregisterResource('++resource++jquery.ui.all.css')
        csstool.cookResources()
        return

    #a theme in persistent directory
    plone = component.getSiteManager()
    csstool = plone.portal_css
    BASE = 'portal_resources/%s/css/'%interfaces.THEME_RESOURCE_NAME
    themeContainer = getThemeDirectory()
    try:
        ids = themeContainer['css'][themeid].listDirectory()
        css_id = None
        for id in ids:
            if id.endswith('css'):
                css_id = id
        resource = BASE+themeid+'/'+css_id
        csstool.registerStylesheet(resource)
        csstool.cookResources()
    except NotFound, e:
        logger.info('the new theme has not been found in resource directory')
    except Exception, e:
        logger.error(e)

def download_theme(data):
    """Download the themezip directly from jqueryui.com
    
    * theme: params from theme app
    * jqueryui: {'version':'1.8.8', version of jqueryui
    * theme_fol"""
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
    theme = urlencode(datac)
    query+='&theme=?'+theme
    url = BASE+query
    logger.info(url)
    download = urlopen(url)
    code = download.getcode()

    if code != 200:
        raise Exception, 'Cant download the theme got %s code'%code
    if download.info().type != 'application/zip':
        raise Exception, 'Is not a zip file'

    sio = StringIO.StringIO(download.read())
    importTheme(sio)
    registerTheme(data['name'])