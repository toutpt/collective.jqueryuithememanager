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

from zExceptions import NotFound, BadRequest
from plone.autoform.form import AutoExtensibleForm
from z3c.form import form, button, browser
from plone.namedfile.field import NamedFile
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName


class MainControlPanelView(BrowserView):
    """Main control panel"""
    
    def isExampleJqueryUIEnabled(self):
        pp = getToolByName(self.context, 'portal_properties')
        try:
            return pp.jqueryui_properties.example_activated
        except AttributeError:
            return False


class SelectThemeControlPanelForm(RegistryEditForm):
    """Select a theme control panel"""
    schema = interfaces.IDefaultThemeFormSchema
    control_panel_view = "collective.jqueryuithememanager-controlpanel"

class SelectThemeControlPanelView(layout.FormWrapper):
    label = i18n.label_selectcontrolpanel
    form = SelectThemeControlPanelForm
    index = ViewPageTemplateFile('controlpanel_layout.pt')


class CustomControlPanelForm(RegistryEditForm):
    """Create or modify a theme control panel"""
    schema = interfaces.IJQueryUIThemeSettings
    control_panel_view = "collective.jqueryuithememanager-controlpanel"

    def applyChanges(self, data):
        super(CustomControlPanelForm, self).applyChanges(data)
        tm = theme.ThemeManager()
        tm.downloadTheme(data)
        IStatusMessage(self.request).addStatusMessage(i18n.msg_customtheme_changes_saved)


class CustomControlPanelView(layout.FormWrapper):
    label = i18n.customcontrolpanel_label
    form = CustomControlPanelForm
    index = ViewPageTemplateFile('controlpanel_layout.pt')


class IImportThemeForm(interface.Interface):
    """Import Theme Form schema"""

    themeArchive = schema.Bytes(title=i18n.label_theme_archive,
                                description=i18n.desc_theme_archive)

class ImportThemeForm(AutoExtensibleForm, form.Form):
    """Import Theme Form control panel (from a zipfile)"""
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
        IStatusMessage(self.request).addStatusMessage(i18n.msg_defaulttheme_loaded)
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.parent_view))



class DeleteThemeForm(AutoExtensibleForm, form.Form):
    """Delete Theme Form control panel"""
    schema = interfaces.IDeleteThemeFormSchema
    ignoreContext = True
    control_panel_view = "plone_control_panel"
    parent_view = "@@collective.jqueryuithememanager-controlpanel"
    schema_prefix = None

    @button.buttonAndHandler(i18n.action_delete_theme)
    def handleDeleteTheme(self, action):
        data, errors = self.extractData()
        abs_url=self.context.absolute_url()
        url = abs_url+'/@@collective.jqueryuithememanager-delete-theme'

        tm = theme.ThemeManager()
        badreq = False
        for themeid in data['themes']:
            try:
                tm.deleteTheme(themeid)
            except BadRequest:
                badreq = True

        if badreq:
            msg = i18n.err_deletetheme_badrequest
        else:
            msg = i18n.msg_deletetheme_changes_saved

        IStatusMessage(self.request).add(msg)
        self.request.response.redirect(url)

    @button.buttonAndHandler(i18n.action_delete_allthemes)
    def handleDeleteAllThemes(self, action):
        tm = theme.ThemeManager()
        themeids = tm.getThemeIds()
        badreq = False
        for themeid in themeids:
            if themeid == 'sunburst':continue
            try:
                tm.deleteTheme(themeid)
            except BadRequest:
                badreq = True

        if badreq:
            msg = i18n.err_deletetheme_badrequest
        else:
            msg = i18n.msg_deletethemes_changes_saved
        IStatusMessage(self.request).addStatusMessage(msg)
        abs_url=self.context.absolute_url()
        url="%s/%s" % (abs_url, self.parent_view)
        self.request.response.redirect(url)


class DeleteThemeFormWrapper(layout.FormWrapper):
    """Use this form as the plone.z3cform layout wrapper to get the control
    panel layout.
    """
    label = i18n.label_deletetheme_form
    form = DeleteThemeForm
    index = ViewPageTemplateFile('controlpanel_layout.pt')

@component.adapter(interfaces.IDefaultThemeFormSchema, IRecordModifiedEvent)
def handleRegistryModified(settings, event):
    """Handle configuration change in the registry on theme config"""
    #FIRST: remove old resource
    oldtheme = None
    if event.record.fieldName == 'theme':
        tm = theme.ThemeManager()
        oldtheme = tm.getThemeById(event.oldValue)
        newtheme = tm.getThemeById(settings.theme)
        oldtheme.unactivate()
        newtheme.activate()

class ThemesWhichNeedAnUpdate(BrowserView):
    """
    """
    def themes(self):
        """Return a list of theme object"""
        tm = theme.ThemeManager()
        themes = tm.getThemes()
        return themes

    def jsversion(self):
        return config.VERSION
    
    def needupdate(self, theme):
        return theme.version != config.VERSION
