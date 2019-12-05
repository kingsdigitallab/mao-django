from django import template
import datetime
from django.utils.dateformat import format

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
def formatDate(value):
    try:
        date = datetime.datetime.strptime(value, "%Y-%m-%d").date()
        date = format(date, "M d, Y")
    except:
        try:
            date = datetime.datetime.strptime(value, "%Y-%m").date()
            date = format(date, "M, Y")
        except:
            try:
                date = datetime.datetime.strptime(value, "%Y").date()
                date = format(date, "Y")
            except:
                date = value
    return date