#!/usr/bin/env python

import sys
import math
import cairo
import PSDraw
from parser import parse
from util import intersect

REGION_EXTEND = 100
RANGE = 500

def main():
	if len(sys.argv) < 2:
		print "Usage: draw.py FILE"
		sys.exit()

	filename     = sys.argv[1]
	out_filename = filename + '.svg'

	f = open(filename)
	draw(f, out_filename)
	f.close()

def draw(f, out):
	points, roads, regions = parse(f)

	mX = max([p.x for p in points])
	mY = max([p.y for p in points])

	surface = cairo.SVGSurface(out, mX, mY)
	context = cairo.Context(surface)
	context.set_line_width(2)

	context.set_source_rgb(1, 1, 1)
	context.rectangle(0, 0, mX, mY)
	context.fill()

	for region in regions:
		context.set_source_rgba(0, 1, 0, 0.5)
		context.rectangle(region['x'] - REGION_EXTEND, region['y'], REGION_EXTEND, region['height'])
		context.fill()
		context.rectangle(region['x'] + region['width'], region['y'], REGION_EXTEND, region['height'])
		context.fill()

		context.set_source_rgba(1, 0, 0, 0.5)
		context.rectangle(region['x'], region['y'], region['width'], region['height'])
		context.fill()

	context.set_source_rgb(0, 0, 0)
	for road in roads:
		context.move_to(road.start.x, road.start.y)
		context.line_to(road.end.x, road.end.y)
		context.stroke()

	context.set_source_rgb(0, 0, 1)
	for region in regions:
		for road in roads:
			intersection = intersect(road, region)
			if intersection != None:
				context.arc(intersection[0], intersection[1], RANGE, 0, 2 * math.pi)
				context.stroke()

				context.arc(intersection[0], intersection[1], 2, 0, 2 * math.pi)
				context.fill()

	surface.finish()

if __name__ == '__main__':
	main()
