from plone.base.interfaces.installable import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "collective.click_to_zoom:uninstall",
        ]

    def getNonInstallableProducts(self):
        """Hide the upgrades package from site-creation and quickinstaller."""
        return [
            "collective.click_to_zoom.upgrades",
        ]
