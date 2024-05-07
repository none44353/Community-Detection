
import networkx
from louvain import Louvain

def input(file_name):
    graph = networkx.Graph()
    with open(file_name, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if not line.startswith('#'):
                from_node, to_node = line.strip().split('\t')
                graph.add_edge(int(from_node), int(to_node), weight=1)
        return graph

datasets = ["dblp", "amazon","youtube", "lj"]

def main():    
    for dataset in datasets:
        print("Current Dataset: {}".format(dataset))
        graph = input('data\com-{}.ungraph.txt'.format(dataset))
        LouvainAlg = Louvain(graph)
        LouvainAlg.run()
        LouvainAlg.get_clusters()

        output_file_name = 'data\{}_clusters.txt'.format(dataset)
        history = LouvainAlg.get_community_history()

        with open(output_file_name, 'w') as file:
            for i, clusters in enumerate(history):
                file.write('Iteration {}, Number of clusters = {}\n'.format(i, len(clusters)))
                for cluster in clusters:
                    file.write(','.join(str(node) for node in cluster))
                    file.write('\n')

def test():
    edges = [(0,2), (0,3), (0,4), (0,5), (1,2), 
             (1,4), (1,7), (2,4), (2,5), (2,6), 
             (3,7), (4,10), (5,7), (5,11), (6,7), 
             (6,11), (8,9), (8,10), (8,11), (8,14),
             (8,15), (9,12), (9,14), (10,11), (10,12), (10,13), (10,14), (11,13)]

    graph = networkx.Graph()
    for edge in edges:
        graph.add_edge(edge[0], edge[1], weight=1)
    
    LouvainAlg = Louvain(graph)
    LouvainAlg.run()
    LouvainAlg.get_clusters()

    output_file_name = 'data\example_clusters.txt'
    history = LouvainAlg.get_community_history()

    with open(output_file_name, 'w') as file:
        for i, clusters in enumerate(history):
            file.write('Iteration {}, Number of clusters = {}\n'.format(i, len(clusters)))
            for cluster in clusters:
                file.write(','.join(str(node) for node in cluster))
                file.write('\n')

if __name__ == '__main__':
    main()
    #test()