from zope import component
from zope import interface

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from collective.jqueryuithememanager import config
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
            for id in ids:
                if ids not in themeids:
                    themeids.append(id)
        themeids.sort()
        items = [(id, id) for id in themeids]
        return SimpleVocabulary.fromItems(items)
#        except TypeError:
#            logger.info('kss inline validation ... getSite doesn t return Plone site')
#            return SimpleVocabulary.fromItems([])

    def getPersistentThemeProviders(self):
        providers = []
        names = []
        persistents = sorted(component.getUtilitiesFor(interfaces.IPersistentThemesProvider))
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
            items = [(id, id) for id in ids if id]
            return SimpleVocabulary.fromItems(items)
        except TypeError:
            logger.info('kss inline validation ... getSite doesn t return Plone site')
            return SimpleVocabulary.fromItems([('sunburst','sunburst')])

    def getThemeManager(self):
        return component.getUtility(interfaces.IJQueryUIThemeManager)

JQueryUIThemeVocabulary = JQueryUIThemeVocabularyFactory()
