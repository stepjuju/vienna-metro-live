"""Convert ordinary station ticks into circles without moving their centers.

Run from the repository root:
  python frontend/scripts/create_station_map.py

The original SVG is never modified.
"""
from math import cos, radians, sin
from pathlib import Path
import re
import xml.etree.ElementTree as ET

FRONTEND = Path(__file__).resolve().parents[1]
SOURCE = FRONTEND / 'public' / 'maps' / 'vienna-ubahn-original.svg'
OUTPUT = FRONTEND / 'public' / 'maps' / 'vienna-ubahn-circles.svg'

NS = 'http://www.w3.org/2000/svg'
RECT = f'{{{NS}}}rect'
CIRCLE = f'{{{NS}}}circle'
ET.register_namespace('', NS)

COLORS = {
    '#ce2b31': 'U1',
    '#945d9e': 'U2',
    '#d47800': 'U3',
    '#209640': 'U4',
    '#91642f': 'U6',
}


def apply_transform(transform, x, y):
    """Return transformed center; SVG transform functions execute in right-to-left order."""
    commands = re.findall(r'(matrix|rotate|translate|scale)\s*\(([^)]*)\)', transform or '')
    for op, args in reversed(commands):
        values = [float(v) for v in re.split(r'[\s,]+', args.strip()) if v]
        if op == 'matrix':
            a, b, c, d, e, f = values
            x, y = a * x + c * y + e, b * x + d * y + f
        elif op == 'rotate':
            angle = radians(values[0])
            cx, cy = (values[1], values[2]) if len(values) == 3 else (0, 0)
            dx, dy = x - cx, y - cy
            x = cx + cos(angle) * dx - sin(angle) * dy
            y = cy + sin(angle) * dx + cos(angle) * dy
        elif op == 'translate':
            x += values[0]
            y += values[1] if len(values) > 1 else 0
        elif op == 'scale':
            x *= values[0]
            y *= values[1] if len(values) > 1 else values[0]
    return x, y


def world_center(element, parent_by_element, x, y):
    """Apply element and ancestor transforms, innermost to outermost."""
    node = element
    while node is not None:
        x, y = apply_transform(node.get('transform'), x, y)
        node = parent_by_element.get(node)
    return x, y


def find_line(element, parent_by_element):
    node = element
    while node is not None:
        color = (node.get('stroke') or '').lower()
        if color in COLORS:
            return COLORS[color]
        node = parent_by_element.get(node)
    return None


def main():
    tree = ET.parse(SOURCE)
    root = tree.getroot()
    parents = {child: parent for parent in root.iter() for child in parent}
    stations = []

    for element in root.iter(RECT):
        width = float(element.get('width', '0'))
        height = float(element.get('height', '0'))
        # The source uses exactly these dimensions for the ordinary ticks.
        if abs(width - 9.17) > 0.01 or abs(height - 2.1709) > 0.01:
            continue
        # Hidden SVG rectangles are not visible stations.
        if element.get('display', '').strip().lower() == 'none':
            continue
        if 'display:none' in element.get('style', '').replace(' ', '').lower():
            continue
        line = find_line(element, parents)
        if line is None:
            continue
        x = float(element.get('x', '0')) + width / 2
        y = float(element.get('y', '0')) + height / 2
        wx, wy = world_center(element, parents, x, y)
        stations.append((element, line, x, y, wx, wy))

    for element, line, x, y, wx, wy in stations:
        radius = 4.7
        circle = ET.Element(CIRCLE, {
            'cx': f'{x:.6f}',
            'cy': f'{y:.6f}',
            'r': f'{radius:.1f}',
            'fill': '#ffffff',
            'stroke': '#222222',
            'stroke-width': '1.5',
        })
        if element.get('transform'):
            circle.set('transform', element.get('transform'))
        parent = parents[element]
        index = list(parent).index(element)
        parent.remove(element)
        parent.insert(index, circle)


    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    tree.write(OUTPUT, encoding='utf-8', xml_declaration=True)
    print(f'Converted {len(stations)} ordinary station markers')
    print(f'Output: {OUTPUT}')
    if len(stations) != 90:
        print('WARNING: The marker count differs from the inspected source (90).')


if __name__ == '__main__':
    main()
