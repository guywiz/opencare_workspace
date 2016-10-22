from tulip import *

class LiftUp(object):
	'''
	Utility class selecting items in the original forum_graph
	associated with pre-selected tags in the tag-tag graph.

	Graphs must be strictly named for the class to properly work.
	'''
	def __init__(self, graph):
		self.tagtag_graph = graph
		self.tagtag_graph.getBooleanProperty('viewSelection')
		self.forum_graph = self.tagtag_graph.getSuperGraph().getSubGraph('Forum Network')
		vs = self.forum_graph.getBooleanProperty('viewSelection')
		self.forum_graph.getStringProperty('entity_type')

	def lift_up(self):
		selected_tags = set()
		for e in self.tagtag_graph.getEdges():
			if self.tagtag_graph['viewSelection'][e]:
				selected_tags.add(self.tagtag_graph.source(e))
				selected_tags.add(self.tagtag_graph.target(e))
		for t in selected_tags:
			self.forum_graph['viewSelection'][t] = True
			for n in self.forum_graph.getOutNodes(t):
				self.forum_graph['viewSelection'][n] = True
				for a in self.forum_graph.getInNodes(n):
					if self.forum_graph['entity_type'][a] == 'user':
						self.forum_graph['viewSelection'][a] = True
		nodeSet = set()
		for n in self.forum_graph.getNodes():
			if self.forum_graph['viewSelection'][n]:
				nodeSet.add(n)
		g = self.forum_graph.inducedSubGraph(nodeSet)
		g.setName('Selected tags subgraph')


# SHould be run as a script within the Tulip GUI
def main(graph):
	lu = LiftUp(graph)
	lu.lift_up()
