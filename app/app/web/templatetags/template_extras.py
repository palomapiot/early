from django import template

register = template.Library()

@register.filter
def reason(value, arg):
    """Filters the given list of reasons by arg type"""
    return list(filter(lambda reason: reason['profile_data_type'] == arg, value))

@register.filter(name='has_group') 
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()