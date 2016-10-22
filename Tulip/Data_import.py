from tulip import *
import json

class Data_Import(object):
	'''
	Utility class  turning json objects into a graph.
	This code mimicks the graph object we get by querying the Neo4j database.
	Users are authors of posts and comments; comments point to posts or comments.
	Tags are attached to posts or comments.

	This graph, here and there called "forum_graph" is the one from which other graphs are derived.
	'''
	def __init__(self, graph):
		self.filenames = {'user': 'users-pretty.json', 'post': 'content-pretty.json',\
							'comment': 'comments-pretty.json', 'tag': 'tags-pretty.json',\
							'annotation': 'annotations-pretty.json'}
		self.node_shapes = {'user': tlp.TulipFontAwesome.User, 'post': tlp.TulipFontAwesome.AlignLeft,\
							'comment': tlp.TulipFontAwesome.Comment, 'tag': tlp.TulipFontAwesome.Tag}
		self.node_colors = {'user': tlp.Color.Carmine, 'post': tlp.Color.Amber,\
							'comment': tlp.Color.Apricot, 'tag': tlp.Color.Burgundy}
		self.tulip_graph = graph

	def data_nodes(self, entity_type):
		'''
		Nodes are instanciated from posts and comments.
		Users are not instanciated from the users file, they instead
		are instanciated from the author id contained in the post and commment files.
		'''
		with open(self.filenames[entity_type], 'rU') as fp:
			json_object = json.load(fp)
			if not self.tulip_graph.existProperty('entity_type'):
				self.tulip_graph.getStringProperty('entity_type')
			i = 0
			for entry in json_object['nodes']:
				node = self.tulip_graph.addNode()
				for key in entry['node'].keys():
					if not self.tulip_graph.existProperty(key):
						self.tulip_graph.getStringProperty(key)
					self.tulip_graph[key][node] = entry['node'][key]
				self.tulip_graph['viewShape'][node] = tlp.NodeShape.FontAwesomeIcon
				self.tulip_graph['viewFontAwesomeIcon'][node] = self.node_shapes[entity_type]
				self.tulip_graph['entity_type'][node] = entity_type
				self.tulip_graph['viewColor'][node] = self.node_colors[entity_type]

				if entity_type == 'post' or entity_type == 'comment':
					user_id = entry['node']['user_id']
					user_node = self.find_node(user_id, self.tulip_graph['user_id'], 'user')
					if user_node == None:
						user_node = self.tulip_graph.addNode()
					self.tulip_graph['user_id'][user_node] = user_id
					self.tulip_graph['viewShape'][user_node] = tlp.NodeShape.FontAwesomeIcon
					self.tulip_graph['viewFontAwesomeIcon'][user_node] = self.node_shapes['user']
					self.tulip_graph['entity_type'][user_node] = 'user'
					self.tulip_graph['viewColor'][user_node] = self.node_colors['user']

	def find_node(self, id, idProperty, entity_type):
		'''
		Utility function returning a node associated with an id.
		used to locate users or posts or comments or tags.
		'''
		for n in self.tulip_graph.getNodes():
			if self.tulip_graph['entity_type'][n] == entity_type:
				if idProperty[n] == id:
					return n

	def find_edge(self, source, target, graph):
		'''
		Utility function returning an edge associated with source and target nodes,
		searched in the graph passed as argument.
		'''
		edge = graph.existEdge(source, target, False)
		if not edge.isValid():
			edge = graph.addEdge(source, target)
		return edge

	def post_edges(self):
		'''
		Creates edges between posts and users.
		'''
		added_edges = 0
		with open(self.filenames['post'], 'rU') as fp:
			json_object = json.load(fp)
			for entry in json_object['nodes']:
				post_id = entry['node']['post_id']
				post_node = self.find_node(post_id, self.tulip_graph['post_id'], 'post')
				user_id = entry['node']['user_id']
				user_node = self.find_node(user_id, self.tulip_graph['user_id'], 'user')
				if post_node != None and user_node != None:
					self.tulip_graph.addEdge(user_node, post_node)
					added_edges += 1
				else:
					print 'Post ', post_id
					print 'User ', user_id
		return added_edges

	def comment_edges(self).
		'''
		Creates edges between comments and users?
		'''
		added_edges = 0
		with open(self.filenames['comment'], 'rU') as fp:
			json_object = json.load(fp)
			for entry in json_object['nodes']:
				comment_id = entry['node']['comment_id']
				comment_node = self.find_node(comment_id, self.tulip_graph['comment_id'], 'comment')
				user_id = entry['node']['user_id']
				user_node = self.find_node(user_id, self.tulip_graph['user_id'], 'user')
				if comment_node != None and user_node != None:
					self.tulip_graph.addEdge(user_node, comment_node)
					added_edges += 1
				if entry['node']['parent_comment_id'] == '0':
					post_id = entry['node']['post_id']
					post_node = self.find_node(post_id, self.tulip_graph['post_id'], 'post')
					if post_node != None and comment_node != None:
						self.tulip_graph.addEdge(comment_node, post_node)
						added_edges += 1
				else:
					parent_id = entry['node']['parent_comment_id']
					parent_node = self.find_node(parent_id, self.tulip_graph['comment_id'], 'comment')
					if parent_node != None and comment_node != None:
						self.tulip_graph.addEdge(comment_node, parent_node)
						added_edges += 1
		return added_edges


	def tag_edges(self):
		'''
		Creates edges between tags and posts or comments.
		'''
		added_edges = 0
		with open(self.filenames['annotation'], 'rU') as fp:
			json_object = json.load(fp)
			i = 0
			for entry in json_object['nodes']:
				tag_id = entry['node']['tag_id']
				tag_node = self.find_node(tag_id, self.tulip_graph['tag_id'], 'tag')
				if entry['node']['entity_type'] == 'node':
					post_id = entry['node']['entity_id']
					post_node = self.find_node(post_id, self.tulip_graph['post_id'], 'post')
					if post_node != None and tag_node != None:
						edge = self.find_edge(tag_node, post_node, self.tulip_graph)
						if edge == None:
							self.tulip_graph.addEdge(tag_node, post_node)
							added_edges += 1
				if entry['node']['entity_type'] == 'comment':
					comment_id = entry['node']['entity_id']
					comment_node = self.find_node(comment_id, self.tulip_graph['comment_id'], 'comment')
					if comment_node != None and tag_node != None:
						edge = self.find_edge(tag_node, comment_node, self.tulip_graph)
						if edge == None:
							self.tulip_graph.addEdge(tag_node, comment_node)
							added_edges += 1
		return added_edges

if __name__ == '__main__':
	g = tlp.newGraph()
	di = Data_Import(g)
	print 'Processing posts'
	di.data_nodes('post')
	print 'Processing comments'
	di.data_nodes('comment')
	print 'Processing tags'
	di.data_nodes('tag')

	post_edges = di.post_edges()
	print 'Connecting posts and users', post_edges
	comment_edges = di.comment_edges()
	print 'Connecting comments and users', comment_edges
	tag_edges = di.tag_edges()
	print 'Connecting tags to content', tag_edges
	di.tulip_graph.addCloneSubGraph('Forum Network')
	tlp.saveGraph(di.tulip_graph, 'opencare.tlp')
