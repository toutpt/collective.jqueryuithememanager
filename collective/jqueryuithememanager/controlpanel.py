import urllib
import StringIO

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


class MainControlPanelForm(RegistryEditForm):
    schema = interfaces.IJQueryUIThemeSettings

MainControlPanelView = layout.wrap_form(MainControlPanelForm,
                                     ControlPanelFormWrapper)
MainControlPanelView.label = i18n.maincontrolpanel_label


class CustomControlPanelForm(RegistryEditForm):
    schema = interfaces.IJQueryUITheme
    parent_view = "collective.jqueryuithememanager-controlpanel"

    def applyChanges(self, data):
        super(CustomControlPanelForm, self).applyChanges(data)
        tm = theme.ThemeManager()
        tm.downloadTheme(data)
        IStatusMessage(self.request).addStatusMessage(i18n.msg_customtheme_changes_saved)
        url = "%s/%s" % (self.context.absolute_url(), self.parent_view)
        self.request.response.redirect(url)


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

    themeArchive = schema.Bytes(title=i18n.label_theme_archive,
                                description=i18n.desc_theme_archive)

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
        abs_url=self.context.absolute_url()
        try:
            tm = theme.ThemeManager()
            themes = tm.getThemesFromZip(sio)
            msg = i18n.msg_importtheme_changes_saved
            IStatusMessage(self.request).addStatusMessage(msg)
            url="%s/%s" % (abs_url, self.parent_view)
            self.request.response.redirect(url)
        except TypeError, e:
            IStatusMessage(self.request).add(i18n.err_importtheme_typeerror,
                                             type=u'error')
            url="%s/%s" % (abs_url,"@@jqueryui-import-theme")
            self.request.response.redirect(url)
        except ValueError, e:
            IStatusMessage(self.request).add(i18n.err_importtheme_valueerror,
                                             type=u'error')
            url="%s/%s" % (abs_url, "@@jqueryui-import-theme")
            self.request.response.redirect(url)

class ImportThemeFormWrapper(layout.FormWrapper):
    """Use this form as the plone.z3cform layout wrapper to get the control
    panel layout.
    """
    label = i18n.label_importtheme_form
    form = ImportThemeForm
    index = ViewPageTemplateFile('controlpanel_layout.pt')


class LoadDefaultThemes(BrowserView):
    """This view load all default themes"""
    parent_view = "@@collective.jqueryuithememanager-controlpanel"

    def __call__(self):
        url = "http://jquery-ui.googlecode.com/files/jquery-ui-themes-%s.zip"%(config.VERSION)
        jqueryui_content = urllib.urlopen(url).read()
        themeArchive = StringIO.StringIO(jqueryui_content)
        tm = theme.ThemeManager()
        tm.getThemesFromZip(themeArchive)
        IStatusMessage(self.request).addStatusMessage(u"Default themes as been loaded.")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.parent_view))



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
