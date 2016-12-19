from django import template

register = template.Library()


@register.filter(name='minus')
def minus(value, arg):
    """Subtracts the values"""
    return value-arg


@register.filter(name='plus')
def plus(value, arg):
    """Subtracts the values"""
    return value+arg


@register.filter(name='get')
def get(d, k):
    return d.get(k, None)


@register.filter(name='getArray')
def getArray(value, arg):
    if arg:
        return range(arg)
    else:
        return range(0)
