from zope import component
from zope import interface
from zope import schema

from plone.registry.interfaces import IRecordModifiedEvent

from plone.z3cform import layout

from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

from collective.jqueryuithememanager import config
from collective.jqueryuithememanager import interfaces
from collective.jqueryuithememanager import i18n
from collective.jqueryuithememanager import logger
from collective.jqueryuithememanager import theme

from Products.Five.browser import BrowserView
from Products.Five.browser.decode import processInputs

from zExceptions import NotFound


class MainControlPanelForm(RegistryEditForm):
    schema = interfaces.IJQueryUIThemeSettings

MainControlPanelView = layout.wrap_form(MainControlPanelForm,
                                     ControlPanelFormWrapper)
MainControlPanelView.label = i18n.maincontrolpanel_label


class CustomControlPanelForm(RegistryEditForm):
    schema = interfaces.IJQueryUITheme
    
    def applyChanges(self, data):
        super(CustomControlPanelForm, self).applyChanges(data)
        #TODO: unregister old theme
        oldtheme = theme.getCurrentThemeId()
        theme.unregisterTheme(oldtheme)
        theme.download_theme(data)
        theme.registerTheme(data['name'])
        theme.setCurrentThemeId(data['name'])


CustomControlPanelView = layout.wrap_form(CustomControlPanelForm,
                                     ControlPanelFormWrapper)
CustomControlPanelView.label = i18n.customcontrolpanel_label


class ImportThemeForm(BrowserView):

    def __call__(self):
        if self.update():
            return self.index()
        return ''

    def authorize(self):
        authenticator = component.getMultiAdapter((self.context, self.request), name=u"authenticator")
        if not authenticator.verify():
            raise Unauthorized
    
    def update(self):
        self.errors = {}
        processInputs(self.request)
        form = self.request.form

        if 'form.button.Import' in form:
            self.authorize()
            submitted = True
            themeArchive = form.get('themeArchive', None)
            theme.importTheme(themeArchive)

        return True

@component.adapter(interfaces.IJQueryUIThemeSettings, IRecordModifiedEvent)
def handleRegistryModified(settings, event):
    #FIRST: remove old resource
    oldtheme = None
    if event.record.fieldName == 'theme':
        theme.unregisterTheme(event.oldValue)
        theme.registerTheme(settings.theme)

