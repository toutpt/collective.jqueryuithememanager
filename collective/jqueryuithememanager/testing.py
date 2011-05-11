from plone.testing import z2

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting, FunctionalTesting

class CollectiveJQueryUIThemeManagerLayer(PloneSandboxLayer):
    default_bases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.js.jqueryui
        import collective.jqueryuithememanager
        import plone.app.registry
        import collective.z3cform.colorpicker
        import plone.resource
        import plone.namedfile

        self.loadZCML(package=plone.resource)
        self.loadZCML(package=plone.namedfile)
        self.loadZCML(package=plone.app.registry)
        self.loadZCML(package=collective.z3cform.colorpicker)
        self.loadZCML(package=collective.js.jqueryui)
        self.loadZCML(package=collective.jqueryuithememanager)

        # Install product and call its initialize() function
        z2.installProduct(app, 'collective.js.jqueryui')
        z2.installProduct(app, 'collective.jqueryuithememanager')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'collective.jqueryuithememanager:default')

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'collective.js.jqueryui')
        z2.uninstallProduct(app, 'collective.jqueryuithememanager')

FIXTURE = CollectiveJQueryUIThemeManagerLayer()

INTEGRATION = IntegrationTesting(bases=(FIXTURE,), name="JQUeryUIThemManager:Integration")
FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,), name="JQUeryUIThemManager:Functional")
