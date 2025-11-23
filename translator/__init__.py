"""
Translators for different agent frameworks.
"""

from ._langgraph import LangGraphTranslator


translators = {
    "langgraph": LangGraphTranslator
}
