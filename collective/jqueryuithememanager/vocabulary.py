from zope import component
from zope import interface

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from collective.jqueryuithememanager import interfaces
from collective.jqueryuithememanager import logger


class PersistentThemeVocabularyFactory(object):
    """Vocabulary for jqueryui themes.
    """
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        """Retrieve available themes inside persistent resource and add
        sunburst and collective.js.jqueryui themes"""
        providers = self.getPersistentThemeProviders()
        themeids = []
        for provider in providers:
            ids = provider.getThemeIds()
            for themeid in ids:
                if ids not in themeids:
                    themeids.append(themeid)
        themeids.sort()
        items = [(themeid, themeid) for themeid in themeids]
        return SimpleVocabulary.fromItems(items)

    def getPersistentThemeProviders(self):
        providers = []
        names = []
        iface = interfaces.IPersistentThemesProvider
        persistents = sorted(component.getUtilitiesFor(iface))
        for utility in persistents:
            name, provider = utility
            names.append(name)
            providers.append(provider)

        return providers

PersistentThemeVocabulary = PersistentThemeVocabularyFactory()


class JQueryUIThemeVocabularyFactory(object):
    """Add sunburst theme to persistent"""
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        """Retrieve available themes inside persistent resource and add
        sunburst and collective.js.jqueryui themes"""
        tm = self.getThemeManager()
        try:
            ids = tm.getThemeIds()
            ids.sort()
            items = [(themeid, themeid) for themeid in ids if id]
            return SimpleVocabulary.fromItems(items)
        except TypeError:
            msg = 'kss inline validation ... getSite doesn t return Plone site'
            logger.info(msg)
            return SimpleVocabulary.fromItems([('sunburst', 'sunburst')])

    def getThemeManager(self):
        return component.getUtility(interfaces.IJQueryUIThemeManager)

JQueryUIThemeVocabulary = JQueryUIThemeVocabularyFactory()
