
class FakeManager:
    def __init__(self):
        self._tool = FakeCSSTool()
        self._directory = FakeResourceDirectory()
    def csstool(self):
        return self._tool

    def getThemeDirectory(self):
        return self._directory
    
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
        self.themes = []
    
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
        if key == 'css':
            return self
        raise IndexError(key)

    def __delitem__(self, key):
        pass

    def listDirectory(self):
        return self.themes
