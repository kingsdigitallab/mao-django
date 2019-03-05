from django import template


register = template.Library()


@register.inclusion_tag('mao_era/includes/source_title.html')
def display_source_title(source):
    return {
        'source_type': source.source_type,
        'title': source.title,
    }
