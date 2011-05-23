from zope import component
from zope import interface

from collective.jqueryuithememanager import config
from collective.jqueryuithememanager import interfaces
from collective.jqueryuithememanager import logger

from plone.registry.interfaces import IRegistry

class ThemeManager(object):
    """implements IJQueryUIThemeManager"""
    interface.implements(interfaces.IJQueryUIThemeManager)

    def __init__(self):
        self._site = None
        self._settings = None
        self._csstool = None
        self._persistenttp = None
        self._providers = None

    def site(self):
        if self._site is None:
            self._site = component.getSiteManager()
        return self._site

    def getCSSRegistry(self):
        if self._csstool is None:
            site = self.site()
            self._csstool = site.portal_css
        return self._csstool

    def settings(self):
        if self._settings is None:
            self._settings = component.getUtility(IRegistry).forInterface(interfaces.IDefaultThemeFormSchema)
        return self._settings

    def getDefaultThemeId(self):
        """Return the configuration themeid currently used"""
        settings = self.settings()
        return settings.theme

    def setDefaultThemeId(self, themeid):
        """Set the current theme configuration to themeid"""
        settings = self.settings()
        settings.theme = themeid


    def getThemesProviders(self):
        if self._providers is not None:
            return self._providers

        providers = []
        utilities = sorted(component.getUtilitiesFor(interfaces.IThemesProvider))
        #WARNING: self is a IThemeProvier, so remove it from results
        for utility in utilities:
            name, provider = utility
            if name == 'portal_resources_jqueryuithemes':
                providers.insert(0, provider)
            elif provider is not self:
                providers.append(provider)

        self._providers = providers
        return providers

    def getPersistentThemesProvider(self):
        if self._persistenttp is not None:
            return self._persistenttp
        registry = component.getUtility(IRegistry)
        name = 'portal_resources_jqueryuithemes'
        utility = component.queryUtility(interfaces.IPersistentThemesProvider,
                                         name)
        self._persistenttp = utility
        return utility

    def getThemeIds(self):
        themes = []
        providers = self.getThemesProviders()
        for provider in providers:
            ids = provider.getThemeIds()
            for id in ids:
                if id not in themes:
                    themes.append(id)
        if 'sunburst' not in themes:
            themes.insert(0,'sunburst')
        return themes

    def getThemes(self):
        themes = []
        ids = []
        providers = self.getThemesProviders()
        for provider in providers:
            pthemes = provider.getThemes()
            for theme in pthemes:
                if theme.id not in ids:
                    ids.append(theme.id)
                    themes.append(theme)
        return themes

    def getThemeById(self, id):
        providers = self.getThemesProviders()
        for provider in providers:
            pthemes = provider.getThemes()
            for theme in pthemes:
                if theme.id == id:
                    return theme
