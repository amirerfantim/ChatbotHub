from django import template
from markdown import markdown

register = template.Library()


@register.filter(name='markdown')
def render_markdown(value):
    return markdown(value, extensions=['markdown.extensions.fenced_code'])
