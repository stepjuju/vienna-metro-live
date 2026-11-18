
import json
from collections import defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SVG_FILE = ROOT / "public" / "maps" / "vienna-ubahn-original.svg"
OUTPUT_FILE = ROOT / "src" / "data" / "metroPaths.json"

COLORS = {
    "#ce2b31": "U1",
    "#945d9e": "U2",
    "#d47800": "U3",
    "#209640": "U4",
    "#91642f": "U6",
}

tree = ET.parse(SVG_FILE)
root = tree.getroot()

candidates = defaultdict(list)


def inspect(element, inherited_transforms=()):
    transforms = inherited_transforms

    if "transform" in element.attrib:
        transforms += (element.attrib["transform"],)

    tag = element.tag.split("}")[-1]
    stroke = element.attrib.get("stroke", "").lower()

    if tag == "path" and stroke in COLORS:
        line = COLORS[stroke]
        path_data = element.attrib.get("d", "")

        candidates[line].append({
            "color": stroke,
            "d": path_data,
            "strokeWidth": element.attrib.get("stroke-width"),
            "transforms": list(transforms),
        })

    for child in element:
        inspect(child, transforms)


inspect(root)

routes = {}

for line in ["U1", "U2", "U3", "U4", "U6"]:
    line_candidates = candidates[line]

    if not line_candidates:
        print(f"WARNING: No paths found for {line}")
        continue

    # Print every candidate, so we can detect decorative paths.
    print(f"\n{line}: found {len(line_candidates)} matching paths")

    for index, candidate in enumerate(line_candidates):
        print(
            f"  Candidate {index + 1}: "
            f"{len(candidate['d'])} characters"
        )

    # Temporary heuristic: the main route is likely the
    # candidate with the longest path-data string.
    main_route = max(
        line_candidates,
        key=lambda item: len(item["d"]),
    )

    routes[line] = main_route

    print(
        f"  Selected: {len(main_route['d'])} characters"
    )

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE.write_text(
    json.dumps(routes, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print(f"\nExtracted {len(routes)} routes")
print(f"Saved to: {OUTPUT_FILE}")