"""Helpers for converting Pydantic JSON schemas into OpenAI's strict
structured-output format (all $ref inlined, additionalProperties=false,
every key marked required, no bare 'default').
"""

from typing import Any


def _inline_refs(node: Any, defs: dict[str, Any]) -> Any:
    if isinstance(node, dict):
        if "$ref" in node:
            ref_name = node["$ref"].split("/")[-1]
            resolved = defs.get(ref_name, {})
            return _inline_refs(resolved, defs)
        return {key: _inline_refs(value, defs) for key, value in node.items()}
    if isinstance(node, list):
        return [_inline_refs(item, defs) for item in node]
    return node


def _strictify(node: Any) -> Any:
    if isinstance(node, dict):
        node.pop("default", None)
        node.pop("title", None)
        if node.get("type") == "object" or "properties" in node:
            node["additionalProperties"] = False
            props = node.get("properties", {})
            node["required"] = list(props.keys())
            for value in props.values():
                _strictify(value)
        if "items" in node:
            _strictify(node["items"])
        for key in ("anyOf", "oneOf", "allOf"):
            if key in node:
                for sub in node[key]:
                    _strictify(sub)
        return node
    return node


def to_openai_strict_schema(model_cls: type) -> dict[str, Any]:
    """Convert a Pydantic model class into an OpenAI strict `json_schema` dict."""
    raw = model_cls.model_json_schema()
    defs = raw.pop("$defs", {})
    resolved = _inline_refs(raw, defs)
    return _strictify(resolved)
