from bs4 import BeautifulSoup
from plone import api
from plone.base.utils import safe_text
from plone.outputfilters.interfaces import IFilter
from plone.registry.interfaces import IRegistry
from plone.rfc822.interfaces import IPrimaryFieldInfo
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

    def _get_zoom_url(self, item, registry, show_original=False):
        field_name = "image"
        try:
            info = IPrimaryFieldInfo(item, None)
            if info:
                field_name = info.fieldname
        except Exception as e:
            logger.debug("Failed to obtain primary field info: %s", str(e))

        if show_original:
            return f"{item.absolute_url()}/@@images/{field_name}"

        scale_name = registry.get(
            "collective.click_to_zoom.click_to_zoom_control_panel.image_scale",
            "large",
        )

        try:
            request = self.request
            if request is None:
                from zope.globalrequest import getRequest

                request = getRequest()
            images_view = api.content.get_view("images", item, request)
            if images_view:
                scale = images_view.scale(field_name, scale=scale_name)
                if scale:
                    return scale.url
        except Exception as e:
            logger.debug("Failed to obtain scale for click-to-zoom: %s", str(e))

        return item.absolute_url()

    def _get_dimensions_from_value(self, value):
        if not value:
            return None, None
        if hasattr(value, "getImageSize"):
            return value.getImageSize()
        if hasattr(value, "width") and hasattr(value, "height"):
            return value.width, value.height
        return None, None

    def _get_dimensions_from_primary_field(self, item):
        try:
            info = IPrimaryFieldInfo(item, None)
            if info:
                return self._get_dimensions_from_value(info.value)
        except Exception as e:
            logger.debug("Failed to obtain primary field dimensions: %s", str(e))
        return None, None

    def _get_dimensions_from_image_attribute(self, item):
        try:
            field_value = getattr(item, "image", None)
            width, height = self._get_dimensions_from_value(field_value)
            if width:
                return width, height
            if hasattr(field_value, "getWidth"):
                return field_value.getWidth(), field_value.getHeight()
        except Exception as e:
            logger.debug("Failed to obtain 'image' attribute dimensions: %s", str(e))
        return None, None

    def _get_dimensions_from_images_view(self, item):
        try:
            request = self.request
            if request is None:
                from zope.globalrequest import getRequest

                request = getRequest()
            images_view = api.content.get_view("images", item, request)
            if images_view:
                scale = images_view.scale("image")
                if scale:
                    return scale.width, scale.height
        except Exception as e:
            logger.debug("Failed to obtain dimensions via images view: %s", str(e))
        return None, None

    def _get_dimensions(self, item):
        # Try primary field first
        width, height = self._get_dimensions_from_primary_field(item)
        if width:
            return width, height

        # Fallback to 'image' attribute
        width, height = self._get_dimensions_from_image_attribute(item)
        if width:
            return width, height

        # Final fallback: use the 'images' view to get original scale dimensions
        return self._get_dimensions_from_images_view(item)

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

        show_original = registry.get(
            "collective.click_to_zoom.click_to_zoom_control_panel.show_original",
            False,
        )
        zoom_url = self._get_zoom_url(item, registry, show_original=show_original)

        # Create a new <a> tag and wrap the image
        a_tag = soup.new_tag("a", href=zoom_url)
        if not show_original:
            a_tag["class"] = "click-to-zoom"
            a_tag["data-linktype"] = "image-zoom"

            # Get original dimensions
            width, height = self._get_dimensions(item)
            if width:
                a_tag["data-width"] = str(width)
                a_tag["data-height"] = str(height)

        img.wrap(a_tag)
        return True

    def __call__(self, data):
        if not data:
            return data

        if not self.is_enabled():
            return data

        # Make sure data is text
        data = safe_text(data)

        data = re.sub(r"<([^<>\s]+?)\s*/>", self._shorttag_replace, data)
        soup = BeautifulSoup(data, "html.parser")
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
