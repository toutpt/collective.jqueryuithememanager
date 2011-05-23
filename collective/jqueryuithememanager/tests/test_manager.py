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
        self.tm._persistenttp = utils.FakePersistentProvider()
        self.tm._providers = [self.tm._persistenttp, utils.FakeProvider()]

    def test_getThemeIds(self):
        ids = self.tm.getThemeIds()
        self.failUnless(len(ids)==1)
        self.failUnless(ids[0]=='sunburst')
        #lets add a theme
        testtheme = utils.FakeTheme('testtheme',self.tm.getPersistentThemesProvider())
        self.tm._persistenttp._directory.themes['testtheme'] = testtheme
        ids = self.tm.getThemeIds()
        self.failUnless(len(ids)==2)
        self.failUnless(ids[1]=='testtheme')

    def test_getThemeById(self):
        t = self.tm.getThemeById('notexisting')
        from collective.jqueryuithememanager import theme
        self.failUnless(t is None)

    def test_defaultThemeId(self):
        self.failUnless(self.tm.getDefaultThemeId() == 'sunburst')
        self.tm.setDefaultThemeId('testtheme')
        self.failUnless(self.tm.getDefaultThemeId() == 'testtheme')

