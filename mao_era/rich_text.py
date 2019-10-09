"""Anchor extension to the rich text editor was written by Thibaud
Colas, available at
https://github.com/thibaudcolas/wagtail_draftail_experiments

"""

from draftjs_exporter.dom import DOM
from wagtail.admin.rich_text.converters.html_to_contentstate import \
    InlineEntityElementHandler


def anchor_entity_decorator(props):
    """
    Draft.js ContentState to database HTML.
    Converts the ANCHOR entities into <a> tags.
    """
    return DOM.create_element('a', {
        'data-anchor': True,
        'href': props['fragment'],
    }, props['children'])


def anchorid_entity_decorator(props):
    """
    Draft.js ContentState to database HTML.
    Converts the ANCHORID entities into <span> tags.
    """
    return DOM.create_element('span', {
        'data-anchorid': True,
        'id': props['anchorid'],
    }, props['children'])


class AnchorEntityElementHandler(InlineEntityElementHandler):
    """
    Database HTML to Draft.js ContentState.
    Converts the <a> tags into ANCHOR entities, with the right data.
    """
    # In Draft.js entity terms, anchors are "mutable".
    # We can alter the anchor's text, but it's still an anchor.
    mutability = 'MUTABLE'

    def get_attribute_data(self, attrs):
        """
        Take the ``fragment`` value from the ``href`` HTML attribute.
        """
        return {
            'fragment': attrs['href'],
        }


class AnchorIDEntityElementHandler(InlineEntityElementHandler):
    """
    Database HTML to Draft.js ContentState.
    Converts the a tag into a ANCHORID entity, with the right data.
    """
    mutability = 'IMMUTABLE'

    def get_attribute_data(self, attrs):
        """
        Take the ``anchor_id`` value from the ``id`` HTML attribute.
        """
        return {
            'anchorid': attrs['id'],
        }
