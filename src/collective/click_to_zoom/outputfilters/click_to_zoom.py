from plone.outputfilters.interfaces import IFilter
from zope.interface import implementer
from plone.base.utils import safe_text
import re
from bs4 import BeautifulSoup
from plone import api


@implementer(IFilter)
class ClickToZoomFilter:
    singleton_tags = {
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

    def __call__(self, data):
        if not data:
            return data

        data = re.sub(r"<([^<>\s]+?)\s*/>", self._shorttag_replace, data)
        soup = BeautifulSoup(safe_text(data), "html.parser")
        has_changes = False

        for img in soup.find_all("img"):
            # If the image is already inside a link, we don't do anything
            if img.parent and img.parent.name == "a":
                continue

            if img.attrs.get("data-linktype") == "image":
                uid = img.attrs.get("data-val")
                if not uid:
                    continue

                item = api.content.get(UID=uid)
                if item is not None:
                    zoom_url = None

                    # Get the cacheable URL for the 'large' (or 'great') scale
                    try:
                        images_view = api.content.get_view("images", item, self.request)
                        if images_view:
                            # The most common field name for an image is 'image'
                            scale = images_view.scale("image", scale="large")
                            if scale:
                                zoom_url = scale.url
                    except Exception:
                        # If something goes wrong (e.g. no 'image' field), do not fail
                        pass

                    # If no scale is obtained, use the original image URL as fallback
                    if not zoom_url:
                        zoom_url = item.absolute_url()

                    # Create a new <a> tag and wrap the image
                    a_tag = soup.new_tag("a", href=zoom_url)
                    a_tag["class"] = "click-to-zoom"
                    a_tag["data-linktype"] = "image-zoom"

                    img.wrap(a_tag)
                    has_changes = True

        # Only return the new object if there were changes, else return the original 'data'
        if has_changes:
            return str(soup)

        return data
