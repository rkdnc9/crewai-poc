"""Deterministic SVG annotation helpers."""

from pathlib import Path
from typing import List, Dict, Sequence
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def _svg_tag(name: str) -> str:
    return f"{{{SVG_NS}}}{name}"


def _truncate(text: str, limit: int = 90) -> str:
    clean_text = " ".join(str(text).split())
    return clean_text if len(clean_text) <= limit else f"{clean_text[:limit-3]}..."


def _parse_viewbox(root: ET.Element) -> Sequence[float]:
    viewbox_raw = root.get("viewBox")
    if viewbox_raw:
        parts = [p for p in viewbox_raw.replace(",", " ").split() if p]
        if len(parts) == 4:
            try:
                return [float(p) for p in parts]
            except ValueError:
                pass
    width = float(root.get("width", 800))
    height = float(root.get("height", 600))
    return [0.0, 0.0, width, height]


def annotate_svg_with_crew(svg_path: str, violations: List[Dict]) -> str:
    """Add violation text blocks to the base SVG without relying on LLM output."""
    svg_file = Path(svg_path)
    try:
        tree = ET.parse(svg_file)
    except ET.ParseError as exc:
        raise ValueError(f"Cannot parse SVG at {svg_path}: {exc}") from exc
    root = tree.getroot()
    _, _, view_width, view_height = _parse_viewbox(root)

    # Remove any stale annotation group (only direct children are created by us)
    for child in list(root):
        if child.tag == _svg_tag("g") and child.get("id") == "violation-annotations":
            root.remove(child)

    annotation_group = ET.SubElement(root, _svg_tag("g"), {"id": "violation-annotations"})
    base_y = view_height - 40
    line_height = 16

    if violations:
        header = ET.SubElement(
            annotation_group,
            _svg_tag("text"),
            {
                "class": "violation-text",
                "x": "50",
                "y": f"{base_y}",
                "fill": "red"
            }
        )
        header.text = f"Violations Found: {len(violations)}"

        max_lines = 4
        for idx, violation in enumerate(violations[:max_lines]):
            reason = _truncate(violation.get("reason", str(violation)))
            line = ET.SubElement(
                annotation_group,
                _svg_tag("text"),
                {
                    "class": "violation-text",
                    "x": "50",
                    "y": f"{base_y + line_height * (idx + 1)}",
                    "fill": "red"
                }
            )
            line.text = f"{idx + 1}. {reason}"

        if len(violations) > max_lines:
            extra = ET.SubElement(
                annotation_group,
                _svg_tag("text"),
                {
                    "class": "violation-text",
                    "x": "50",
                    "y": f"{base_y + line_height * (max_lines + 1)}",
                    "fill": "red"
                }
            )
            extra.text = f"+{len(violations) - max_lines} more"
    else:
        clean_status = ET.SubElement(
            annotation_group,
            _svg_tag("text"),
            {
                "class": "violation-text",
                "x": f"{view_width / 2:.1f}",
                "y": f"{base_y}",
                "text-anchor": "middle",
                "fill": "green"
            }
        )
        clean_status.text = "✅ No violations found"

    tree.write(svg_file, encoding="unicode", xml_declaration=True)
    return str(svg_file)
