from django.template import Library

register = Library()


@register.filter(name="addcls")
def addcls(field, css):
    if hasattr(field, "as_widget"):
        return field.as_widget(attrs={"class": css})
    return None
