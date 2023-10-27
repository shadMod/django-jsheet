from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def display_bottom_sheet(sheets: str, url_name: str, style_cl: str = None, style_id: str = None):
    if style_cl is None:
        style_cl = ""
    if style_id is None:
        style_id = ""

    sheets = sorted(sheets.split(","))

    html = []
    for name in sheets:
        _button = f"""
<input type='button' onclick='location.href="/{url_name}/{name}/";'
value='{name}' class='{style_cl}' id='{style_id}' />
        """
        html.append(_button)

    nr_sheet = int(name.replace("data_", "")) + 1
    html.append(
        f"""
<input type='button' onclick='location.href="/{url_name}/data_{nr_sheet}/";'
value='+' class='{style_cl}' id='{style_id}' />
    """
    )
    return mark_safe("".join(html))


@register.simple_tag
def display_jsheet(folder: str = None, filename: str = None, domain: str = None):
    if not folder:
        folder = "data"
    if not filename:
        filename = "data_1"
    if not domain:
        domain = ""

    data_links = f"""
<script src="{domain}/media/jsheet/js/{folder}/{filename}.js"></script>
<script src="{domain}/media/jsheet/js/header.js"></script>
<script src="{domain}/media/jsheet/js/fetch_post.js"></script>
    """
    return mark_safe(data_links.strip())
