"""Context processors."""

from cloud_browser.app_settings import settings as _settings


def settings(_):
    """Expose certain settings as context."""
    return {
        'CLOUD_BROWSER_MEDIA_URL': _settings.app_media_url,
    }
