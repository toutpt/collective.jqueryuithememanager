import base
import utils

class ThemeTestCase(base.UnitTestCase):
    
    def setUp(self):
        super(ThemeTestCase, self).setUp()
        from collective.jqueryuithememanager import theme
        from collective.jqueryuithememanager import config
        self.config = config
        self.theme_module = theme
        tm = utils.FakeManager()
        self.tm = tm
        tp = tm.getThemesProviders()[1]
        tm._providers[1].themes['sunburst'] = theme.Theme("sunburst", tp)
        self.theme = tm.getThemeById('sunburst')
        self.theme._manager = tm

    def test_stylesheetid(self):
        self.failUnless(self.theme.stylesheetid == '++resource++jquery-ui-themes/sunburst/jqueryui.css')

    def test_activate(self):
        self.theme.activate()
        stylesheet = self.theme.getThemeManager().getCSSRegistry().getResourcesDict()['++resource++jquery-ui-themes/sunburst/jqueryui.css']
        self.failUnless(stylesheet.enabled) #must be enabled
        stylesheet.enabled = False
        self.theme.activate()
        self.failUnless(stylesheet.enabled) #must have been unabled
        self.theme.unactivate()
        self.failUnless('sunburst' not in self.tm._tool.resources)


class PersistentThemeTestCase(base.UnitTestCase):
    def setUp(self):
        super(PersistentThemeTestCase, self).setUp()
        from collective.jqueryuithememanager import theme
        from collective.jqueryuithememanager import config
        self.config = config
        self.theme_module = theme
        tm = utils.FakeManager()
        self.tm = tm
        tp = tm.getPersistentThemesProvider()
        tp.themes['mytheme'] = theme.PersistentTheme("mytheme", tp)
        self.theme = tm.getThemeById('mytheme')
        self.theme._manager = tm
        self.CUSTOM_CSS_ID = 'portal_resources/jqueryuitheme/mytheme/jqueryui.css'

    def test_stylesheetid(self):
        self.failUnless(self.theme.stylesheetid == self.CUSTOM_CSS_ID)

    def test_activate(self):
        stylesheet = self.theme.getThemeManager().getCSSRegistry().getResourcesDict().get(self.CUSTOM_CSS_ID, None)
        self.failUnless(stylesheet is None) #must be enabled
        self.theme.activate()
        stylesheet = self.theme.getThemeManager().getCSSRegistry().getResourcesDict().get(self.CUSTOM_CSS_ID, None)
        self.failUnless(stylesheet is not None) #must be enabled
        self.failUnless(stylesheet.enabled) #must have been unabled
        self.failUnless(stylesheet.prefixed)

        self.theme.unactivate()
        stylesheet = self.theme.getThemeManager().getCSSRegistry().getResourcesDict().get(self.CUSTOM_CSS_ID, None)
        self.failUnless(stylesheet is None) #must be enabled
