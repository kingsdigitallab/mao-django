from django import forms

from wagtail.core.blocks import (
    CharBlock, FieldBlock, IntegerBlock, RichTextBlock, StreamBlock,
    StructBlock, TextBlock
)
from wagtail.images.blocks import ImageChooserBlock


class AlignmentChoiceBlock(FieldBlock):

    field = forms.ChoiceField(choices=(
        ('left', 'left'), ('right', 'right'),
    ))


class FootnoteBlock(StructBlock):

    number = IntegerBlock(min_value=1)
    footnote = TextBlock()

    class Meta:
        template = 'mao_era/blocks/footnote_block.html'


class ImageBlock(StructBlock):

    image = ImageChooserBlock()
    image_align = AlignmentChoiceBlock()

    class Meta:
        template = 'mao_era/blocks/image_block.html'


class SectionContentBlock(StreamBlock):

    text = RichTextBlock()
    image = ImageBlock()


class SectionBlock(StructBlock):

    heading = CharBlock()
    content = SectionContentBlock()

    class Meta:
        template = 'mao_era/blocks/section_block.html'


class BiographyStreamBlock(StreamBlock):

    section = SectionBlock()

    class Meta:
        template = 'mao_era/blocks/biography_block.html'


class FootnotesStreamBlock(StreamBlock):

    footnote = FootnoteBlock()

    class Meta:
        template = 'mao_era/blocks/footnotes_block.html'
