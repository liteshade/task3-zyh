import re
import networkx as nx
import matplotlib.pyplot as plt
from graph import Graph
import threading
import time
from concurrent.futures import ThreadPoolExecutor

plt.rcParams['font.sans-serif']='SimHei'
plt.rcParams['axes.unicode_minus']=False
#进程通信全局变量
global_subprocess_finished = False

#读取文件并生成图
def generate_directed_graph(filename):
    global last_word, graph
    try:
        with open(filename, 'r') as file:
            for line in file:
                words = re.findall(r'\b\w+\b', line.lower())
                for word in words:
                    #防止回环
                    if last_word and last_word != word:
                        graph.add_edge(last_word, word, 1)
                    last_word = word
    except FileNotFoundError:
        print("文件未找到！")

#可视化图
def visualize_graph(directed_graph,filename):
    # 布置节点位置
    #plt.clf()  # 清除图形
    pos = nx.kamada_kawai_layout(directed_graph)
    edge_color = [directed_graph[u][v]['color'] for u,v in directed_graph.edges()]
    node_color = [directed_graph.nodes[node]['color'] for node in directed_graph.nodes]
    # 绘制图
    nx.draw(directed_graph, pos, with_labels=True, node_size=800, font_size=10,
            font_weight="bold",edge_color = edge_color, node_color = node_color,
            arrows=True, arrowsize=10, width=1.5, connectionstyle='arc3, rad=0.2')
    
    # 添加边上的权重标签
    edge_labels = {(u, v): directed_graph[u][v]['weight'] for u, v in directed_graph.edges()}
    nx.draw_networkx_edge_labels(directed_graph, pos, edge_labels=edge_labels, font_color='gray')
    plt.savefig("./saved_fig/graph_{}.png".format(round(time.time())))
    plt.show()  # 显示图
    #可视化图
    
#可视化图
def visualize_graph_animate(directed_graph):
    # 布置节点位置
    plt.clf()  # 清除图形
    pos = nx.kamada_kawai_layout(directed_graph)
    edge_color = [directed_graph[u][v]['color'] for u,v in directed_graph.edges()]
    node_color = [directed_graph.nodes[node]['color'] for node in directed_graph.nodes]
    # 绘制图
    nx.draw(directed_graph, pos, with_labels=True, node_size=800, font_size=10,
            font_weight="bold",edge_color = edge_color, node_color = node_color,
            arrows=True, arrowsize=10, width=1.5, connectionstyle='arc3, rad=0.2')
    
    # 添加边上的权重标签
    edge_labels = {(u, v): directed_graph[u][v]['weight'] for u, v in directed_graph.edges()}
    nx.draw_networkx_edge_labels(directed_graph, pos, edge_labels=edge_labels, font_color='gray')
    #plt.show()  # 显示图
    plt.draw()  # 重新绘制并刷新显示
    plt.pause(0.1)
    #可视化图
    
    
def visualize_graph_with_distance(directed_graph,word1,distance):
    # 布置节点位置
    
    pos = nx.kamada_kawai_layout(directed_graph)
    edge_color = [directed_graph[u][v]['color'] for u,v in directed_graph.edges()]
    node_color = [directed_graph.nodes[node]['color'] for node in directed_graph.nodes]
    
    # 绘制图
    nx.draw(directed_graph, pos, with_labels=True, node_size=800, font_size=10,
            font_weight="bold", edge_color = edge_color, node_color = node_color,
            arrows=True, arrowsize=10, width=1.5, connectionstyle='arc3, rad=0.2')
    
    # 添加边上的权重标签
    edge_labels = {(u, v): directed_graph[u][v]['weight'] for u, v in directed_graph.edges()}
    nx.draw_networkx_edge_labels(directed_graph, pos, edge_labels=edge_labels, font_color='gray')
    text = '最短距离：{}'.format(distance)
    plt.text(pos[word1][0]+0.2,pos[word1][1], text, fontsize=12, ha='center', va='center', color='red')
    plt.show()  # 显示图
    
def live_delay():
    start_time = time.time()
    global global_subprocess_finished
    while time.time() - start_time < 0.5:
        #检测终止变量是否变化
        if global_subprocess_finished:
            plt.ioff()
            #防止突然关闭plt导致报错
            plt.switch_backend("agg")
            return True #中断退出
    return False
        
def random_walk_subprocess():
    plt.ion()  # 开启交互式模式
    thisword = None
    wordlist = []
    while(1):
        directed_graph = graph.create_networkx_graph()
        #visualize_graph_animate(directed_graph)
        thisword = graph.random_walk(word1=thisword)
        wordlist.append(thisword)
        if thisword == None:
            if live_delay():
                with open("save.txt","w",encoding="utf-8") as f:
                    f.write(" ".join(wordlist))
                return
            #visualize_graph_animate(directed_graph)
            plt.ioff()
            plt.switch_backend("agg")
            file = open('save.txt', 'w')  # 写入模式，如果文件存在则覆盖
            file.write(" ".join(wordlist[:-1]))
            file.close()
            print("线程正常终止！")
            return
        else:
            if live_delay():
                with open("save.txt","w",encoding="utf-8") as f:
                    f.write(" ".join(wordlist))
                return

if __name__ == "__main__":
    filename = "file/test2.txt"  # 文件名
    graph = Graph()  # 创建一个有向图对象
    last_word = None  # 初始化最后一个单词为空
    generate_directed_graph(filename)  # 生成有向图
    # 创建 NetworkX 图对象
    n = int(input("请输入功能序号： "))
    if n==2 :
        directed_graph = graph.create_networkx_graph()
        visualize_graph(directed_graph,filename)
    elif  n==3:
        print(3)
        word1 = input("请输入第一个单词: ")
        word2 = input("请输入第二个单词: ")
        graph.query_bridge_words(word1, word2)
    elif n==1:
        graph.print_edge_list()  # 打印边和节点
        graph.print_number_of_nodes()  # 打印节点数目
    elif n == 4:
        print(4)
        # 处理新文本
        new_text = input("请输入一行新文本: ")
        result_text = graph.generate_new_text(new_text)
        print("处理后的新文本: ")
        print(result_text)
    elif n == 5:
        print(5)
        #查找最短路径
        word1 = input("请输入第一个单词: ")
        word2 = input("请输入第二个单词，如果只输入第一个单词输入'enter':")
        current_distance = graph.query_min_distance(word1,word2)
        if current_distance != None:
            directed_graph = graph.create_networkx_graph()
            visualize_graph_with_distance(directed_graph,word1,current_distance)
        
    elif n == 6:
        print(6)
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(random_walk_subprocess)
        user_input = input("Enter终止。。。")
        print("用户终止线程！")
        global_subprocess_finished = True
        
        future.cancel()
        # 关闭线程池
        executor.shutdown(wait=False)
        print("线程池已经关闭！")
            
    else:
        print("请输入正确的序号！")
