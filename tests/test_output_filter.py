from collective.click_to_zoom.outputfilters.click_to_zoom import ClickToZoomFilter
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobImage
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import pytest


@pytest.mark.usefixtures("integration")
class TestOutputFilter:
    def test_filter_show_original_false(self, portal):
        setRoles(portal, TEST_USER_ID, ["Manager"])

        # Create an image with some data
        image_data = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        image = api.content.create(
            container=portal,
            type="Image",
            id="test-image",
            title="Test Image",
            image=NamedBlobImage(data=image_data, filename="test.gif"),
        )
        uid = image.UID()

        # Mock the filter
        request = portal.REQUEST
        filter_ = ClickToZoomFilter(context=portal, request=request)

        # Registry settings (default: show_original=False, image_scale=large)
        html = f'<img src="something" data-val="{uid}" data-linktype="image" />'
        result = filter_(html)

        # It should be a scale URL (contains a hash or a size)
        assert "/@@images/image" in result
        assert 'class="click-to-zoom"' in result

    def test_filter_show_original_true(self, portal):
        setRoles(portal, TEST_USER_ID, ["Manager"])

        # Set registry value
        registry = getUtility(IRegistry)
        registry[
            "collective.click_to_zoom.click_to_zoom_control_panel.show_original"
        ] = True

        # Create an image
        image_data = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        image = api.content.create(
            container=portal,
            type="Image",
            id="test-image-original",
            title="Test Image Original",
            image=NamedBlobImage(data=image_data, filename="test.gif"),
        )
        uid = image.UID()

        # Mock the filter
        request = portal.REQUEST
        filter_ = ClickToZoomFilter(context=portal, request=request)

        html = f'<img src="something" data-val="{uid}" data-linktype="image" />'
        result = filter_(html)

        assert 'href="http://nohost/plone/test-image-original/@@images/image"' in result
        assert 'class="click-to-zoom"' in result
