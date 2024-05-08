from django import template
import datetime


register = template.Library()


@register.inclusion_tag('mao_era/includes/source_title.html')
def display_source_title(source):
    return {
        'source_type': source.source_type,
        'title': source.title,
    }


@register.simple_tag(takes_context=True)
def get_site_root(context):
    return context['request'].site.root_page


@register.simple_tag
def get_menu_pages(parent):
    return parent.get_children().live().in_menu()


@register.filter
def format_date(value):
    """Returns a suitably formatted date string from the input string.

    The input string should be of the form [-]YYYY[-MM[-DD]].

    """
    date_formats = (
        ('%Y-%m-%d', '%b %d, %Y'),
        ('%Y-%m', '%b, %Y'),
        ('%Y', '%Y'),
    )
    str_date = value
    for input_format, output_format in date_formats:
        try:
            date = datetime.datetime.strptime(value, input_format).date()
            str_date = date.strftime(output_format)
        except ValueError:
            continue
    return str_date
