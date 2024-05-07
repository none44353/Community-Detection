import networkx

class Louvain:
    def __init__(self, G):
        self.original_graph = G
        self.graph = G
        print("Number of nodes: {}".format(self.graph.number_of_nodes()))
        self.m = G.size(weight="weight")
        self.get_new_community_map()

        self.community_ID = {}
        for node in self.original_graph.nodes():
            self.community_ID[node] = node
        self.community_history = []

    def get_new_community_map(self):
        self.community_map = {}
        self.degree_sum = {}
        self.self_loop = {}

        for node in self.graph.nodes():
            if self.graph.has_edge(node, node):
                self.self_loop[node] = self.graph[node][node]['weight']

        for node in self.graph.nodes():
            self.community_map[node] = node
            self.degree_sum[node] = self.graph.degree(node) + self.self_loop.get(node, 0)
            # Do this because undirected graph degree does not count self-loop.

    def get_neighbor_communities(self, node):
        graph = self.graph
        community_map = self.community_map

        neighbor_communities = {}
        for neighbor in graph.neighbors(node):
            neighbor_community = community_map[neighbor]
            if neighbor_community == None:
                continue
            if neighbor_community not in neighbor_communities:
                neighbor_communities[neighbor_community] = 0
            neighbor_communities[neighbor_community] += graph[node][neighbor]['weight']
        return neighbor_communities
    
    def calculate_Q(self, node, community, incident_weight):
        degree = self.graph.degree(node) + self.self_loop.get(node, 0)
        return 2 * incident_weight - self.degree_sum[community] * degree / self.m

    def local_improvement(self):
        modified = False
        graph = self.graph
        nodes = list(graph.nodes())

        while True:
            improved = False
            for node in nodes:
                old_community = self.community_map[node]
                degree = graph.degree(node) + self.self_loop.get(node, 0)
                best_community = old_community

                # Isolate current node temporarily to calculate increment of modularity
                self.community_map[node] = None
                self.degree_sum[old_community] -= degree

                neighbor_communities = self.get_neighbor_communities(node)
                best_delta_Q = self.calculate_Q(node, old_community, neighbor_communities.get(old_community, 0)) 

                for community, incident_weight in neighbor_communities.items():
                    delta_Q = self.calculate_Q(node, community, incident_weight)
                    if delta_Q > best_delta_Q:
                        best_delta_Q = delta_Q
                        best_community = community

                # Move current node to the best community
                self.community_map[node] = best_community
                self.degree_sum[best_community] += degree
                if best_community != old_community:
                    print("Node {} moved from {} to {}".format(node, old_community, best_community))
                    improved = True
                    modified = True
            if not improved:
                break

        return modified

    def get_new_graph(self, graph, community_map):
        # Before generating a new graph, we need to relabel the community IDs
        community_labels = set(community_map.values())
        relabelled_communities = {j: i for i, j in enumerate(community_labels)}
        for node in community_map:
            community_map[node] = relabelled_communities[community_map[node]]

        for node in self.original_graph.nodes():
            self.community_ID[node] = community_map[self.community_ID[node]]

        new_graph = networkx.Graph()
        for community in set(community_map.values()):
            new_graph.add_node(community)

        for from_node, to_node, weight in graph.edges(data='weight'):
            from_community = community_map[from_node]
            to_community = community_map[to_node]
            if not new_graph.has_edge(from_community, to_community):
                new_graph.add_edge(from_community, to_community, weight=0)
            new_graph[from_community][to_community]['weight'] += weight
            if from_node != to_node and from_community == to_community:
                new_graph[to_community][from_community]['weight'] += weight
                
        print("Generating a new graph with {} nodes ...".format(new_graph.number_of_nodes()))
        return new_graph

    def run(self):
        while True:
            modified = self.local_improvement()
            if not modified:
                break
            self.graph = self.get_new_graph(self.graph, self.community_map)
            self.get_new_community_map()
            self.community_history.append(self.get_clusters())

            # print("New graph:")
            # for edge in self.graph.edges(data=True):
            #     print(edge)
            # for node in self.graph.nodes():
            #     print("Node {} with Neighbors {}".format(node, list(self.graph.neighbors(node))))

    def get_clusters(self):
        clusters = {}
        for node, community in self.community_ID.items():
            if community not in clusters:
                clusters[community] = []
            clusters[community].append(node)
        return list(clusters.values())
    
    def get_community_history(self):
        return self.community_history
