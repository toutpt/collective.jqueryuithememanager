from zope import component

from plone.registry.interfaces import IRecordModifiedEvent

from collective.jqueryuithememanager import interfaces

@component.adapter(interfaces.IDefaultThemeFormSchema, IRecordModifiedEvent)
def handleRegistryModified(settings, event):
    """Handle configuration change in the registry on theme config"""
    #FIRST: remove old resource
    oldtheme = None
    if event.record.fieldName == 'theme':
        tm = component.getUtility(interfaces.IJQueryUIThemeManager)
        oldtheme = tm.getThemeById(event.oldValue)
        newtheme = tm.getThemeById(settings.theme)
        oldtheme.unactivate()
        newtheme.activate()
