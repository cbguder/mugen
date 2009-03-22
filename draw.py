#!/usr/bin/env python

import sys
import PSDraw
from parser import parse

def main():
	if len(sys.argv) < 2:
		print "Usage: draw.py FILE"
		sys.exit()

	filename     = sys.argv[1]
	out_filename = filename + '.ps'

	f = open(filename)
	draw(f, out_filename)
	f.close()

def draw(f, out):
	(points, roads) = parse(f)

	scale = 0

	for p in points:
		M = max(p.x, p.y)
		if M > scale:
			scale = M

	out = open(out, 'w')
	ps = PSDraw.PSDraw(out)
	ps.begin_document()

	for road in roads:
		a = road.start.x * 600 / scale
		b = road.start.y * 600 / scale
		c = road.end.x * 600 / scale
		d = road.end.y * 600 / scale
		ps.line((a, b), (c, d))

	ps.end_document()
	out.close()

if __name__ == '__main__':
	main()
