from django import template

register = template.Library()


@register.simple_tag
def hics_version():
    return "0.1.0"
