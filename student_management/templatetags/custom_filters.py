from django import template

register = template.Library()

@register.filter(name='replace')
def replace(value, args):
    """
    Replace filter for Django templates
    Usage: {{ value|replace:"old,new" }} or {{ value|replace:"old new" }}
    """
    if not value:
        return value

    if ',' in args:
        old, new = args.split(',', 1)
    else:
        parts = args.split(' ', 1)
        if len(parts) == 2:
            old, new = parts
        else:
            return value

    return value.replace(old, new)


@register.filter(name='format_employment')
def format_employment(value):
    """
    Format employment status: full_time -> Full Time
    Usage: {{ employment_status|format_employment }}
    """
    if not value:
        return value
    return value.replace('_', ' ').title()
