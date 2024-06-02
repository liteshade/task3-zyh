import  random
import re
import networkx as nx
import heapq
import copy
import threading
import time


class Graph():
    def __init__(self, directed=True):
        self.directed = directed
        self.edges = {}
        self.nodes = set()  # 追踪图中的节点
        self.highlight_edges = {} #需要高亮的特殊边
        self.highlight_nodes = {} #需要高亮的特殊点
        self.return_as_subthread = None #作为子线程时的返回值
        self.color_list = ['red','yellow','orange','blue','purple','green']
        
        
    #查询是否为邻居节点  
    def __is_neighbor__(self,node1,node2):
        if(node1,node2) in self.edges:
            return True
        else:
            return False         
    
    #查找邻居节点
    def __find_neighbor_and_weight__(self,node1):
        neighbors = {}
        for neighbor_node in self.nodes:
            edge_key = (node1,neighbor_node)
            if edge_key in self.edges:
                neighbors[neighbor_node] = self.edges[edge_key]
        return neighbors
    
        #查找邻居节点
    def __find_neighbor__(self,node1):
        neighbors = []
        for neighbor_node in self.nodes:
            edge_key = (node1,neighbor_node)
            if edge_key in self.edges:
                neighbors.append(neighbor_node)
        return neighbors

    def add_edge(self, node1, node2, weight):
        # 根据节点1和节点2组成的元组作为键，权重作为值存储边的信息
        key = (node1, node2)
        if key in self.edges:
            # 如果边已经存在，增加其权重
            self.edges[key] += weight
        else:
            self.edges[key] = weight
            # 如果是有向图，添加节点1和节点2到图中
            self.nodes.add(node1)
            self.nodes.add(node2)

    #打印边
    def print_edge_list(self):
        for i, (edge, weight) in enumerate(self.edges.items(), 1):
            print(f'边 {i}: {edge[0]} -> {edge[1]} : 权重 {weight}')

    # 打印节点数目
    def print_number_of_nodes(self):
        num_of_nodes = len(self.nodes)
        print(f"节点数目: {num_of_nodes}")

    #查询桥接词语
    def query_bridge_words(self, word1, word2):
        if word1 not in self.nodes or word2 not in self.nodes:
            print(f"No {word1} or {word2} in the graph!")
            return

        bridge_words = []
        for node in self.nodes:
            if (word1, node) in self.edges and (node, word2) in self.edges:
                bridge_words.append(node)

        if not bridge_words:
            print(f"No bridge words from {word1} to {word2}!")
        elif len(bridge_words)==1:
            bridge_words_str = bridge_words[0]
            print(f"The bridge words from {word1} to {word2} is: {bridge_words_str}.")
        else:
            bridge_words_str = ", ".join(bridge_words)
            print(f"The bridge words from {word1} to {word2} are: {bridge_words_str}.")

    # 生成新文本并插入桥接词
    def generate_new_text(self, text):
        words = re.findall(r'\b\w+\b', text.lower())
        new_text = []

        for i in range(len(words) - 1):
            word1 = words[i]
            word2 = words[i + 1]

            bridge_words = []
            #查找桥接词语
            for node in self.nodes:
                if (word1, node) in self.edges and (node, word2) in self.edges:
                    bridge_words.append(node)

            new_text.append(word1)
            if bridge_words:
                new_text.append(random.choice(bridge_words))

        new_text.append(words[-1])
        return ' '.join(new_text)

    # 创建图对象，以便打印
    def create_networkx_graph(self):
        G = nx.DiGraph() if self.directed else nx.Graph()
        for edge, weight in self.edges.items():
            node1, node2 = edge
            color = self.highlight_edges[(node1, node2)] if (node1,node2) in self.highlight_edges else 'black'
            G.add_edge(node1, node2, weight=weight,color=color)
        for node in G.nodes:
            G.nodes[node]['color'] = self.highlight_nodes[node] if node in self.highlight_nodes else 'skyblue'
        return G
    
    #求两点之间最短路径，dijkstra
    def query_min_distance(self, word1, word2):
        is_word2_null = False
        
        if word2 == "":
            word2_list = [word for word in self.nodes if word != word1]
            is_word2_null = True
        elif word2 == word1:
            return 0
        elif word2 in self.nodes:
            word2_list = [word2]
        else:
            print(f"No {word2} in the graph!")
            
        if word1 not in self.nodes:
            print(f"No {word1} in the graph!")
            return
        min_shortest_path = float('infinity')
        
        #保存每个节点的最短距离
        for word2 in word2_list:
            distances = {vertex: float('infinity') for vertex in self.nodes}
            distances[word1] = 0
            # 优先队列
            priority_queue = [(0, word1,[])]
            this_word_dis_found = False
            min_shortest_path = float('infinity')
            now_color = 0
            step_count = 0
            
            while priority_queue:
                current_distance, current_vertex,current_front = heapq.heappop(priority_queue)
                step_count += 1
                if current_vertex == word2:
                    if current_distance <= min_shortest_path:
                        min_shortest_path = current_distance
                        
                        #将前序节点写入高亮边中
                        for i in range(len(current_front) - 1):
                            this_edge = (current_front[i],current_front[i+1])
                            self.highlight_edges[this_edge] = self.color_list[now_color]
                        end_edge = (current_front[-1],current_vertex)
                        self.highlight_edges[end_edge] = self.color_list[now_color]
                        now_color += 1
                        if now_color > 5:
                            now_color = 0
                        this_word_dis_found = True
                        
                        if is_word2_null:
                            path_chain = "→".join(current_front) + "→" + current_vertex
                            print("节点“{}”到节点“{}”的路径为：{}，路径长度为{} ".format(word1,word2,path_chain,current_distance))
                            break
                    else:
                        return min_shortest_path
                    
                #防止出现回环
                if current_distance > distances[current_vertex]:
                    continue
                
                # 开始扩张节点
                for neighbor, weight in self.__find_neighbor_and_weight__(current_vertex).items():
                    distance = current_distance + weight
                    new_front = copy.deepcopy(current_front)
                    new_front.append(current_vertex)
                    # 更新距离
                    if distance <= distances[neighbor]:
                        distances[neighbor] = distance
                        heapq.heappush(priority_queue, (distance, neighbor,new_front))
                    
            if is_word2_null:
                if not this_word_dis_found:
                    print("没有找到节点“{}”到节点“{}”的路径！".format(word1,word2))
            else:
                if not this_word_dis_found:
                    return None
                return min_shortest_path
                    
    def random_walk(self,word1=None):
        if word1 == None:
            nl = list(self.nodes)
            word1 = random.choice(nl)
            self.highlight_nodes[word1] = 'red'
            return word1
        neighbors = self.__find_neighbor__(word1)
        if len(neighbors) == 0:
            return None
        else:
            #去除已经高亮的节点
            neighbors = set(neighbors) - set(self.highlight_nodes.keys())
            if len(neighbors) == 0:
                return None
            next_neighbor = random.choice(list(neighbors))
            self.highlight_nodes[next_neighbor] = 'red'
            return next_neighbor
            