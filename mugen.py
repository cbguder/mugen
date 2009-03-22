#!/usr/bin/env python

# Average vehicle speed in m/s
SPEED_MEAN  = 30.0
SPEED_STDEV = 4.0

# Vehicle density in vehicles/hour
VEHICLE_DENSITY = 2600
ARRIVAL_MEAN    = VEHICLE_DENSITY / 3600.0
ARRIVAL_STDEV   = 0.8

import sys
import random
from parser import parse
from models import Path

def main():
	if len(sys.argv) < 2:
		print "Usage: mugen.py FILE"
		sys.exit()

	filename = sys.argv[1]

	f = open(filename)
	generate(f)
	f.close()

def generate(f):
	(points, roads) = parse(f)

	paths = find_all_paths(points, roads)

	start_t = 0.0
	end_t   = 0.0

	while start_t < 60.0:
		speed   = random.gauss(SPEED_MEAN, SPEED_STDEV)
		arrival = start_t + random.gauss(ARRIVAL_MEAN, ARRIVAL_STDEV)
		start_t = arrival
		path    = random.choice(paths)
		dt      = path.total_distance() / speed
		end_t   = max(end_t, start_t + dt)

		print start_t, path

def find_all_paths(points, roads):
	paths  = []
	tpaths = []

	entrances = points[:]
	exits     = points[:]

	for road in roads:
		if road.end in entrances:
			entrances.remove(road.end)
		if road.start in exits:
			exits.remove(road.start)

	for road in roads:
		if road.start in entrances:
			tpaths.append(Path([road.start, road.end]))

	while len(tpaths):
		t2paths = []
		for path in tpaths:
			if len(path) > 1 and path[0] in entrances and path[-1] in exits:
				paths.append(path)
			elif not path.is_cyclic():
				for road in roads:
					if road.start == path[-1]:
						t2paths.append(Path(path.points + [road.end]))
		tpaths = t2paths

	return paths

if __name__ == '__main__':
	main()
