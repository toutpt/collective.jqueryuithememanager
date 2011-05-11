import doctest
import unittest2 as unittest

from Testing import ZopeTestCase as ztc
import base
import utils

class SunburstThemeTestCase(base.UnitTestCase):
    
    def setUp(self):
        super(SunburstThemeTestCase, self).setUp()
        from collective.jqueryuithememanager import theme
        self.theme_module = theme
        self.theme = theme.SunburstTheme("sunburst", utils.FakeManager())
    
    def test_stylesheetid(self):
        self.failUnless(self.theme.stylesheetid == utils.JQUERYUI_CSS_ID)
    
    def test_activate(self):
        stylesheet = self.theme.manager.csstool().getResourcesDict()[utils.JQUERYUI_CSS_ID]
        self.failUnless(stylesheet.enabled) #must be enabled
        stylesheet.enabled = False
        self.theme.activate()
        self.failUnless(stylesheet.enabled) #must have been unabled

    def test_unactivate(self):
        stylesheet = self.theme.manager.csstool().getResourcesDict()[utils.JQUERYUI_CSS_ID]
        self.failUnless(stylesheet.enabled) #must be enabled
        self.theme.unactivate()
        self.failUnless(not stylesheet.enabled) #must have been unabled


class PersistentThemeTestCase(base.UnitTestCase):
    def setUp(self):
        super(PersistentThemeTestCase, self).setUp()
        from collective.jqueryuithememanager import theme
        tm = utils.FakeManager()
        tm.csstool().registerStylesheet(utils.CUSTOM_CSS_ID)
        self.theme = theme.PersistentTheme(utils.CUSTOM_THEME_NAME, tm)

    def test_stylesheetid(self):
        self.failUnless(self.theme.stylesheetid == utils.CUSTOM_CSS_ID)

    def test_activate(self):
        stylesheet = self.theme.manager.csstool().getResourcesDict()[utils.CUSTOM_CSS_ID]
        self.failUnless(stylesheet.enabled) #must be enabled
        stylesheet.enabled = False
        self.theme.activate()
        self.failUnless(stylesheet.enabled) #must have been unabled
        self.failUnless(stylesheet.prefixed)

    def test_unactivate(self):
        stylesheet = self.theme.manager.csstool().getResourcesDict()[utils.CUSTOM_CSS_ID]
        self.failUnless(stylesheet.enabled) #must be enabled
        self.theme.unactivate()
        self.failUnless(not stylesheet.enabled) #must have been unabled

class ThemeManagerTestCase(base.UnitTestCase):
    def setUp(self):
        super(ThemeManagerTestCase, self).setUp()
        from collective.jqueryuithememanager import theme
        self.theme_module = theme
        self.tm = theme.ThemeManager()
        self.tm._site = utils.FakeSite()
        self.tm._settings = utils.FakeRegistry()
        self.tm._themedirectory = utils.FakeResourceDirectory()

    def test_getThemesIds(self):
        ids = self.tm.getThemeIds()
        self.failUnless(len(ids)==1)
        self.failUnless(ids[0]=='sunburst')
        self.tm._themedirectory.themes.append('testtheme')
        ids = self.tm.getThemeIds()
        self.failUnless(len(ids)==2)
        self.failUnless(ids[1]=='testtheme')

    
    def test_getThemeById(self):
        #non existing id are used to create new theme
        t = self.tm.getThemeById('notexisting')
        self.failUnless(type(t) is self.theme_module.PersistentTheme)
        self.failUnless(t.stylesheetid is None)
        
        sunburst = self.tm.getThemeById("sunburst")
        self.failUnless(type(sunburst) is self.theme_module.SunburstTheme)
        self.failUnless(sunburst.stylesheetid == utils.JQUERYUI_CSS_ID)
    
    def test_defaultThemeId(self):
        self.failUnless(self.tm.getDefaultThemeId() == 'sunburst')
        self.tm.setDefaultThemeId('testtheme')
        self.failUnless(self.tm.getDefaultThemeId() == 'testtheme')
    
    def test_downloadTheme(self):
        data= {'name': 'testtheme',
               'fwDefault': 'normal', 'bgTextureHover': 'normal', 
               'cornerRadiusShadow': '5px', 'fcHover': '#444444',
               'bgTextureShadow': None, 'fcHighlight': '#dd8800',
               'iconColorHover': '#444444', 'fcHeader': '#444444',
               'bgColorError': '#ffddcc', 'bgImgOpacityHover': '75',
               'bgTextureContent': None, 'thicknessShadow': '0px',
               'borderColorHover': '#ae4456', 'bgImgOpacityError': '45',
               'iconColorDefault': '#ffffff', 'fcDefault': '#ffffff',
               'opacityShadow': '45', 'bgImgOpacityDefault': '45',
               'fcActive': '#ffffff', 'bgImgOpacityHighlight': '55',
               'borderColorHighlight': '#dd8800', 'bgImgOpacityOverlay': '75',
               'bgColorOverlay': '#aaaaaa', 'bgTextureError': None,
               'bgColorHeader': u'#dddddd',
               'fsDefault': '1.2em', 'iconColorHighlight': '#000000',
               'bgColorHighlight': '#ffdd77', 'iconColorContent': '#90202b',
               'opacityOverlay': '30', 'borderColorContent': '#cccccc',
               'ffDefault': 'Arial,FreeSans,sans-serif',
               'iconColorHeader': '#902042', 'fcContent': '#444444',
               'bgImgOpacityContent': '100', 'borderColorHeader': '#cccccc',
               'fcError': '#dd0000', 'iconColorActive': '#ffffff',
               'borderColorActive': '#cccccc', 'bgColorActive': '#75ad0a',
               'cornerRadius': '5px', 'bgTextureHeader': None,
               'bgTextureHighlight': None, 'bgTextureOverlay': None,
               'bgColorDefault': '#902320', 'borderColorError': '#dd0000',
               'bgTextureDefault': None, 'bgColorHover': '#dddddd',
               'bgColorShadow': '#999999',
               'offsetLeftShadow': '5px', 'bgColorContent': '#ffffff',
               'iconColorError': '#000000', 'bgImgOpacityShadow': '55',
               'bgImgOpacityHeader': '75', 'bgTextureActive': None,
               'borderColorDefault': '#cccccc', 'bgImgOpacityActive': '50',
               'offsetTopShadow': '5px'}
        self.tm.downloadTheme(data)
        self.tm

    def test_getThemesFromZip(self):
        pass
    
