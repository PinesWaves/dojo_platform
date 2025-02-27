# custom_filters.py
from django import template

register = template.Library()

@register.filter
def widget_type(field):
    w_type = "custom" if "Custom" in field.field.widget.__class__.__name__ else "default"
    return w_type
