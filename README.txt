Introduction
============

This add-on let you manage the jqueryui theme used in Plone.

Features:

  * Import a theme from a zip file built on http://jqueryui.com/themeroller
  * Import multiple themes from a zip file
  * Create or modify themes within the control panel
  * Load all default jqueryui themes in one click in the control panel
  * Delete selected themes
  * Update themes
  * External add-on can embed themes within a zope browser resource directory
  * Select a theme

Dependencies
============

This add-on use:

  * collective.js.jqueryui
  * collective.z3cform.colorpicker
  * plone.app.registry
  * plone.resource
  * plone.namedfile

File system versus data base
============================

If a theme is imported, updated, or created within the control panel it is 
stored in the data base (in the portal_resources).

By default collective.js.jqueryui provide sunburst theme. This one is considered
the default one.

You can provide a theme in your add-on by simply embed it in a zope browser
resource directory as usual. You just need to register a named utility providing
IThemesProvider interface. A default base class is shipped in, so you will
just have to inherits from it and just change RESOURCE_NAME and THEME_IDS class
variables.

If a theme exist on the filesystem and in the database, the database has precedence.

