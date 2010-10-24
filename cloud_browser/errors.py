"""Cloud errors."""

class CloudBrowserException(Exception):
  """Base class for all exceptions."""
  pass

class ConfigurationError(CloudBrowserException):
  """Configuration error."""
  pass
