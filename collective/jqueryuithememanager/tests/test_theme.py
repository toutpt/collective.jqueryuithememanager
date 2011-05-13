import base
import utils

class SunburstThemeTestCase(base.UnitTestCase):
    
    def setUp(self):
        super(SunburstThemeTestCase, self).setUp()
        from collective.jqueryuithememanager import theme
        from collective.jqueryuithememanager import config
        self.config = config
        self.theme_module = theme
        tm = utils.FakeManager()
        tm.getCSSRegistry().registerStylesheet(config.SUNBURST_CSS_ID)
        tp = tm.getThemesProviders()[1]
        tm._providers[1].themes['sunburst'] = theme.SunburstTheme("sunburst", tp)
        self.theme = tm.getThemeById('sunburst')

    def test_stylesheetid(self):
        self.failUnless(self.theme.stylesheetid == self.config.SUNBURST_CSS_ID)

    def test_activate(self):
        stylesheet = self.theme.manager.csstool().getResourcesDict()[self.config.SUNBURST_CSS_ID]
        self.failUnless(stylesheet.enabled) #must be enabled
        stylesheet.enabled = False
        self.theme.activate()
        self.failUnless(stylesheet.enabled) #must have been unabled

    def test_unactivate(self):
        stylesheet = self.theme.manager.csstool().getResourcesDict()[self.config.SUNBURST_CSS_ID]
        self.failUnless(stylesheet.enabled) #must be enabled
        self.theme.unactivate()
        self.failUnless(not stylesheet.enabled) #must have been unabled


class PersistentThemeTestCase(base.UnitTestCase):
    def setUp(self):
        super(PersistentThemeTestCase, self).setUp()
        from collective.jqueryuithememanager import theme
        from collective.jqueryuithememanager import config
        self.config = config
        self.theme_module = theme
        tm = utils.FakeManager()
        tm.getCSSRegistry().registerStylesheet(config.SUNBURST_CSS_ID)
        tp = tm.getThemesProviders()[1]
        tp.themes['mytheme'] = theme.PersistentTheme("mytheme", tp)
        self.theme = tm.getThemeById('mytheme')
        self.CUSTOM_CSS_ID = 'portal_resources/jqueryuitheme/mytheme/jqueryui.css'

    def test_stylesheetid(self):
        self.failUnless(self.theme.stylesheetid == self.CUSTOM_CSS_ID)

    def test_activate(self):
        stylesheet = self.theme.manager.csstool().getResourcesDict().get(self.CUSTOM_CSS_ID, None)
        self.failUnless(stylesheet is None) #must be enabled
        self.theme.activate()
        stylesheet = self.theme.manager.csstool().getResourcesDict().get(self.CUSTOM_CSS_ID, None)
        self.failUnless(stylesheet is not None) #must be enabled
        self.failUnless(stylesheet.enabled) #must have been unabled
        self.failUnless(stylesheet.prefixed)

        self.theme.unactivate()
        stylesheet = self.theme.manager.csstool().getResourcesDict().get(self.CUSTOM_CSS_ID, None)
        self.failUnless(stylesheet is None) #must be enabled
