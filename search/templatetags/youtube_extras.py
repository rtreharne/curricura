from django import template

register = template.Library()

@register.filter
def youtube_seconds(timestamp):
    """Convert HH:MM:SS or MM:SS into total seconds for YouTube links."""
    if not timestamp:
        return 0
    parts = [int(x) for x in timestamp.split(":")]
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h = 0
        m, s = parts
    else:
        h = 0
        m = 0
        s = parts[0]
    return h * 3600 + m * 60 + s
