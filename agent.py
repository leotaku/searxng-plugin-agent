from typing import Any
from flask import Request
from searx.search import SearchWithPlugins as Search

name = "Agent"
description = "Add an LLM agent to your SearXNG search"
default_on = False

preference_section = "general"
plugin_id = "agent"


def pre_search(request: Request, search: Search) -> bool:
    """Runs BEFORE the search request."""
    return True


def post_search(request: Request, search: Search) -> None:
    """Runs AFTER the search request."""
    pass


def on_result(request: Request, search: Search, result: Any) -> bool:
    """Runs for each result of each engine."""
    return True
