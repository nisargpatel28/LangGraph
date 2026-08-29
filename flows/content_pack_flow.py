"""Create a reusable content pack from the existing agentic image flow."""
import json
import os
import uuid
from typing import Any, Callable, Dict, Optional

import openai

from models.content_pack import ContentPack
from storage.artifact_store import ArtifactStore
from flows.agentic_image_flow import make_flow