# Community Detection实验报告

​																																	王颖 2301111962

**一、Louvain算法实现**

​	我在``louvain.py``的Louvain类中实现了Louvain算法。

该类包含以下成员变量：

```python
self.original_graph 	# 实例的原始输入（一个networkx.Graph类的图）
self.graph 				# local improvement的操作对象图
						# 可能是原图，也可能是community aggregation得到的新图
self.m 					# 图self.graph的边权和
self.community_ID 		# 一个mapping, 标明original_graph上每个点对应聚类标号
self.community_map 		# mapping, 标明当前图graph上的聚类标号
self.degree_sum			# mapping, 标明graph上每个聚类内的点度和
self.self_loop			# mapping, 标明graph上每个点的自环权重
```



类内包含以下函数：

```python
def __init__(self, G):				# 初始化

def local_improvement(self):		# 主步骤，返回当前轮次是否有对初始分类进行改动

def get_new_graph(self, graph, community_map):
    								# 构造新图，在主步骤后（如果当前有改动）调用
    
def get_new_community_map(self):	# 初始化community_map, degree_sum, self_loop
    								# 在输入和构造新图后调用

def get_clusters(self):				# 返回一个列表，列表描述当前划分，在主步骤后调用

def get_community_history(self):	# 返回算法中间过程产生的所有划分，在算法结束后调用
    
def run(self):						# 运行算法，在初始化后可调用 
```

 

- 部分实现细节：

  - $\Delta(i→ C(j))$的计算

    $\Delta(i→ C(j)) = \frac{1}{2m}[\delta(i,S_j) - \delta(i,S_i /\{i\})]$，其中

    ​	$S_x$定义为$\{u \in V(graph)\mid C(u) = C(x)\}$即当前图``self.graph``中点$x$所在的聚类

    ​	$\delta(i,S)$定义为$\sum_{x \in S}w(x,i) - \frac{k_i}{2m}\sum_{x\in S}{k_x}$

    为提高计算效率，在local improvement中，对每个点$i$，我先计算一个名为 ``neighbor_communities``的mapping来存储所有邻点所在类$S_j$和这些类与$i$的边权和$\sum_{x \in S}w(x,i)$。该过程的复杂度是$O(degree(i))$的。

    特别的，在我的代码实现中用函数``calculate_Q(node, community)``计算$2\delta(i,S)$。

    

  - 我的代码给出了无向图上的Louvain算法实现，原图和新图都是``networkx.Graph``类的元素

    ``networkx.Graph``是一个无向图类，尽管它允许自环，但类函数graph.degree(node) 在计算node的度时不会计入自环的权重。这导致我在代码实现中使用``self.self_loop	``存储每个点的自环权重。

    

  - 新图自环的边权应当是$w'(i,i) = \sum_{u:C(u) = i}\sum_{v: C(v) = i}w(u,v)$[^*]，**而不是**$\sum_{u,v}1[C(u) = C(v)=i]w(u,v)$（二者在有向图场景下是一致的，但在无向图中边$(u,v)$和边$(v,u)$是同一条，在求和中只出现一次）。

    <img src="E:\研究生\社会与市场中的计算问题选讲\code\example.png" alt="image-20240507165712902" style="zoom:60%;" />

    结合Louvain算法[原文](https://arxiv.org/pdf/0803.0476)中的示例（如上图），无向图场景下的自环和应当是$w'(i,i) = \sum_{u:C(u) = i}\sum_{v: C(v) = i}w(u,v)$，即$\sum_{u,v}1[C(u) = C(v)=i]\cdot \{w(u,v)*2 - w(u,v)\cdot 1[u=v]\}$。

  [^*]:见描述community aggregation的[论文](https://arxiv.org/pdf/physics/0702015)第三页公式(2.1)，文中给出的是有向图情形。



完整代码实现见github仓库[none44353/Community-Detection](https://github.com/none44353/Community-Detection)。



**二、评估、测试与分析**

**1、评价标准**

​	我设计了一种基于ground-truth communities的评价指标，它评估任意参数$k$（聚类数目）下的划分$\mathcal{S}$和任意一个（或多个）ground-truth community的契合程度。

​	给定单个ground truth community $C$，评分$G(\mathcal{S}, C) = k/|C|^2\cdot \sum_{S\in \mathcal{S}}{n_S(C)^2}$。

​	如果存在多个communities $\{C_1, C_2, \cdots, C_m\}$，评分为$C_i$评分的均值，即

​						$G(\mathcal{S}, \{C_1, C_2, \cdots, C_m\})= \frac{1}{m}\sum_{i = 1}^m G(\mathcal{S}, C)$。





- 设计思路：

​	从直觉上看，一个好的划分$\mathcal{S}$尽可能地把ground-truth community $C$中的点划分到一个类里。基于该直观的直接想法是：用类内的同属于ground-truth community的点对数目来衡量划分的好坏，即指标$f(\mathcal{S}, C)  = \sum_{S \in \mathcal{S}}|\{(u,v): u,v \in S\cap C\}|$。记点集$S$与community $C$的交集大小为 $n_S(C) = |\{u:u \in S\cap C\}|$，那么$f(\mathcal{S}, C)  = \sum_{S \in \mathcal{S}}\tbinom{n_S(C)}{2} = \frac{1}{2}\sum_{S\in \mathcal{S}}{n_S(C)^2} - \frac{|C|}{2}$。

​	上式的第二项至于community $C$的大小有关，相比之下，我们更关心第一项，即指标$g(\mathcal{S}, C) = \frac{1}{2}\sum_{S\in \mathcal{S}}{n_S(C)^2} $。

​	然而，指标$g$没有对齐不同参数$k$下的评估标准。$g$对聚类数目$k$更小的划分更友好：当划分$\mathcal{S}$把所有元素划分到一个点集（$\mathcal{S} = \{U\}$）时，指标$g(\mathcal{S}, C)$取到最大值$|C|^2/2$。

​	出于对齐的目的，引入参数$k$下的baseline划分方法：将全集$U$随机分成$k$个点集。该划分方法下，指标$g(\mathcal{S}, C)$的期望为 $\bar{g} =|C|^2/(2k)$。计算$g$与$\bar{g}$的比率，得到新的指标$G(\mathcal{S}, C) = k/|C|^2\cdot \sum_{S\in \mathcal{S}}{n_S(C)^2}$。

​	因为$g(\mathcal{S}, C) \ge \bar{g}$，指标$G$的取值范围为$[1, \infin)$。固定community $C$，$G(\mathcal{S}, C)$越靠近1，划分$\mathcal{S}$越接近于一个随机划分，契合度越差；$G(\mathcal{S}, C)$越大，划分$\mathcal{S}$越契合community $C$。



**2、测试与分析**

​	我选取了SNAP Networks with ground-truth communities中规模较小的4个无向图数据集：[com-DBLP](https://snap.stanford.edu/data/com-DBLP.html)、[com-Amazon](https://snap.stanford.edu/data/com-Amazon.html)、[com-Youtube](https://snap.stanford.edu/data/com-Youtube.html)、[com-LiveJournal](https://snap.stanford.edu/data/com-LiveJournal.html)进行测试。这些数据集的基本信息如下：

| Name                | # Nodes   | # Edges    | # Communities[^1] | Description                       |
| ------------------- | --------- | ---------- | ----------------- | --------------------------------- |
| **com-DBLP**        | 317,080   | 1,049,866  | 13,477            | DBLP collaboration network        |
| **com-Amazon**      | 334,863   | 925,872    | 75,149            | Amazon product network            |
| **com-Youtube**     | 1,134,890 | 2,987,624  | 16,386            | Youtube online social network     |
| **com-LiveJournal** | 3,997,962 | 34,681,189 | 664,414           | LiveJournal online social network |

[^1]: 本表中的Communities数目与[SNAP](https://snap.stanford.edu/data/index.html#communities)中的统计信息不一致，因为SNAP在统计时排除了所有节点数小于3的Communities。我在测试中没有排除这类Communities。即使Community $C$只由两个节点构成，算法在哪一次迭代后把这两个点聚到一个类里也可以反映其恢复能力。



- Louvain算法测评

  下表为Louvain算法结果的聚类数目（# Clusters）和平均聚类大小（Average Cluster Size）：

|                          | **com-DBLP** | **com-Amazon** | **com-Youtube** | com-LiveJournal |
| ------------------------ | ------------ | -------------- | --------------- | --------------- |
| **# Clusters**           | 569          | 234            | 19691           | 10111           |
| **Average Cluster Size** | 53.411       | 30.227         | 7.885           | 10.789          |

com-Youtube和com-LiveJournal数据的平均聚类大小较小，平均每个聚类中不超过11个点。



​	下表为Louvain的划分结果$\mathcal{S}$在所有ground-truth communities上的平均评分$G$，以及其在质量最高[^2]的5000个communities上的评分。在com-Youtube和com-LiveJournal数据集上，top 5000 communities和聚类结果的契合度相比于全体ground truth communities更高；在com-DBLP和com-Amazon数据集上，top 5000 communities和聚类结果的契合度相比于所有数据集更高。

[^2]: 高质量的定义参考Yang和Leskovec的[论文](https://link.springer.com/article/10.1007/s10115-013-0693-z)，它根据communities在6项指标（Conductance, TPR, Modularity, Flake ODF, FOMD, Cut Ratio）上的平均排名确定。

|                                             | **com-DBLP** | **com-Amazon** | **com-Youtube** | com-LiveJournal |
| ------------------------------------------- | ------------ | -------------- | --------------- | --------------- |
| **Score with All Ground-Truth Communities** | **1.757**    | **1.190**      | 1.173           | 1.130           |
| **Score with Top 5000 Communities**         | 1.191        | 1.005          | **1.355**       | **1.199**       |

​	

​	下图是Louvain算法在各轮主步骤（local improvement）局部优化后得到的划分$\mathcal{S}_t$的评分。每张子图对应一个数据集上Louvain算法的聚类表现动态，实线对应划分$\mathcal{S}_t$在全体ground-truth communities上的平均评分，点线对应划分$\mathcal{S}_t$在top 5000 communities上的平均评分。灰色的虚线为划分$\mathcal{S}_t$的聚类数目的对数（以自然底数$e$为底）$\ln|\mathcal{S}_t|$，括号内标注的数字是聚类数目$|\mathcal{S}_t|$。

![scores](E:\研究生\社会与市场中的计算问题选讲\code\scores.png)

评价指标$G$随着迭代优化的轮次$t$上升而下降。由于Louvain算法中的划分$\mathcal{S}_t$一定是$\mathcal{S}_{t-1}$的一个粗化，指标$g(\mathcal{S_t}, C)$随着$t$的增加而升高，baseline指标$\bar{g}_t$也随着$t$的增加而升高。$G(\mathcal{S}_t, C) = g(\mathcal{S_t}, C)/\bar{g}$ 的下降表明指标$g(\mathcal{S_t}, C)$的上升曲线相比更$\bar{g}_t$平缓，平均来说，Louvain算法率先把同时在ground-truth communities里的点聚合起来。



**算法没能精确恢复的部分**

​	评分表和评分动态图表明算法没能精确恢复的部分存在差异性：在com-Youtube和com-LiveJournal数据集上，算法没能精确恢复low quality communities；在com-DBLP和com-Youtube数据集上，算法没能精确恢复high quality communities。

​	由于quality基于communities在6项指标（Conductance, TPR, Modularity, Flake ODF, FOMD, Cut Ratio）上的平均排名确定，需要进一步分析不同数据集上6项指标的分布特征来确定影响算法恢复性能的核心指标（e.g. 算法在X指标较大的数据上恢复能力差）。

​	潜在改进思路：修改主步骤的优化目标为Modularity和核心指标X的线性组合，来提升算法在X指标较大的Communities上的恢复能力。

