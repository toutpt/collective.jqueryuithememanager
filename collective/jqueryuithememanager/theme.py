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
    registry = component.getUtility(IRegistry).forInterface(interfaces.IJQueryUIThemeSettings)
    return registry.theme

def setCurrentThemeId(themeid):
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
#    query += "&theme=%3FffDefault=Segoe+UI%2C+Arial%2C+sans-serif&fwDefault=bold&fsDefault=1.1em&amp;cornerRadius=6px&amp;bgColorHeader=333333&amp;bgTextureHeader=12_gloss_wave.png&amp;bgImgOpacityHeader=25&amp;borderColorHeader=333333&amp;fcHeader=ffffff&amp;iconColorHeader=ffffff&amp;bgColorContent=000000&amp;bgTextureContent=05_inset_soft.png&amp;bgImgOpacityContent=25&amp;borderColorContent=666666&amp;fcContent=ffffff&amp;iconColorContent=cccccc&amp;bgColorDefault=555555&amp;bgTextureDefault=02_glass.png&amp;bgImgOpacityDefault=20&amp;borderColorDefault=666666&amp;fcDefault=eeeeee&amp;iconColorDefault=cccccc&amp;bgColorHover=0078a3&amp;bgTextureHover=02_glass.png&amp;bgImgOpacityHover=40&amp;borderColorHover=59b4d4&amp;fcHover=ffffff&amp;iconColorHover=ffffff&amp;bgColorActive=f58400&amp;bgTextureActive=05_inset_soft.png&amp;bgImgOpacityActive=30&amp;borderColorActive=ffaf0f&amp;fcActive=ffffff&amp;iconColorActive=222222&amp;bgColorHighlight=eeeeee&amp;bgTextureHighlight=03_highlight_soft.png&amp;bgImgOpacityHighlight=80&amp;borderColorHighlight=cccccc&amp;fcHighlight=2e7db2&amp;iconColorHighlight=4b8e0b&amp;bgColorError=ffc73d&amp;bgTextureError=02_glass.png&amp;bgImgOpacityError=40&amp;borderColorError=ffb73d&amp;fcError=111111&amp;iconColorError=a83300&amp;bgColorOverlay=5c5c5c&amp;bgTextureOverlay=01_flat.png&amp;bgImgOpacityOverlay=50&amp;opacityOverlay=80&amp;bgColorShadow=cccccc&amp;bgTextureShadow=01_flat.png&amp;bgImgOpacityShadow=30&amp;opacityShadow=60&amp;thicknessShadow=7px&amp;offsetTopShadow=-7px&amp;offsetLeftShadow=-7px&amp;cornerRadiusShadow=8px"
#    query += "&theme=?ffDefault=Lucida+Grande%2C+Lucida+Sans%2C+Arial%2C+sans-serif&fwDefault=normal&fsDefault=1.1em&cornerRadius=10px&bgColorHeader=3a8104&bgTextureHeader=03_highlight_soft.png&bgImgOpacityHeader=33&borderColorHeader=3f7506&fcHeader=ffffff&iconColorHeader=ffffff&bgColorContent=285c00&bgTextureContent=05_inset_soft.png&bgImgOpacityContent=10&borderColorContent=72b42d&fcContent=ffffff&iconColorContent=72b42d&bgColorDefault=4ca20b&bgTextureDefault=03_highlight_soft.png&bgImgOpacityDefault=60&borderColorDefault=45930b&fcDefault=ffffff&iconColorDefault=ffffff&bgColorHover=4eb305&bgTextureHover=03_highlight_soft.png&bgImgOpacityHover=50&borderColorHover=8bd83b&fcHover=ffffff&iconColorHover=ffffff&bgColorActive=285c00&bgTextureActive=04_highlight_hard.png&bgImgOpacityActive=30&borderColorActive=72b42d&fcActive=ffffff&iconColorActive=ffffff&bgColorHighlight=fbf5d0&bgTextureHighlight=02_glass.png&bgImgOpacityHighlight=55&borderColorHighlight=f9dd34&fcHighlight=363636&iconColorHighlight=4eb305&bgColorError=ffdc2e&bgTextureError=08_diagonals_thick.png&bgImgOpacityError=95&borderColorError=fad000&fcError=2b2b2b&iconColorError=cd0a0a&bgColorOverlay=444444&bgTextureOverlay=08_diagonals_thick.png&bgImgOpacityOverlay=15&opacityOverlay=30&bgColorShadow=aaaaaa&bgTextureShadow=07_diagonals_small.png&bgImgOpacityShadow=0&opacityShadow=30&thicknessShadow=0px&offsetTopShadow=4px&offsetLeftShadow=4px&cornerRadiusShadow=4px"
    url = BASE+query
    logger.info(url)

    download = urlopen(BASE, query)
    code = download.getcode()

    if code != 200:
        raise Exception, 'Cant download the theme got %s code'%code
    if download.info().type != 'application/zip':
        raise Exception, 'Is not a zip file'
    f = open('test.zip', 'wb')
    content = download.read()
    f.write(content)
    sio = StringIO.StringIO(content)
    importTheme(sio)
