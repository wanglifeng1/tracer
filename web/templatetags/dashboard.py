from django.template import Library

register = Library()


@register.simple_tag
def use_space(str):
    if str >= 1024 * 1024 * 1024:
        return "%.2f GB" % (str / (1024 * 1024 * 1024))
    elif str >= 1024 * 1024:
        return "%.2f M" % (str / (1024 * 1024))
    elif str >= 1024:
        return "%.2f KB" % (str / 1024)
    else:
        return "%d B" % str
