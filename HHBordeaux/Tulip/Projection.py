from tulip import *
import json


class Projection(object):
	'''
	Projects the original forum_graph onto a user-user network.
	'''
	def __init__(self, graph):
		self.filenames = {'user': 'users-pretty.json', 'post': 'content-pretty.json',\
							'comment': 'comments-pretty.json', 'tag': 'tags-pretty.json',\
							'annotation': 'annotations-pretty.json'}
		self.root_graph = graph
		self.forum_graph = self.root_graph.getSubGraph('Forum Network')
		self.forum_graph.getStringProperty('comment_id')
		self.forum_graph.getStringProperty('post_id')
		self.forum_graph.getStringProperty('user_id')
		self.forum_graph.getStringProperty('entity_type')
		self.interaction_graph = self.root_graph.addSubGraph('Interaction network')


	def find_node(self, id, idProperty, entity_type):
		for n in self.forum_graph.getNodes():
			if self.forum_graph['entity_type'][n] == entity_type:
				if idProperty[n] == id:
					return n

	def find_edge(self, source, target):
		edge = self.interaction_graph.existEdge(source, target, True)
		if not edge.isValid():
			edge = self.interaction_graph.addEdge(source, target)
		return edge

	def edge_project(self):
		# go through comments and for each
		#	for each comment c
		#		graph c tags
		#		find author user u_c
		# 		find parent comment or post p
		#		grab p tags
		#		find author user u_p
		# 		connect u_c and u_p, label edge with c tags and p tags
		with open(self.filenames['comment'], 'rU') as fp:
			json_object = json.load(fp)
			for entry in json_object['nodes']:
				comment_id = entry['node']['comment_id']
				comment_node = self.find_node(comment_id, self.forum_graph['comment_id'], 'comment')
				c_user_id = entry['node']['user_id']
				c_user_node = self.find_node(c_user_id, self.forum_graph['user_id'], 'user')

				if entry['node']['parent_comment_id'] == '0':
					parent_id = entry['node']['post_id']
					parent_node = self.find_node(parent_id, self.forum_graph['post_id'], 'post')

				else:
					parent_id = entry['node']['parent_comment_id']
					parent_node = self.find_node(parent_id, self.forum_graph['comment_id'], 'comment')

				if parent_node != None:
					p_user_node = None
					for n in self.forum_graph.getInNodes(parent_node):
						if self.forum_graph['entity_type'][n] == 'user':
							p_user_node = n
							break

					if c_user_node != None and p_user_node != None:
						self.interaction_graph.addNode(c_user_node)
						self.interaction_graph.addNode(p_user_node)
						edge = self.find_edge(c_user_node, p_user_node)

class TagTag(object):
	'''
	Projects the original forum_graph onto a tag-tag network, two tags being connected whenever they co-occur
	in *the same piece of content* (post or comment).
	Computes interesting metrics associated with nodes and edges of the tag-tag network.
	Each edge, a pair of co-occuring tags, is assigned a weight (number of co-occurences),
	For each edge, we additionally compute the number of users hiding behind the co-occurences.
	It is also useful to transfer, for each tag, its outgoing degree computed on the forum_graph
	which indicates the number of posts/comments to which a tag is attached.
	'''
	def __init__(self, graph):
		self.root_graph = graph
		self.forum_graph = self.root_graph.getSubGraph('Forum Network')
		self.forum_graph.getStringProperty('comment_id')
		self.forum_graph.getStringProperty('post_id')
		self.forum_graph.getStringProperty('user_id')
		self.forum_graph.getStringProperty('entity_type')
		self.tagtag_graph = self.root_graph.addSubGraph('Tag Tag Network')
		self.tagtag_graph.getDoubleProperty('edge_force')
		self.tagtag_graph.getDoubleProperty('nb_users')
		self.tagtag_graph.getStringProperty('users')

	def find_node(self, id, idProperty, entity_type, graph):
		for n in graph.getNodes():
			if graph['entity_type'][n] == entity_type:
				if idProperty[n] == id:
					return n

	def find_edge(self, source, target, graph):
		edge = graph.existEdge(source, target, False)
		if not edge.isValid():
			edge = graph.addEdge(source, target)
		return edge

	def tagtag_edges(self):
		for node in self.forum_graph.getNodes():
			if self.forum_graph['entity_type'][node] == 'post' or self.forum_graph['entity_type'][node] == 'comment':
				tag_nodes = []
				for neigh in self.forum_graph.getInNodes(node):
					if self.forum_graph['entity_type'][neigh] == 'tag':
						tag_nodes.append(neigh)
						self.tagtag_graph.addNode(neigh)
				for i, ni in enumerate(tag_nodes):
					for j, nj in enumerate(tag_nodes):
						if i < j:
							edge = self.find_edge(ni, nj, self.tagtag_graph)
							if edge == None:
								edge = self.tagtag_graph.addEdge(ni, nj)
							self.tagtag_graph['edge_force'][edge] += 1.0
							s = set(self.tagtag_graph['users'][edge].split(';'))
							s.add(self.forum_graph['user_id'][node])
							self.tagtag_graph['users'][edge] = ';'.join(s)
		for edge in self.tagtag_graph.getEdges():
			self.tagtag_graph['nb_users'][edge] = len(self.tagtag_graph['users'][edge].split(';')) - 1.0

if __name__ == '__main__':
	'''
	g = tlp.loadGraph('opencare.tlp')
	print g.numberOfNodes()
	print g.numberOfEdges()
	tagtag = TagTag(g)
	tagtag.tagtag_edges()
	tlp.saveGraph(g, 'opencare_tag_bis.tlp')
	'''
	g = tlp.loadGraph('opencare_tag.tlp')
	proj = Projection(g)
	proj.edge_project()
	tlp.saveGraph(g, 'opencare_tag_interaction.tlp')

