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
    
    def test_version(self):
        self.failUnless(self.theme.version == utils.JQUERYUI_CSS_VERSION)

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
    
    def test_version(self):
        self.failUnless(self.theme.version == utils.CUSTOM_CSS_VERSION)

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
        pass
    
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
    
    def downloadTheme(self):
        pass #already tested by the integration tests
