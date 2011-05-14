import base
import utils

class ProviderTestCase(base.UnitTestCase):
    def setUp(self):
        super(TestPersistentProvider, self).setUp()
        from collective.jqueryuithememanager.browser import provider
        from collective.jqueryuithememanager import config
        self.provider = provider.BrowserResourceThemeProvider()

    def test_getThemeIds(self):
        pass
    
    def test_getThemeById(self):
        pass
    
    def test_getThemes(self):
        pass



class PersistentProviderTestCase(base.UnitTestCase):
    def setUp(self):
        super(TestPersistentProvider, self).setUp()
        from collective.jqueryuithememanager import provider
        from collective.jqueryuithememanager import config
        self.provider = provider.PersistentThemeProvider()

    def test_getThemeIds(self):
        pass
    
    def test_getThemeById(self):
        pass
    
    def test_getThemes(self):
        pass
    
    def test_downloadTheme(self):
        pass
    
    def test_deleteTheme(self):
        pass
    
    def test_updateTheme(self):
        pass

