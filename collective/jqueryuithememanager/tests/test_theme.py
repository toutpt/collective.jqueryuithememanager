from collective.jqueryuithememanager.tests import base

class Test(base.UnitTestCase):
    
    def testTest(self):
        self.assertEqual(1, 1)

class TestIntegration(base.TestCase):
    
    def testTest(self):
        self.failUnless(1==1)

