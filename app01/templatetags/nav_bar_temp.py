from django import template

register = template.Library()

@register.inclusion_tag('navibar.html')
def navi_bar(title,request):
    """

    :param title: This is title/slogan of personal blog site
    :param request: this is used for check if user is logged in or not to display different tags on nav-bar,
    if login in will show more,if not will show signup and sign in.
    :return: return all parameters where to render a nav-bar, where use this inclusion tag
    """
    return locals()