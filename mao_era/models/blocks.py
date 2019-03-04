from django import forms

from wagtail.core.blocks import (
    FieldBlock, RichTextBlock, StreamBlock, StructBlock
)
from wagtail.images.blocks import ImageChooserBlock


class AlignmentChoiceBlock(FieldBlock):

    field = forms.ChoiceField(choices=(
        ('left', 'left'), ('right', 'right'),
    ))


class TextImageBlock(StructBlock):

    image = ImageChooserBlock()
    image_align = AlignmentChoiceBlock()
    text = RichTextBlock()

    class Meta:
        template = 'mao_era/blocks/text_image_block.html'


class BiographyStreamBlock(StreamBlock):

    text = RichTextBlock()
    text_with_image = TextImageBlock()
