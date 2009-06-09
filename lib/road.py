class Road:
	def __init__(self, start, end):
		self.start = start
		self.end = end

	def length(self):
		return self.start.distance_to(self.end)
