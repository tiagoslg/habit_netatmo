from django import template

register = template.Library()


@register.filter
def list_to_str(data_type):
    return ','.join(data_type)

@register.filter
def clear_id(id):
    return id.replace(':', '')
