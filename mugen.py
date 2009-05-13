#!/usr/bin/env python

VERSION = 0.3

SIMULATION_TIME = 60.0

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
from models import Point, Path
from util import *

def main():
	if len(sys.argv) < 2:
		print "Usage: mugen.py FILE"
		sys.exit()

	filename = sys.argv[1]

	with open(filename) as f:
		vehicles = generate(f)

	with open(filename + '.gpi', 'w') as f:
		plot_vehicle_count(f, vehicles)

	with open(filename + '.tcl', 'w') as f:
		generate_ns2_scene(f, vehicles)

	display_stats(vehicles)

def generate(f):
	points, roads, regions = parse(f)

	paths = find_all_paths(points, roads)
	trim = calculate_trim(paths)
	vehicles = generate_movement(paths, SIMULATION_TIME + trim)
	trimmed = trim_vehicles(vehicles, trim)

	add_collisions(trimmed, regions)

	return trimmed

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

def calculate_trim(paths):
	longest_dist = 0.0
	for path in paths:
		dist = path.total_distance()
		if dist > longest_dist:
			longest_dist = dist

	return longest_dist / SPEED_MEAN

def generate_movement(paths, duration):
	t = 0.0

	vehicles = []

	while t < duration:
		speed   = random.gauss(SPEED_MEAN, SPEED_STDEV)
		arrival = t + random.gauss(ARRIVAL_MEAN, ARRIVAL_STDEV)
		path    = random.choice(paths)

		vehicles.append({'speed'  : speed,
		                 'arrival': arrival,
		                 'path'   : path})

		t = arrival

	return vehicles

def trim_vehicles(vehicles, trim):
	trimmed = []

	for v in vehicles:
		path    = v['path']
		arrival = v['arrival'] - trim
		times   = [t + arrival for t in path.get_times(v['speed'])]

		if times[0] < SIMULATION_TIME and times[-1] >= 0:
			if times[0] < 0:
				# Interpolate position at t = 0
				i = 0
				while times[i] < 0:
					i += 1

				ratio   = times[i] / (times[i] - times[i-1])
				initial = interpolate(path[i], path[i-1], ratio)
				initial = Point('S', initial[0], initial[1])

				arrival = 0.0
				times = [0.0] + times[i:]
				path = Path([initial] + path[i:])

			v['arrival'] = arrival
			v['times']   = times
			v['path']    = path

			trimmed.append(v)

	return trimmed

def add_collisions(vehicles, regions):
	for v in vehicles:
		v['collisions'] = []
		collisions = v['path'].get_collisions(regions, v['speed'])

		for collision in collisions:
			collision['time'] += v['arrival']
			if collision['time'] < SIMULATION_TIME:
				for event in collision['region']['events']:
					if random.random() < event['probability']:
						dispatch = {'time': collision['time'],
						            'event': event['id']}
						v['collisions'].append(dispatch)

def plot_vehicle_count(f, vehicles):
	v_count = {}

	for v in vehicles:
		dt = v['path'].total_distance() / v['speed']
		v['leave'] = v['arrival'] + dt

		v_count[v['arrival']] = v_count.get(v['arrival'], 0) + 1
		v_count[v['leave']] = v_count.get(v['leave'], 0) - 1

	times = sorted(v_count.keys())
	real_count = 0

	f.write("set style data lines\n")
	f.write("set xrange[0:%f]\n" % SIMULATION_TIME)
	f.write("set yrange[0:]\n")
	f.write("set xlabel 'time (s)'\n")
	f.write("set ylabel 'Vehicles'\n")
	f.write("set nokey\n")
	f.write("plot '-'\n")

	for t in times:
		real_count += v_count[t]
		f.write("%f %d\n" % (t, real_count))

def generate_ns2_scene(f, vehicles):
	f.write('#\n')
	f.write('# Generated using MUGEN %.1f\n' % VERSION)
	f.write('#\n')
	for line in get_stats(vehicles):
		f.write('# ')
		f.write(line)
		f.write('\n')
	f.write('#\n')

	for i, v in enumerate(vehicles):
		f.write('$node_(%d) set X_ %f\n' % (i, v['path'][0].x))
		f.write('$node_(%d) set Y_ %f\n' % (i, v['path'][0].y))
		f.write('$node_(%d) set Z_ %f\n' % (i, 0))

		f.write('$ns_ at %f "$beacon_(%d) PeriodicBroadcast ON"\n' % (v['times'][0], i))

		for j, t in enumerate(v['times'][:-1]):
			p = v['path'][j+1]
			f.write('$ns_ at %f "$node_(%d) setdest %f %f %f"\n' % (t, i, p.x, p.y, v['speed']))

		for collision in v['collisions']:
			f.write('$ns_ at %f "$agent_(%d) send %d"\n' % (collision['time'], i, collision['event']))

		if v['times'][-1] < SIMULATION_TIME:
			params = (v['times'][-1], i, i)
			f.write('$ns_ at %f "$ns_ detach-agent $node_(%d) $agent_(%d)"\n'  % params)
			f.write('$ns_ at %f "$ns_ detach-agent $node_(%d) $beacon_(%d)"\n'  % params)

def display_stats(vehicles):
	for line in get_stats(vehicles):
		print line

def get_stats(vehicles):
	stats = []
	stats.append("Simulation Time: %.2fs" % SIMULATION_TIME)
	stats.append("")
	stats.append("Mean Speed:      %.2f m/s" % SPEED_MEAN)
	stats.append("Speed Std. Dev.:  %.2f m/s" % SPEED_STDEV)
	stats.append("")
	stats.append("Vehicle Density: %d veh/h" % VEHICLE_DENSITY)
	stats.append("")
	stats.append("Mean Inter-Arrival Time:      %.2fs" % ARRIVAL_MEAN)
	stats.append("Inter-Arrival Time Std. Dev.: %.2fs" % ARRIVAL_STDEV)
	stats.append("")
	stats.append("Number of Vehicles: %d" % len(vehicles))
	return stats

if __name__ == '__main__':
	main()
