from django import template
from .. import models

register = template.Library()


@register.filter
def show_role(value):
    role = ""
    for i, rolename in models.Role.ROLES:
        if i == value:
            role = " ({})".format(rolename)
    return role
