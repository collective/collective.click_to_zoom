from collective.click_to_zoom import _
from collective.click_to_zoom.interfaces import IBrowserLayer
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.z3cform import layout
from zope import schema
from zope.component import adapter
from zope.interface import Interface


class IClickToZoomControlPanel(Interface):
    enabled = schema.Bool(
        title=_("Enable Click to Zoom"),
        description=_("Check this to enable the click-to-zoom effect on images."),
        default=True,
        required=False,
    )

    image_scale = schema.Choice(
        title=_("Image scale"),
        description=_("Select the image scale that will be loaded when zooming."),
        vocabulary="plone.app.vocabularies.ImagesScales",
        default="large",
        required=True,
    )

    show_original = schema.Bool(
        title=_("Show original image"),
        description=_(
            "If enabled, the zoom effect will show the original "
            "image instead of the selected scale."
        ),
        default=False,
        required=False,
    )


class ClickToZoomControlPanel(RegistryEditForm):
    schema = IClickToZoomControlPanel
    schema_prefix = "collective.click_to_zoom.click_to_zoom_control_panel"
    label = _("Click To Zoom Control Panel")


ClickToZoomControlPanelView = layout.wrap_form(
    ClickToZoomControlPanel, ControlPanelFormWrapper
)


@adapter(Interface, IBrowserLayer)
class ClickToZoomControlPanelConfigletPanel(RegistryConfigletPanel):
    """Control Panel endpoint"""

    schema = IClickToZoomControlPanel
    configlet_id = "click_to_zoom_control_panel-controlpanel"
    configlet_category_id = "Products"
    title = _("Click To Zoom Control Panel")
    group = ""
    schema_prefix = "collective.click_to_zoom.click_to_zoom_control_panel"
