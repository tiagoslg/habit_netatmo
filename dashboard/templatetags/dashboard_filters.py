import os
from django import template
from django.utils.html import format_html

register = template.Library()


@register.filter
def list_to_str(data_type):
    return ','.join(data_type)


@register.filter
def clear_id(id):
    return id.replace(':', '')


@register.simple_tag(takes_context=True)
def get_log_url(context, type_log):
    url_list = []
    for camera in context.get('camera_id_list', []):
        dest = '/media/{}/{}_{}.log'.format(context['user_id'], type_log, camera.replace(':', ''))
        if os.path.exists('/app{}'.format(dest)):
            url_list.append('<a href="{}" target="_blank">Camera ID: {}</a>'.format(dest, camera))
    return format_html('<br />'.join(url_list))
