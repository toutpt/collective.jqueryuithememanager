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
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zExceptions import NotFound
from plone.autoform.form import AutoExtensibleForm
from z3c.form import form, button
from plone.namedfile.field import NamedFile
from Products.statusmessages.interfaces import IStatusMessage

import StringIO

class MainControlPanelForm(RegistryEditForm):
    schema = interfaces.IJQueryUIThemeSettings

MainControlPanelView = layout.wrap_form(MainControlPanelForm,
                                     ControlPanelFormWrapper)
MainControlPanelView.label = i18n.maincontrolpanel_label


class CustomControlPanelForm(RegistryEditForm):
    schema = interfaces.IJQueryUITheme
    
    def applyChanges(self, data):
        super(CustomControlPanelForm, self).applyChanges(data)
        tm = theme.ThemeManager()
        tm.downloadTheme(data)

CustomControlPanelView = layout.wrap_form(CustomControlPanelForm,
                                     ControlPanelFormWrapper)
CustomControlPanelView.label = i18n.customcontrolpanel_label


#class ImportThemeForm(BrowserView):
#
#    def __call__(self):
#        if self.update():
#            return self.index()
#        return ''
#
#    def authorize(self):
#        authenticator = component.getMultiAdapter((self.context, self.request), name=u"authenticator")
#        if not authenticator.verify():
#            raise Unauthorized
#    
#    def update(self):
#        self.errors = {}
#        processInputs(self.request)
#        form = self.request.form
#
#        if 'form.button.Import' in form:
#            self.authorize()
#            submitted = True
#            themeArchive = form.get('themeArchive', None)
#            theme.importTheme(themeArchive)
#
#        return True

class IImportThemeForm(interface.Interface):
    """Import Theme Form"""

    themeArchive = schema.Bytes(title=u"Theme archive")

class ImportThemeForm(AutoExtensibleForm, form.Form):
    """
    """
    schema = IImportThemeForm
    ignoreContext = True
    control_panel_view = "plone_control_panel"
    parent_view = "@@collective.jqueryuithememanager-controlpanel"
    schema_prefix = None

    @button.buttonAndHandler(u'Import')
    def handleImportTheme(self, action):
        data, errors = self.extractData()
        sio = StringIO.StringIO()
        sio.write(data['themeArchive'])
        try:
            tm = theme.ThemeManager()
            t = tm.getThemeFromZip(sio)
            IStatusMessage(self.request).addStatusMessage(u"Theme imported. You may want to select this theme.")
            self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.parent_view))
        except TypeError, e:
            IStatusMessage(self.request).add(u"You must upload a zip", type=u'error')
            self.request.response.redirect("%s/%s" % (self.context.absolute_url(), "@@jqueryui-import-theme"))
        except ValueError, e:
            IStatusMessage(self.request).add(u"You must upload a valid JQueryUI theme file", type=u'error')
            self.request.response.redirect("%s/%s" % (self.context.absolute_url(), "@@jqueryui-import-theme"))

class ImportThemeFormWrapper(layout.FormWrapper):
    """Use this form as the plone.z3cform layout wrapper to get the control
    panel layout.
    """
    label = u"Import JQueryUI Theme"
    form = ImportThemeForm
    index = ViewPageTemplateFile('controlpanel_layout.pt')

@component.adapter(interfaces.IJQueryUIThemeSettings, IRecordModifiedEvent)
def handleRegistryModified(settings, event):
    #FIRST: remove old resource
    oldtheme = None
    if event.record.fieldName == 'theme':
        tm = theme.ThemeManager()
        oldtheme = tm.getThemeById(event.oldValue)
        newtheme = tm.getThemeById(settings.theme)
        
        oldtheme.unactivate()
        newtheme.activate()
