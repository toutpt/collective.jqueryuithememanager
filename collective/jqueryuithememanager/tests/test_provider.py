import base
import utils

class ProviderTestCase(base.UnitTestCase):
    def setUp(self):
        super(ProviderTestCase, self).setUp()
        from collective.jqueryuithememanager.browser import provider
        from collective.jqueryuithememanager import config
        self.provider = provider.BrowserResourceThemeProvider()

    def test_getThemeIds(self):
        ids = self.provider.getThemeIds()
        self.failUnless(len(ids)==1)
        self.failUnless(ids[0]=='sunburst')
    
    def test_getThemeById(self):
        t = self.provider.getThemeById('sunburst')
        self.failUnless(t is not None)
        self.failUnless(t.id == 'sunburst')
        self.failUnless(type(t) == self.provider.THEME_CLASS)
        self.assertRaises(AttributeError, self.provider.getThemeById, 'no')
    
    def test_getThemes(self):
        themes = self.provider.getThemes()
        self.failUnless(len(themes)==1)
        self.failUnless(themes[0].id=='sunburst')



class PersistentProviderTestCase(base.UnitTestCase):
    def setUp(self):
        super(PersistentProviderTestCase, self).setUp()
        from collective.jqueryuithememanager import provider
        from collective.jqueryuithememanager import config
        self.provider = provider.PersistentThemeProvider()
        self.provider._themedirectory = utils.FakeResourceDirectory()
        self.provider.THEME_CLASS = utils.FakeTheme

    def test_getThemeIds(self):
        ids = self.provider.getThemeIds()
        self.failUnless(len(ids)==0)
        self.provider._themedirectory.themes['toto'] = None
        ids = self.provider.getThemeIds()
        self.failUnless(len(ids)==1)
        
    
    def test_getThemeById(self):
        self.provider._themedirectory.themes['toto'] = None
        theme = self.provider.getThemeById('toto')
        self.failUnless(theme is not None)
    
    def test_getThemes(self):
        pass
    
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
        pass
    
    def test_deleteTheme(self):
        pass
    
    def test_updateTheme(self):
        pass

