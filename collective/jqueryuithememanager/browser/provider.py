from zope import component
from zope import interface

from collective.jqueryuithememanager import config
from collective.jqueryuithememanager import interfaces
from collective.jqueryuithememanager import logger
from collective.jqueryuithememanager import theme

class BrowserResourceThemeProvider(object):
    """Browser resource directory base theme provider"""
    interface.implements(interfaces.IThemesProvider)
    RESOURCE_NAME = 'jquery-ui-themes'
    BASE_PATH = '++resource++'+RESOURCE_NAME+'/'
    THEME_IDS = ['sunburst']
    THEME_ROLLER = {'sunburst':'http://jqueryui.com/themeroller/?ffDefault=%20Arial,FreeSans,sans-serif&fwDefault=normal&fsDefault=0.9em&cornerRadius=5px&bgColorHeader=dddddd&bgTextureHeader=01_flat.png&bgImgOpacityHeader=75&borderColorHeader=cccccc&fcHeader=444444&iconColorHeader=205c90&bgColorContent=ffffff&bgTextureContent=01_flat.png&bgImgOpacityContent=100&borderColorContent=cccccc&fcContent=444444&iconColorContent=205c90&bgColorDefault=205c90&bgTextureDefault=01_flat.png&bgImgOpacityDefault=45&borderColorDefault=cccccc&fcDefault=ffffff&iconColorDefault=ffffff&bgColorHover=dddddd&bgTextureHover=01_flat.png&bgImgOpacityHover=75&borderColorHover=448dae&fcHover=444444&iconColorHover=444444&bgColorActive=75ad0a&bgTextureActive=01_flat.png&bgImgOpacityActive=50&borderColorActive=cccccc&fcActive=ffffff&iconColorActive=ffffff&bgColorHighlight=ffdd77&bgTextureHighlight=01_flat.png&bgImgOpacityHighlight=55&borderColorHighlight=dd8800&fcHighlight=000000&iconColorHighlight=dd8800&bgColorError=ffddcc&bgTextureError=01_flat.png&bgImgOpacityError=45&borderColorError=dd0000&fcError=000000&iconColorError=dd0000&bgColorOverlay=aaaaaa&bgTextureOverlay=01_flat.png&bgImgOpacityOverlay=75&opacityOverlay=30&bgColorShadow=999999&bgTextureShadow=01_flat.png&bgImgOpacityShadow=55&opacityShadow=45&thicknessShadow=0px&offsetTopShadow=5px&offsetLeftShadow=5px&cornerRadiusShadow=5px'}
    THEME_CLASS = theme.Theme
    VERSION=config.VERSION

    def getThemeIds(self):
        return self.THEME_IDS

    def getThemeById(self, id):
        if id not in self.getThemeIds():
            raise AttributeError(id)
        return self.THEME_CLASS(id, self)

    def getThemes(self):
        return map(self.getThemeById, self.getThemeIds())

