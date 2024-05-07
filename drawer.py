from adjustText import adjust_text
import math

datasets = ["dblp", "amazon", "youtube", "lj"]
cluster_numbers = {"youtube": [], "dblp": [], "amazon": [], "lj": []}
colors = {"youtube": 'blue', "dblp": 'orange', "amazon": 'green', "lj": 'red'}
titles = {"youtube": 'Youtube Dataset', "dblp": 'DBLP Dataset', "amazon": 'Amazon Dataset', "lj": 'LiveJournal Dataset'}

def load_scores():
    dataset = None
    type = None
    eval_scores = {"All":{}, "Top5000":{}}
    with open('data\log.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('Current Dataset:'):
                dataset = line.strip().split(': ')[1]
            elif line.startswith('*'):
                type = line.strip().split(' ')[1]
            elif line.startswith('Round '):
                #Format: "Round 0, Average score = 1.2902725157508677"
                iteration = int(line.strip().split(', Average score = ')[0].split(' ')[-1]) 
                score = float(line.strip().split(' = ')[-1])
                if not dataset in eval_scores[type].keys():
                    eval_scores[type][dataset] = []
                eval_scores[type][dataset].append(score)

    return eval_scores['All'], eval_scores['Top5000']


def calc_cluster_numbers(cluster_numbers, output_file_name):
    with open(output_file_name, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('Iteration'):
                cluster_numbers.append(0)
            else:
                cluster_numbers[-1] += 1
    return

def draw(all_scores, top5000_scores):
    import matplotlib.pyplot as plt

    fig, axs = plt.subplots(2, 2, figsize=(10, 8))

    for i, dataset in enumerate(datasets):
        ax = axs[i // 2, i % 2]
        x_values = range(1, len(cluster_numbers[dataset]) + 1)

        ax2 = ax.twinx()
        num = cluster_numbers[dataset]
        log_num = [0 if x == 0 else math.log(x) for x in num]
        ax2.plot(x_values, log_num, linestyle='dashed', color='gray', label='Cluster Numbers')
        ax2.scatter(x_values, log_num, color='gray', marker='.')
        for j, x in enumerate(num):
            ax2.annotate('({:d})'.format(x), (j + 1, log_num[j]), ha='left', va='center', color = "gray")

        ax.plot(x_values, all_scores[dataset], label="All", color=colors[dataset])
        ax.scatter(x_values, all_scores[dataset], color=colors[dataset], marker='x')

        ax.plot(x_values, top5000_scores[dataset], linestyle='dotted', color=colors[dataset], label='Top 5k')
        ax.scatter(x_values, top5000_scores[dataset], color=colors[dataset], marker='+')

        texts = []
        for j, (x, y) in enumerate(zip(cluster_numbers[dataset], all_scores[dataset])):
            texts.append(ax.text(j + 1, y, '{:.2f}'.format(y), ha='left', va='top'))
        for j, (x, y) in enumerate(zip(cluster_numbers[dataset], top5000_scores[dataset])):
            if round(y,2) != round(all_scores[dataset][j],2):
                texts.append(ax.text(j + 1, y, '{:.2f}'.format(y), ha='left', va='top'))
        adjust_text(texts, ax=ax, lim = 5)

        ax2.set_ylabel('ln(Number of Clusters)')
        ax2.spines['top'].set_visible(False)
        # ax2.set_yticklabels([])
        # ax2.spines['right'].set_visible(False)
        # ax2.tick_params(right = False)

        ax.set_title(titles[dataset])
        ax.set_xlabel('Iteration Number')
        ax.set_ylabel('Average Score')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_xticks(range(1, len(cluster_numbers[dataset]) + 1))
        ax.set_xticklabels(range(1, len(cluster_numbers[dataset]) + 1))
        ax.plot([], [], linestyle='dashed', color='gray', label='# Clusters')
        ax.legend()

    plt.tight_layout()
    plt.show()

def count_communities():
    counter = {}
    total_nodes = {}
    for dataset in datasets:
        community_file_name = 'data\com-{}.all.cmty.txt'.format(dataset)
        counter[dataset] = 0
        total_nodes[dataset] = 0
        with open(community_file_name, 'r') as file:
            lines = file.readlines()
            for line in lines:
                nodes = line.strip().split('\t')
                if len(nodes) != 0:
                    counter[dataset] += 1
                    total_nodes[dataset] += len(nodes)
    
    print("# Clusters: ", counter)
    average_cluster_size = {}
    for dataset in datasets:
        average_cluster_size[dataset] = total_nodes[dataset] / counter[dataset]
    print("Average Cluster Size: ", average_cluster_size)
    return 

if __name__ == '__main__':
    all_scores, top5000_scores = load_scores()
    for dataset in datasets:
        output_file_name = 'data\\' + dataset + '_clusters.txt'
        calc_cluster_numbers(cluster_numbers[dataset], output_file_name)
    
    draw(all_scores, top5000_scores)
    count_communities()