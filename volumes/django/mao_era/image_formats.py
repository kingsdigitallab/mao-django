from wagtail.images.formats import Format, register_image_format

register_image_format(Format(
    'mao_original', 'Mao Full Scale', 'richtext-image full-width-original',
    'original'))
