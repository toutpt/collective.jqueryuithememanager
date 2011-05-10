import doctest
import unittest2 as unittest

from Testing import ZopeTestCase as ztc
import base
import utils

class SunburstThemeTestCase(base.UnitTestCase):
    
    def setUp(self):
        super(SunburstThemeTestCase, self).setUp()
        from collective.jqueryuithememanager import theme
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
 