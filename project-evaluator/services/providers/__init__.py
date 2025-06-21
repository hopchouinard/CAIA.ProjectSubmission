# AI Providers package
from .base_provider import AIProvider
from .openai_provider import OpenAIProvider

# Import other providers conditionally to allow partial installation
__all__ = ['AIProvider', 'OpenAIProvider']

try:
    from .anthropic_provider import AnthropicProvider
    __all__.append('AnthropicProvider')
except ImportError:
    AnthropicProvider = None

try:
    from .google_provider import GoogleProvider
    __all__.append('GoogleProvider')
except ImportError:
    GoogleProvider = None

try:
    from .azure_provider import AzureProvider
    __all__.append('AzureProvider')
except ImportError:
    AzureProvider = None

try:
    from .databricks_provider import DatabricksProvider
    __all__.append('DatabricksProvider')
except ImportError:
    DatabricksProvider = None
