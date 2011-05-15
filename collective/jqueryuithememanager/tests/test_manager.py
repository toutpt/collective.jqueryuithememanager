import base
import utils


class ThemeManagerTestCase(base.UnitTestCase):
    def setUp(self):
        super(ThemeManagerTestCase, self).setUp()
        from collective.jqueryuithememanager import manager
        from collective.jqueryuithememanager import config
        self.config = config
        self.tm = manager.ThemeManager()
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
        from collective.jqueryuithememanager import theme
        self.failUnless(type(t) is theme.PersistentTheme)
        self.failUnless(t.stylesheetid=='portal_resources/jqueryuitheme/notexisting/jqueryui.css')

    def test_defaultThemeId(self):
        self.failUnless(self.tm.getDefaultThemeId() == 'sunburst')
        self.tm.setDefaultThemeId('testtheme')
        self.failUnless(self.tm.getDefaultThemeId() == 'testtheme')

