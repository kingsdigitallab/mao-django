from draftjs_exporter.dom import DOM
from wagtail.admin.rich_text.converters.html_to_contentstate import \
    InlineEntityElementHandler


"""Anchor extension to the rich text editor was written by Thibaud
Colas, available at
https://github.com/thibaudcolas/wagtail_draftail_experiments
"""
def anchor_entity_decorator(props):
    """
    Draft.js ContentState to database HTML.
    Converts the ANCHOR entities into <a> tags.
    """
    return DOM.create_element('a', {
        'data-anchor': True,
        'href': props['fragment'],
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

"""
    An extension of extension developed by King's Digital Lab
    to connect anchors with html blocks through id's
"""
def anchorid_entity_decorator(props):
    return DOM.create_element('span', {
        'id': props['anchorid'],
    }, props['children'])

class AnchorIDEntityElementHandler(InlineEntityElementHandler):
    mutability = 'MUTABLE'

    def get_attribute_data(self, attrs):
        """
        Take the ``anchorid`` value from the ``id`` HTML attribute.
        """
        return {
            'anchorid': attrs['id'],
        }
