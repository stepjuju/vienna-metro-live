"""Create the clean display version of the January 2026 Vienna U-Bahn SVG.

Input:  frontend/public/maps/vienna-ubahn-circles.svg
Output: frontend/public/maps/vienna-ubahn-display.svg

The source is preserved. The indices in DECORATION_INDICES are specific to
this version of the SVG and are validated before removing any elements.
"""
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'public' / 'maps' / 'vienna-ubahn-circles.svg'
OUTPUT = ROOT / 'public' / 'maps' / 'vienna-ubahn-display.svg'
SVG_NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG_NS)

COLORS = {'#ce2b31', '#945d9e', '#d47800', '#209640', '#91642f'}

@dataclass(frozen=True)
class MapStyle:
    line_scale: float = 2.4

    # Relative to the final metro line width
    station_diameter_ratio: float = 0.95
    station_outline_ratio: float = 0.10

STYLE = MapStyle()


def tag(element):
    return element.tag.rsplit('}', 1)[-1]



def generate():
    # --------------------------------------------------
    # 1. Load and validate the source SVG
    # --------------------------------------------------

    tree = ET.parse(SOURCE)
    root = tree.getroot()

    if root.get('viewBox') != '0 0 1122.5 793.7':
        raise ValueError(
            'Unexpected SVG viewBox. '
            'Decorative-element selection must be reviewed.'
        )

    # --------------------------------------------------
    # 2. Remove decorative elements
    # --------------------------------------------------

    # This selection is specific to the January 2026 SVG.
    artwork = next(
        (element for element in root
         if tag(element) == 'g' and len(element) >= 59),
        None,
    )

    if artwork is None or len(artwork) != 59:
        raise ValueError(
            'SVG structure has changed. '
            'Cannot safely remove decorative elements.'
        )

    decoration_indices = {2, *range(47, 59)}

    for index in sorted(decoration_indices, reverse=True):
        artwork.remove(artwork[index])

    # Remove the separate decorative U1 legend badge.
    for element in list(root):
        if tag(element) != 'g':
            continue

        is_legend_badge = any(
            tag(child) == 'rect'
            and child.get('x') == '1009.2'
            for child in element
        )

        if is_legend_badge:
            root.remove(element)

    # Remove any old opaque cover rectangles.
    for element in list(root):
        if (
            tag(element) == 'rect'
            and element.get('fill') == '#f2f2f2'
            and element.get('x') in ('0', '970')
        ):
            root.remove(element)

    # --------------------------------------------------
    # 3. Identify the five metro routes
    # --------------------------------------------------

    metro_paths = [
        element
        for element in root.iter()
        if tag(element) == 'path'
        and element.get('stroke', '').lower() in COLORS
    ]

    if len(metro_paths) != 5:
        raise ValueError(
            f'Expected 5 metro routes, found {len(metro_paths)}.'
        )

    # --------------------------------------------------
    # 4. Calculate dimensions
    # --------------------------------------------------

    original_widths = [
        float(element.get('stroke-width', '5.17'))
        for element in metro_paths
    ]

    original_line_width = sum(original_widths) / len(original_widths)
    line_width = original_line_width * STYLE.line_scale

    station_radius = (
        line_width * STYLE.station_diameter_ratio / 2
    )

    station_outline = (
        line_width * STYLE.station_outline_ratio
    )

    # --------------------------------------------------
    # 5. Scale metro lines
    # --------------------------------------------------

    for element in metro_paths:
        original_width = float(element.get('stroke-width', '5.17'))

        element.set(
            'stroke-width',
            f'{original_width * STYLE.line_scale:.3f}',
        )
        element.set('stroke-linejoin', 'round')
        element.set('stroke-linecap', 'round')

    # --------------------------------------------------
    # 6. Scale ordinary station circles
    # --------------------------------------------------

    station_circles = [
        element
        for element in root.iter()
        if (
            tag(element) == 'circle'
            and element.get('fill', '').lower() == '#ffffff'
            and element.get('stroke', '').lower() == '#222222'
        )
    ]

    if len(station_circles) != 89:
        raise ValueError(
            f'Expected 89 ordinary station circles, '
            f'found {len(station_circles)}.'
        )

    for element in station_circles:
        element.set('r', f'{station_radius:.3f}')
        element.set('stroke-width', f'{station_outline:.3f}')

    # --------------------------------------------------
    # 7. Save the generated SVG
    # --------------------------------------------------

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    tree.write(
        OUTPUT,
        encoding='utf-8',
        xml_declaration=True,
    )

    # --------------------------------------------------
    # 8. Print summary
    # --------------------------------------------------

    print(f'Metro lines:         {len(metro_paths)}')
    print(f'Ordinary stations:   {len(station_circles)}')
    print(f'Original line width: {original_line_width:.2f}')
    print(f'New line width:      {line_width:.2f}')
    print(f'Station radius:      {station_radius:.2f}')
    print(f'Station outline:     {station_outline:.2f}')
    print(f'Output: {OUTPUT}')


if __name__ == '__main__':
    generate()
