"""
Custom template tags for i18n functionality.
Provides tags to mark content as non-translatable (e.g., Japanese technical terms).
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def notrans(text):
    """
    Mark text as non-translatable (for Japanese technical terms like kata names).
    Wraps text in a span with 'notranslate' class.

    Usage in templates:
        {% load i18n_extras %}
        {% notrans kata.name %}
    """
    if text is None:
        return ''
    return mark_safe(f'<span class="notranslate">{text}</span>')


@register.filter
def notrans_filter(text):
    """
    Filter version of notrans for use in {{ variable|notrans_filter }}

    Usage in templates:
        {% load i18n_extras %}
        {{ kata.name|notrans_filter }}
    """
    if text is None:
        return ''
    return mark_safe(f'<span class="notranslate">{text}</span>')
