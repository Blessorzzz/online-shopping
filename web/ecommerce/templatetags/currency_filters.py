from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """乘法过滤器：用于价格 * 汇率"""
    try:
        return round(float(value) * float(arg), 2)
    except (ValueError, TypeError):
        return value
