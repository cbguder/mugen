import re
from point import Point

def parse(f):
	points = {}
	roads = []
	regions = []

	point_pattern = re.compile("(\w+)\s+(\d*\.?\d+)\s+(\d*\.?\d+)$")
	road_pattern = re.compile("(\w+)\s+->\s+(\w+)$")
	region_pattern = re.compile("R\s+(\d*\.?\d+)\s+(\d*\.?\d+)\s+(\d*\.?\d+)\s+(\d*\.?\d+)$")
	event_pattern = re.compile("E\s*(\d+)\s+(\d*\.?\d+)$")

	for line in f:
		line = line.strip()
		if line != '':
			m = point_pattern.match(line)
			if m:
				p = Point(m.group(1), float(m.group(2)), float(m.group(3)))
				points[m.group(1)] = p
			else:
				m = road_pattern.match(line)
				if m:
					roads.append((points[m.group(1)], points[m.group(2)]))
				else:
					m = region_pattern.match(line)
					if m:
						r = {'x': float(m.group(1)),
							 'y': float(m.group(2)),
							 'width': float(m.group(3)),
							 'height': float(m.group(4)),
							 'events': []}
						regions.append(r)
					else:
						m = event_pattern.match(line)
						if m:
							e = {'id': int(m.group(1)),
							     'probability': float(m.group(2))}
							regions[-1]['events'].append(e)

	return points.values(), roads, regions
