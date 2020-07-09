from django import template
from django.template.defaultfilters import stringfilter
import os
register = template.Library()


@register.filter
@stringfilter
def append(str1, str2):
    return str(str1) + str(str2)


@register.filter
@stringfilter
def path_join(str1, str2):
    return os.path.join(str1,str2)

