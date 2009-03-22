import re
from models import Point, Road

def parse(f):
	points = {}
	roads  = []

	point_pattern = re.compile("(\w+)\s+(\d*\.?\d+)\s+(\d*\.?\d+)")
	road_pattern  = re.compile("(\w+)\s+->\s+(\w+)")

	for line in f:
		m = point_pattern.match(line)
		if m:
			p = Point(m.group(1), float(m.group(2)), float(m.group(3)))
			points[m.group(1)] = p
		else:
			m = road_pattern.match(line)
			if m:
				r = Road(points[m.group(1)], points[m.group(2)])
				roads.append(r)

	return points.values(), roads
