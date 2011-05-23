from zope import interface
from zope import schema
from zope.schema import vocabulary

from collective.jqueryuithememanager import i18n
from collective.jqueryuithememanager import config

class IJQueryUIThemeManagerLayer(interface.Interface):
    """Browser layer"""



class IThemesProvider(interface.Interface):
    """A IThemeProver object is a registry of theme in read only mode.
    It is used as an entry point for external add-ons who want to provide
    jqueryuitheme. It can be seen has a theme container"""
    
    def getThemeIds():
        """Return a list of all theme ids"""

    def getThemeById(id):
        """Return the theme with id=id. If the theme doesn't exist it create
        a new one but doesn't create resources. You must use theme manager
        for that. If id is None return None"""

    def getThemes():
        """Return a list of ITheme objects"""

class IJQueryUITheme(interface.Interface):
    """A JQueryUI Theme object."""
    
    stylesheetid = schema.ASCIILine(title=u"Stylesheet ID")
    
    version = schema.ASCIILine(title=i18n.label_theme_version)
    
    provider = schema.Object(title=u"theme provider", schema=IThemesProvider)
    
    def activate():
        """Register the theme in the css registry."""
    
    def unactivate():
        """Unregister the theme from the css registry."""

    def getThemeRollerLink():
        """Return the link to jqueryui.com/themeroller to configure it"""



class IPersistentThemesProvider(IThemesProvider):
    """A persistent theme provider is an extended IThemesProvider. You can
    add, modify, delete, import themes.
    """

    def downloadTheme(params):
        """Download theme from jqueryui.com base on provided properties.
        return IJQueryUITheme object
        """

    def importThemes(archive):
        """import themes from archive"""

    def deleteTheme(id):
        """Delete a theme. If the theme is used as default, the system default
        (undeletable) theme will be set as default."""

    def updateTheme(id):
        """Update a theme to fit with the js system version"""

class IJQueryUIThemeManager(IThemesProvider):
    """A IJQueryUITheme manager, is an aggregation of IThemesProvider with
    a peristent theme provider to be able to customize a theme
    """

    def getDefaultThemeId():
        """Return the default theme id"""

    def setDefaultThemeId(id):
        """Set the default theme used by the theme manager"""

    def getThemesProviders():
        """Return a list of IThemesProvider. The persistent themesProvider
        is the first, it as precedence on all other ones. It is like the
        custom folder in portal_skin."""

    def getCSSRegistry():
        """Return the css registry"""

    def getPersistentThemesProvider():
        """Return the default theme provider to use for create, modify themes"""

class IJQueryUIThemeSettings(interface.Interface):
    """Define a JQuery UI Theme"""
    
    name = schema.ASCIILine(title=i18n.themename)
    
    #Fonts
    fwDefault = schema.ASCIILine(title=i18n.fwDefault,
                                 default='normal')
    ffDefault = schema.ASCIILine(title=i18n.ffDefault,
                                 default='Arial,FreeSans,sans-serif')
    fsDefault = schema.ASCIILine(title=i18n.fsDefault,
                                 default='1.2em')
    
    #corner
    cornerRadius = schema.ASCIILine(title=i18n.cornerRadius,
                                 default='5px')
    
    #header/toolbar
    bgColorHeader = schema.TextLine(title=i18n.bgColorHeader,
                                 default=u'#dddddd')
    bgImgOpacityHeader = schema.ASCIILine(title=i18n.bgImgOpacityHeader,
                                 default='75')
    bgTextureHeader = schema.ASCIILine(title=i18n.bgTextureHeader,
                                 required=False)
    borderColorHeader = schema.ASCIILine(title=i18n.borderColorHeader,
                                 default='#cccccc')
    iconColorHeader = schema.ASCIILine(title=i18n.iconColorHeader,
                                 default='#205c90')
    fcHeader = schema.ASCIILine(title=i18n.fcHeader,
                                 default='#444444')
    
    #content
    bgColorContent = schema.ASCIILine(title=i18n.bgColorContent,
                                 default='#ffffff')
    bgImgOpacityContent = schema.ASCIILine(title=i18n.bgImgOpacityContent,
                                 default='100')
    bgTextureContent = schema.ASCIILine(title=i18n.bgTextureContent,
                                 required=False)
    borderColorContent = schema.ASCIILine(title=i18n.borderColorContent,
                                 default='#cccccc')
    iconColorContent = schema.ASCIILine(title=i18n.iconColorContent,
                                 default='#205c90')
    fcContent = schema.ASCIILine(title=i18n.fcContent,
                                 default='#444444')
    
    #clickable default state
    bgColorDefault = schema.ASCIILine(title=i18n.bgColorDefault,
                                 default='#205c90')
    bgImgOpacityDefault = schema.ASCIILine(title=i18n.bgImgOpacityDefault,
                                 default='45')
    bgTextureDefault = schema.ASCIILine(title=i18n.bgTextureDefault,
                                 required=False)
    borderColorDefault = schema.ASCIILine(title=i18n.borderColorDefault,
                                 default='#cccccc')
    iconColorDefault = schema.ASCIILine(title=i18n.iconColorDefault,
                                 default='#ffffff')
    fcDefault = schema.ASCIILine(title=i18n.fcDefault,
                                 default='#ffffff')

    #clickable hover state
    bgColorHover = schema.ASCIILine(title=i18n.bgColorHover,
                                 default='#dddddd')
    bgImgOpacityHover = schema.ASCIILine(title=i18n.bgImgOpacityHover,
                                 default='75')
    bgTextureHover = schema.ASCIILine(title=i18n.bgTextureHover,
                                 default='normal')
    borderColorHover = schema.ASCIILine(title=i18n.borderColorHover,
                                 default='#448dae')
    iconColorHover = schema.ASCIILine(title=i18n.iconColorHover,
                                 default='#444444')
    fcHover = schema.ASCIILine(title=i18n.fcHover,
                                 default='#444444')
    
    #clickable active state
    bgColorActive = schema.ASCIILine(title=i18n.bgColorActive,
                                 default='#75ad0a')
    bgImgOpacityActive = schema.ASCIILine(title=i18n.bgImgOpacityActive,
                                 default='50')
    bgTextureActive = schema.ASCIILine(title=i18n.bgTextureActive,
                                 required=False)
    borderColorActive = schema.ASCIILine(title=i18n.borderColorActive,
                                 default='#cccccc')
    iconColorActive = schema.ASCIILine(title=i18n.iconColorActive,
                                 default='#ffffff')
    fcActive = schema.ASCIILine(title=i18n.fcActive,
                                 default='#ffffff')

    #highlight
    bgColorHighlight = schema.ASCIILine(title=i18n.bgColorHighlight,
                                 default='#ffdd77')
    bgImgOpacityHighlight = schema.ASCIILine(title=i18n.bgImgOpacityHighlight,
                                 default='55')
    bgTextureHighlight = schema.ASCIILine(title=i18n.bgTextureHighlight,
                                 required=False)
    borderColorHighlight = schema.ASCIILine(title=i18n.borderColorHighlight,
                                 default='#dd8800')
    iconColorHighlight = schema.ASCIILine(title=i18n.iconColorHighlight,
                                 default='#000000')
    fcHighlight = schema.ASCIILine(title=i18n.fcHighlight,
                                 default='#dd8800')

    #error
    bgColorError = schema.ASCIILine(title=i18n.bgColorError,
                                 default='#ffddcc')
    bgImgOpacityError = schema.ASCIILine(title=i18n.bgImgOpacityError,
                                 default='45')
    bgTextureError = schema.ASCIILine(title=i18n.bgTextureError,
                                 required=False)
    borderColorError = schema.ASCIILine(title=i18n.borderColorError,
                                 default='#dd0000')
    iconColorError = schema.ASCIILine(title=i18n.iconColorError,
                                 default='#000000')
    fcError = schema.ASCIILine(title=i18n.fcError,
                                 default='#dd0000')

    #modal screen for overlay
    bgColorOverlay = schema.ASCIILine(title=i18n.bgColorOverlay,
                                 default='#aaaaaa')
    bgImgOpacityOverlay = schema.ASCIILine(title=i18n.bgImgOpacityOverlay,
                                 default='75')
    bgTextureOverlay = schema.ASCIILine(title=i18n.bgTextureOverlay,
                                 required=False)
    opacityOverlay = schema.ASCIILine(title=i18n.opacityOverlay,
                                 default='30')

    #drop shadows#999999
    bgColorShadow = schema.ASCIILine(title=i18n.bgColorShadow,
                                 default='#999999')
    bgImgOpacityShadow = schema.ASCIILine(title=i18n.bgImgOpacityShadow,
                                 default='55')
    bgTextureShadow = schema.ASCIILine(title=i18n.bgTextureShadow,
                                 required=False)
    cornerRadiusShadow = schema.ASCIILine(title=i18n.cornerRadiusShadow,
                                 default='5px')
    thicknessShadow = schema.ASCIILine(title=i18n.thicknessShadow,
                                 default='0px')
    opacityShadow = schema.ASCIILine(title=i18n.opacityShadow,
                                 default='45')
    offsetLeftShadow = schema.ASCIILine(title=i18n.offsetLeftShadow,
                                 default='5px')
    offsetTopShadow = schema.ASCIILine(title=i18n.offsetTopShadow,
                                 default='5px')

from plone.autoform.interfaces import WIDGETS_KEY

COLOR_WIDGETS = {}
for i in config.THEME_SETTINGS:
    if 'color' not in i.lower() and not i.startswith('fc'):continue
    COLOR_WIDGETS[i] = 'collective.z3cform.colorpicker.colorpicker.ColorpickerFieldWidget'

IJQueryUIThemeSettings.setTaggedValue(WIDGETS_KEY, COLOR_WIDGETS)

class IDefaultThemeFormSchema(interface.Interface):
    """JQueryUIThem settings"""

    theme = schema.Choice(title=i18n.label_theme,
                          required=True,
                          default='sunburst',
                          vocabulary='collective.jqueryuithememanager.vocabularies.themes')

class IDeleteThemeFormSchema(interface.Interface):
    """Delete theme form"""
    themes = schema.List(title=i18n.label_themes,
                required=True,
                value_type=schema.Choice(title=i18n.label_theme,
                         vocabulary='collective.jqueryuithememanager.vocabularies.persistentthemes')
                         )

