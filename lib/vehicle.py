from movement import Movement
from util import distance, intersect, interpolate

class Vehicle:
	def __init__(self):
		self.arrival = 0.0
		self.leave = 0.0

		self.collisions = []
		self.movements = []
		self.path = []
		self.speed = 0.0

	def calculate_movements(self):
		self.movements = []

		t = self.arrival
		for i in range(len(self.path) - 1):
			m = Movement()
			m.time = t
			m.start = self.path[i]
			m.end = self.path[i+1]
			m.speed = self.speed

			duration = distance(m.start, m.end) / m.speed
			t += duration

			if t > 0:
				if m.time < 0:
					# Interpolate position at t = 0
					ratio   = -m.time / duration
					m.start = interpolate(m.start, m.end, ratio)
					self.arrival = m.time = 0.0

				self.movements.append(m)

		self.leave = t

	def calculate_collisions(self, regions):
		self.collisions = []

		for region in regions:
			for m in self.movements:
				intersection = intersect((m.start, m.end), region)
				if intersection != None:
					time = m.time + distance(m.start, intersection) / m.speed
					collision = {'time': time, 'region': region}
					self.collisions.append(collision)
					break
