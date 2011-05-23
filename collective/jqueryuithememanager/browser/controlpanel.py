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

def getThemeManager():
    return component.getUtility(interfaces.IJQueryUIThemeManager)

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
        tm = getThemeManager()
        tp = tm.getPersistentThemesProvider()
        tp.downloadTheme(data)
        IStatusMessage(self.request).add(i18n.msg_customtheme_changes_saved)


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
            tm = getThemeManager()
            tp = tm.getPersistentThemesProvider()
            themes = tp.importThemes(sio)
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
        tm = getThemeManager()
        tp = tm.getPersistentThemesProvider()
        themes = tp.importThemes(themeArchive) #load themes !
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

        tm = getThemeManager()
        tp = tm.getPersistentThemesProvider()
        badreq = False
        for themeid in data['themes']:
            try:
                tp.deleteTheme(themeid)
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
        tm = getThemeManager()
        tp = tm.getPersistentThemesProvider()
        themeids = tp.getThemeIds()
        badreq = False
        for themeid in themeids:
            try:
                tp.deleteTheme(themeid)
            except BadRequest:
                badreq = True

        if badreq:
            msg = i18n.err_deletetheme_badrequest
        else:
            msg = i18n.msg_deletethemes_changes_saved
        IStatusMessage(self.request).add(msg)
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


class ThemesWhichNeedAnUpdate(BrowserView):
    """
    """
    def themes(self):
        """Return a list of theme object"""
        tm = getThemeManager()
        themes = tm.getThemes()
        return themes

    def jsversion(self):
        return config.VERSION
    
    def needupdate(self, theme):
        return theme.version != config.VERSION


class UpdateTheme(BrowserView):
    """Update a theme"""
    def __call__(self):
        id = self.request.get('id')
        tm = getThemeManager()
        tp = tm.getPersistentThemesProvider()
        tp.updateTheme(id)
        abs_url = self.context.absolute_url()
        url="%s/collective.jqueryuithememanager-update-themes"%abs_url 
        msg = u"Theme has been updated"

        IStatusMessage(self.request).add(msg)
        self.request.response.redirect(url)

