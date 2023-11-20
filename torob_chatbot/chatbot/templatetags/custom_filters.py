# custom_filters.py
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='highlight', is_safe=True, needs_autoescape=True)
@stringfilter
def highlight(value, search_term, autoescape=True):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    highlighted = esc(value).replace(
        esc(search_term),
        '<span class="highlighted">{}</span>'.format(esc(search_term)),
    )
    return mark_safe(highlighted)
