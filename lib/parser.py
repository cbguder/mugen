import re

def parse(f):
	points = {}
	roads = []
	regions = []

	point_pattern = re.compile("(\w+)\s+(\d*\.?\d+)\s+(\d*\.?\d+)$")
	road_pattern = re.compile("(\w+)\s+->\s+(\w+)$")
	region_pattern = re.compile("R\s+(\d*\.?\d+)\s+(\d*\.?\d+)\s+(\d*\.?\d+)\s+(\d*\.?\d+)$")

	for line in f:
		line = line.strip()
		if line != '':
			m = point_pattern.match(line)
			if m:
				points[m.group(1)] = (float(m.group(2)), float(m.group(3)))
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
							 'height': float(m.group(4))}
						regions.append(r)

	return points.values(), roads, regions
