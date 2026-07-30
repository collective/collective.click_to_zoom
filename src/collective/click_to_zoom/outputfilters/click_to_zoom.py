from bs4 import BeautifulSoup
from plone import api
from plone.base.utils import safe_text
from plone.outputfilters.interfaces import IFilter
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import implementer

import logging
import re
import typing


logger = logging.getLogger(__name__)


@implementer(IFilter)
class ClickToZoomFilter:
    singleton_tags: typing.ClassVar[set[str]] = {
        "area",
        "base",
        "basefont",
        "br",
        "col",
        "command",
        "embed",
        "frame",
        "hr",
        "img",
        "input",
        "isindex",
        "keygen",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self, context=None, request=None):
        self.current_status = None
        self.context = context
        self.request = request

    # IFilter implementation
    order = 500

    def _shorttag_replace(self, match):
        tag = match.group(1)
        if tag in self.singleton_tags:
            return "<" + tag + " />"

        return "<" + tag + "></" + tag + ">"

    def is_enabled(self):
        registry = getUtility(IRegistry)
        return registry.get(
            "collective.click_to_zoom.click_to_zoom_control_panel.enabled",
            True,
        )

    def _process_image(self, img, soup, registry):
        # If the image is already inside a link, we don't do anything
        if img.parent and img.parent.name == "a":
            return False

        if img.attrs.get("data-linktype") != "image":
            return False

        uid = img.attrs.get("data-val")
        if not uid:
            return False

        item = api.content.get(UID=uid)
        if item is None:
            return False

        zoom_url = None

        # Check if we should use the original image
        show_original = registry.get(
            "collective.click_to_zoom.click_to_zoom_control_panel.show_original",
            False,
        )

        if show_original:
            zoom_url = f"{item.absolute_url()}/@@images/image"
        else:
            # Get the selected image scale from the control panel registry
            scale_name = registry.get(
                "collective.click_to_zoom.click_to_zoom_control_panel.image_scale",
                "large",
            )

            # Get the cacheable URL for the chosen scale
            try:
                images_view = api.content.get_view("images", item, self.request)
                if images_view:
                    # The most common field name for an image is 'image'
                    scale = images_view.scale("image", scale=scale_name)
                    if scale:
                        zoom_url = scale.url
            except Exception as e:
                logger.debug("Failed to obtain scale for click-to-zoom: %s", str(e))

        # If no scale is obtained, use the original image URL as fallback
        if not zoom_url:
            zoom_url = item.absolute_url()

        # Create a new <a> tag and wrap the image
        a_tag = soup.new_tag("a", href=zoom_url)
        a_tag["class"] = "click-to-zoom"
        a_tag["data-linktype"] = "image-zoom"

        img.wrap(a_tag)
        return True

    def __call__(self, data):
        if not data:
            return data

        if not self.is_enabled():
            return data

        data = re.sub(r"<([^<>\s]+?)\s*/>", self._shorttag_replace, data)
        soup = BeautifulSoup(safe_text(data), "html.parser")
        has_changes = False
        registry = getUtility(IRegistry)

        for img in soup.find_all("img"):
            changed = self._process_image(img, soup, registry)
            if changed:
                has_changes = True

        # Only return new object if changes were made to save parse time
        if has_changes:
            return str(soup)

        return data
