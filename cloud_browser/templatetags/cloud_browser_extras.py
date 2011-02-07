"""Cloud browser template tags."""
import os

from django import template
from django.template import TemplateSyntaxError, Node
from django.template.defaultfilters import stringfilter

from cloud_browser.app_settings import settings

register = template.Library()  # pylint: disable=C0103


@register.filter
@stringfilter
def truncatechars(value, num, end_text="..."):
    """Truncate string on character boundary.

    .. note::
        Django ticket `5025 <http://code.djangoproject.com/ticket/5025>`_ has a
        patch for a more extensible and robust truncate characters tag filter.

    Example::

        {{ my_variable|truncatechars:22 }}

    :param value: Value to truncate.
    :type  value: ``string``
    :param num: Number of characters to trim to.
    :type  num: ``int``
    """
    length = None
    try:
        length = int(num)
    except ValueError:
        pass

    if length is not None and len(value) > length:
        return value[:length-len(end_text)] + end_text

    return value
truncatechars.is_safe = True  # pylint: disable=W0612


@register.tag
def cloud_browser_media_link(_, token):
    """Create appropriate ``link``, ``script`` or ``style`` tag for JavaScript
    and CSS files from relative resource path.

    .. note::
        Presently only works for JavaScript and CSS because those *can* be
        dumped inline into an HTML page. Unfortunately, images cannot, and we
        haven't decided how to handle that yet (maybe ignore if not statically
        served?)

    Correctly handles whether or not the settings variable
    ``CLOUD_BROWSER_STATIC_MEDIA_DIR`` is set and served.

    For example, if we use the tag in a template::

        {% cloud_browser_media_link "js/browser.js" %}

    And the static media directory variable is set and media is served, then
    a ``<script>`` tag **with** a ``link`` is emitted, pointing to the URL.
    However, if the directory variable is not set, a ``<script>`` tag with
    the full inline JavaScript text is emitted instead.

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

    #: The static served media URL (or ``None``)
    static_media_url = settings.app_media_url

    #: The fallback template path of the same media.
    template_media_path = 'cloud_browser_media'

    def __init__(self, rel_path):
        """Initializer."""
        super(MediaLinkNode, self).__init__()
        self.rel_path = rel_path.lstrip('/').strip("'").strip('"')
        self.media_type = os.path.splitext(self.rel_path)[1].strip('.').lower()

    def render(self, context):
        """Render."""
        from django.template.loader_tags import IncludeNode

        # Check if we have static-served media
        if self.static_media_url:
            # Use a link.
            static_path = os.path.join(self.static_media_url, self.rel_path)
            return self.mappings[self.media_type][0] % static_path

        else:
            # Have to render page with full media included.
            template_path = os.path.join(self.template_media_path,
                                         self.rel_path)
            template_path = '"' + template_path.strip('"') + '"'
            rendered = IncludeNode(template_path).render(context)
            return self.mappings[self.media_type][1] % rendered
