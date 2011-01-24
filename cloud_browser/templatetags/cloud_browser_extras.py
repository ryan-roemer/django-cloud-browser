"""Cloud browser template tags."""

import os

from django import template
from django.template import TemplateSyntaxError, Node
from django.template.loader_tags import IncludeNode

from cloud_browser.app_settings import settings

register = template.Library()

@register.tag
def cloud_browser_media_link(parser, token):
    """Create appropriate ``link``, ``script`` or ``style`` tag from relative
    resource path.

    Correctly handles whether or not the settings variable
    ``CLOUD_BROWSER_STATIC_MEDIA_DIR`` is set and served.

    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("'%s' takes one argument" % bits[0])
    rel_path = bits[1]

    return MediaLinkNode(rel_path)


class MediaLinkNode(Node):
    """Media link node."""
    mappings = {
        'css': [
            "<link rel=\"stylesheet\" type=\"text/css\" href=\"%s\" />",
            "<style type=\"text/css\">%s</style>",
        ],
        'js': [
            "<script type=\"text/javascript\" src=\"%s\"></script>",
            "<script type=\"text/javascript\">%s</script>",
        ],
    }

    def __init__(self, rel_path):
        """Initializer."""
        self.rel_path = rel_path.lstrip('/').strip("'").strip('"')
        self.media_type = os.path.splitext(self.rel_path)[1].strip('.').lower()

    def render(self, context):
        """Render."""
        # Check if we have static-served media
        if settings.app_media_url:
            # Use a link.
            path = os.path.join(settings.app_media_url, self.rel_path)
            return self.mappings[self.media_type][0] % path

        else:
            # Have to render page with full media included.
            template_path = os.path.join('cloud_browser_media', self.rel_path)
            template_path = '"' + template_path.strip('"') + '"'
            rendered = IncludeNode(template_path).render(context)
            return self.mappings[self.media_type][1] % rendered
