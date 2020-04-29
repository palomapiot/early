from django import template

register = template.Library()

@register.filter
def reason(value, arg):
    """Filters the given list of reasons by arg type"""
    print(value)
    return list(filter(lambda reason: reason['profile_data_type'] == arg, value))
