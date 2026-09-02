"""Generate multiple content packs from a list of prompts."""
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional


PackRunner = Callable[..., Dict[str, Any]]
