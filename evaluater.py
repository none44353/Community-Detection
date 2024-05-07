import numpy as np
import sys
datasets = ["youtube", "dblp", "amazon", "lj"]
types = ["all", "top5000"]
t = 1.001

def read_community_file(file_name):
    communities = []
    with open(file_name, 'r') as file:
        lines = file.readlines()
        for line in lines:
            nodes = line.strip().split('\t')
            community = [int(node) for node in nodes]
            communities.append(community)
    return communities

def get_map_history(output_file_name):
    history = []

    with open(output_file_name, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('Iteration'):
                history.append([])
            else:
                nodes = line.strip().split(',')
                history[-1].append([int(node) for node in nodes])
    
    map_history = []
    for clusters in history:
        map_history.append({})
        for i, cluster in enumerate(clusters):
            for node in cluster:
                map_history[-1][node] = i
    return map_history

def get_score(map, community):
    sizes = {}
    k = 0
    for node in community:
        if not map[node] in sizes.keys():
            sizes[map[node]] = 0
            k += 1
        sizes[map[node]] += 1

    
    n_ave = len(community) / k
    score = 0
    for ni in list(sizes.values()):
        score += ni**2
    base_line = n_ave**2 * k
    return score / base_line

def evaluate(community_file_name, output_file_name):
    communities = read_community_file(community_file_name)
    map_history = get_map_history(output_file_name)
    rounds = len(map_history)

    scores = []  # Initialize the scores list
    print("Rounds = {}".format(rounds))

    score = {}
    for k, community in enumerate(communities):
        for i in range(rounds):
            map_i = map_history[i]
            if (k, i) not in score:
                score[(k, i)] = get_score(map_i, community)
        
    for i in range(rounds):
        average_score = 0
        for k in range(len(communities)):
            average_score += score[(k, i)]
        average_score /= len(communities)
        print("Round {}, Average score = {}".format(i, average_score))
    average_score = np.mean(list(score.values()))
    print("Average score = {}".format(average_score))

    bad_communities = []
    for k in range(len(communities)):
        average_score = 0
        for i in range(rounds):
            average_score += score[(k, i)]
        average_score /= rounds
        if average_score < t:
            bad_communities.append(k)    
    # print("Bad communities: {}".format(bad_communities))

    return
 
def main():
    sys.stdout = open('data\log.txt', 'w')  # Redirect stdout to log.txt
    for dataset in datasets:
        print("Current Dataset: {}".format(dataset))
        for type in types:
            community_file_name = 'data\com-{}.{}.cmty.txt'.format(dataset, type)                
            output_file_name = 'data\{}_clusters.txt'.format(dataset)
            print("* {}".format(type.capitalize()))
            evaluate(community_file_name, output_file_name)
            print("\n")
    sys.stdout.close()  # Close the log file

if __name__ == '__main__':
    main()