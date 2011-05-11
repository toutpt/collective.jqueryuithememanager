from zope.i18nmessageid import MessageFactory

messageFactory = MessageFactory("collective.jqueryuithememanager")
_ = messageFactory

label_version = _(u"label_version", default=u"JQuery UI Version")
desc_version = _(u"desc_version", default=u"Specify the version of jqueryui used")

label_cdn = _(u"label_cdn", default=u"CDN to use")
desc_cdn = _(u"desc_cdn", default=u"Default is http://ajax.googleapis.com/ajax/libs/jqueryui/%s/themes/%s/jquery-ui.css")

label_theme = _(u"label_theme", default=u"Theme")
maincontrolpanel_label = _(u"JQuery UI theme settings")
customcontrolpanel_label = _(u"JQuery UI custom theme settings")
msg_customtheme_changes_saved = _(u"Your custom theme has been install. You can now select it.")
msg_importtheme_changes_saved = _(u"Theme imported. You may want to select this theme.")
err_importtheme_typeerror = _(u"You must upload a zip")
err_importtheme_valueerror = _(u"You must upload a valid JQueryUI theme file")

label_importtheme_form = _(u"Import JQueryUI Theme")

label_theme_archive= _(u"Theme archive")
desc_theme_archive= _(u"The archive mut provide the structure provided by http://jqueryui.com/themeroller archive.")

themename           = _(u"themename", default=u"Theme name (ascii)")

fwDefault           = _(u"fwDefault", default=u"Familly")
ffDefault           = _(u"ffDefault", default=u"Weight")
fsDefault           = _(u"fsDefault", default=u"Size")
cornerRadius        = _(u"cornerRadius", default=u"Corner Radius")

bgColorHeader       = _(u"bgColorHeader", default=u"Header: Background color")
bgImgOpacityHeader  = _(u"bgImgOpacityHeader", default=u"Header: Background opacity")
bgTextureHeader     = _(u"bgTextureHeader", default=u"Header: Background texture")
borderColorHeader   = _(u"borderColorHeader", default=u"Header: Border color")
iconColorHeader     = _(u"iconColorHeader", default=u"Header: Icon color")
fcHeader            = _(u"fcHeader", default=u"Header: Text color")

bgColorContent      = _(u"bgColorContent", default=u"Content: Background color")
bgImgOpacityContent = _(u"bgImgOpacityContent", default=u"Content: Background opacity")
bgTextureContent    = _(u"bgTextureContent", default=u"Content: Background texture")
borderColorContent  = _(u"borderColorContent", default=u"Content: Border color")
iconColorContent    = _(u"iconColorContent", default=u"Content: Icon color")
fcContent           = _(u"fcContent", default=u"Content: Text color")

bgColorShadow       = _(u"bgColorShadow", default=u"Drop shadows: Background color")
bgTextureShadow     = _(u"bgTextureShadow", default=u"Drop shadows: Background Texture")
bgImgOpacityShadow  = _(u"bgImgOpacityShadow", default=u"Drop shadows: Background opacity")
cornerRadiusShadow  = _(u"cornerRadiusShadow", default=u"Drop shadows: Corners")
opacityShadow       = _(u"opacityShadow", default=u"Drop shadows: Shadow opacity")
offsetLeftShadow    = _(u"offsetLeftShadow", default=u"Drop shadows: Left offset")
offsetTopShadow     = _(u"offsetTopShadow", default=u"Drop shadows: Top offset")
thicknessShadow     = _(u"thicknessShadow", default=u"Drop shadows: Shadow tickness")

bgColorDefault      = _(u"bgColorDefault", default=u"Clickable default state: Background color")
bgImgOpacityDefault = _(u"bgImgOpacityDefault", default=u"Clickable default state: Background opacity")
bgTextureDefault    = _(u"bgTextureDefault", default=u"Clickable default state: Background texture")
borderColorDefault  = _(u"borderColorDefault", default=u"Clickable default state: Border color")
iconColorDefault    = _(u"iconColorDefault", default=u"Clickable default state: Icon color")
fcDefault           = _(u"fcDefault", default=u"Clickable default state: Text color")

bgColorHover        = _(u"bgColorHover", default=u"Clickable hover state: Background color")
bgImgOpacityHover   = _(u"bgImgOpacityHover", default=u"Clickable hover state: Background opacity")
bgTextureHover      = _(u"bgTextureHover", default=u"Clickable hover state: Background texture")
borderColorHover    = _(u"borderColorHover", default=u"Clickable hover state: Border color")
iconColorHover      = _(u"iconColorHover", default=u"Clickable hover state: Icon color")
fcHover             = _(u"fcHover", default=u"Clickable hover state: Text color")

bgColorError        = _(u"bgColorError", default=u"Error: Background color")
bgImgOpacityError   = _(u"bgImgOpacityError", default=u"Error: Background opacity")
bgTextureError      = _(u"bgTextureError", default=u"Error: Background texture")
borderColorError    = _(u"borderColorError", default=u"Error: Border color")
iconColorError      = _(u"iconColorError", default=u"Error: Icon color")
fcError             = _(u"fcError", default=u"Error: Text color")

bgColorActive       = _(u"bgColorActive", default=u"Clickable active state: Background color")
bgImgOpacityActive  = _(u"bgImgOpacityActive", default=u"Clickable active state: Background opacity")
bgTextureActive     = _(u"bgTextureActive", default=u"Clickable active state: Background texture")
borderColorActive   = _(u"borderColorActive", default=u"Clickable active state: Border color")
iconColorActive     = _(u"iconColorActive", default=u"Clickable active state: Icon color")
fcActive            = _(u"fcActive", default=u"Clickable active state: Text color")

bgColorHighlight    = _(u"bgColorHighlight", default=u"Highlight: Background color")
bgImgOpacityHighlight   = _(u"bgImgOpacityHighlight", default=u"Highlight: Background opacity")
bgTextureHighlight  = _(u"bgTextureHighlight", default=u"Highlight: Background texture")
borderColorHighlight    = _(u"borderColorHighlight", default=u"Highlight: Border color")
iconColorHighlight  = _(u"iconColorHighlight", default=u"Highlight: Icon color")
fcHighlight         = _(u"fcHighlight", default=u"Highlight: Text color")

bgColorOverlay      = _(u"bgColorOverlay", default=u"Modal screen for overlay: Background color")
bgImgOpacityOverlay = _(u"bgImgOpacityOverlay", default=u"Modal screen for overlay: Background opacity")
bgTextureOverlay    = _(u"bgTextureOverlay", default=u"Modal screen for overlay: Background texture")
opacityOverlay      = _(u"opacityOverlay", default=u"Modal screen for overlay: Opacity")
