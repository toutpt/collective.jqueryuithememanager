JQUERYUI_CSS_ID = "++resource++jquery-ui-themes/sunburst/jquery-ui-1.8.12.custom.css"
JQUERYUI_CSS_VERSION = "1.8.12"

class FakeManager:
    def __init__(self):
        self._tool = FakeCSSTool()
    
    def csstool(self):
        return self._tool
    
class FakeCSSTool:
    def __init__(self):
        self.resources = {}
        self.registerStylesheet(JQUERYUI_CSS_ID)

    def getResourcesDict(self):
        return self.resources
    
    def registerStylesheet(self, id):
        self.resources[id] = FakeStyleSheet()
        self.resources[id].setEnabled(True)
    
    def cookResources(self):
        pass

class FakeStyleSheet:
    def __init__(self):
        self.enabled = None
    
    def setEnabled(self, value):
        self.enabled = value
