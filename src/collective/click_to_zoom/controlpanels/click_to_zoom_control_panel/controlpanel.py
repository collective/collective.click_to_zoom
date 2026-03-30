# -*- coding: utf-8 -*-
from collective.click_to_zoom import _
from collective.click_to_zoom.interfaces import IBrowserLayer
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.z3cform import layout
from zope.component import adapter
from zope.interface import Interface
from zope import schema

class IClickToZoomControlPanel(Interface):
    myfield_name = schema.TextLine(
        title=_(
            "This is an example field for this control panel",
        ),
        description=_(
            "",
        ),
        default="",
        required=False,
        readonly=False,
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
