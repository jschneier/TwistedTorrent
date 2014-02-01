from hashlib import sha1
#from collections import defaultdict
#from twisted.internet import protocol

from .constants import K

def distance(node1, node2):
    return to_int(node1.id) ^ to_int(node2.id)

def to_int(node_id):
    return int(node_id.encode('hex'), 16)

class RoutingTable(object):

    def __init__(self, node):
        # the root node -- AKA us
        self.node = node
        self.buckets = [Bucket([node], 0, 2**160)]

    def insert_node(self, node):
        dist = distance(self.node, node)

class Bucket(object):

    def __init__(self, nodes, min, max):
        self.nodes = nodes
        self.min = min
        self.max = max

class Node(object):

    def __init__(self, id):
        self.id = id
