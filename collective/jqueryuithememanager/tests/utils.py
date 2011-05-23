class FakeProvider(object):
    BASE_PATH = '++resource++jquery-ui-themes/'
    VERSION='1.8.55'

    def __init__(self):
        self.themes = {}

    def getThemeIds(self):
        return self.themes.keys()

    def getThemeById(self, id):
        return self.themes.get(id,None)

    def getThemes(self):
        return self.themes.values()

class FakePersistentProvider(FakeProvider):
    BASE_PATH = 'portal_resources/jqueryuitheme/'
    VERSION='1.8.55'

    def __init__(self):
        super(FakePersistentProvider, self).__init__()
        self._directory = FakeResourceDirectory()

    def downloadTheme(self, params):
        pass

    def importThemes(archive):
        return []

    def deleteTheme(self, id):
        del self.themes[id]

    def updateTheme(self, id):
        pass

    def getThemeDirectory(self):
        return self._directory

    def getThemeIds(self):
        return self._directory.listDirectory()

class FakeManager(object):
    def __init__(self):
        self._tool = FakeCSSTool()
        self._providers = [FakePersistentProvider(), FakeProvider()]
        self._default = 'sunburst'

    def getCSSRegistry(self):
        return self._tool

    def getDefaultThemeId(self):
        return self._default
    
    def setDefaultThemeId(self, id):
        self._default = id

    def getThemesProviders(self):
        return self._providers

    def getPersistentThemesProvider(self):
        return self._providers[0]
    
    def getThemeIds(self):
        providers = self.getThemesProviders()
        ids = []
        for provider in providers:
            for id in provider.getThemeIds():
                if id not in ids:
                    ids.append(id)
        return ids

    def getThemeById(self, id):
        providers = self.getThemesProviders()
        ids = []
        for provider in providers:
            for theme in provider.getThemes():
                if theme.id == id:
                    return theme

    def getThemes(self):
        providers = self.getThemesProviders()
        themes = []
        providers = self.getThemesProviders()
        for provider in providers:
            for theme in provider.getThemes():
                themes.append(theme)
        return themes

    
class FakeCSSTool:
    def __init__(self):
        self.resources = {}

    def getResourcesDict(self):
        return self.resources

    def registerStylesheet(self, id):
        self.resources[id] = FakeStyleSheet()
        self.resources[id].setEnabled(True)

    def cookResources(self):
        pass

    def unregisterResource(self, id):
        del self.resources[id]

class FakeStyleSheet:
    def __init__(self):
        self.enabled = None
        self.prefixed = None
    
    def setEnabled(self, value):
        self.enabled = value

    def setApplyPrefix(self, value):
        self.prefixed = value

class FakeSite:
    def __init__(self):
        self.portal_css = FakeCSSTool()

class FakeRegistry:
    def __init__(self):
        self.theme = 'sunburst'


class FakeResourceDirectory:
    def __init__(self):
        self.themes = {}
    
#    def importZip(self, themeZip):
#        for name in themeZip.namelist():
#            member = themeZip.getinfo(name)
#            path = member.filename.lstrip('/')
#            starter = path.split('/')[0]
#            if starter =='css' and path.endswith('.custom.css'):
#                themeid = path.split('/')[1]
#                break
#        self.themes.append(themeid)

    def makeDirectory(self, path):
        pass
    
    def writeFile(self, path, data):
        pass

    def __getitem__(self, key):
        return self.themes[key]

    def __delitem__(self, key):
        pass

    def listDirectory(self):
        return self.themes.keys()

class FakeTheme(object):
    def __init__(self, id, provider):
        self.id = id
        self.stylesheetid = None
        self.version = None
        self.provider = provider
        self.activated = False
    def activate(self):
        self.activated = True
    
    def unactivate(self):
        self.activated = False
    def getThemeRollerLink(self):
        return 'http://jqueryui.com/themeroller'
    
    