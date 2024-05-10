# Community-Detection based on Louvain Algorithm

This is a course project for [Selected Topics in Social Computing](https://shaofengjiang.cn/networks-course/index.html)



In this project, I design evaluation metrics and test the effectiveness of Louvain algorithm in community detection using [datasets](https://snap.stanford.edu/data/index.html#communities) with ground-truth communities.



## How to Run this Project?

1. **Run Louvain Algorithms to Get Clusters**

```bash
python main.py
```

- **Input**: Undirected networks in `data/com-*.ungraph.txt`.
- **Output**: Clustering results in ``data/\*_clusters.txt``.

2. **Evaluate Clustering Results Based on Ground-Truth Communities**

```bash
python evaluater.py
```

- **Input**: Ground-truth communities in ``data/com-\*.all.cmty.txt`` and ``data/com-\*.top5000.cmty.txt`` & Clustering results in ``data/\*_clusters.txt``. 
- **Output**: Evaluation scores recorded in ``data/log.txt``.

3. **Visualization**

```bash
python drawer.py
```

- This script demonstrates the score dynamics of Louvain clustering results.



