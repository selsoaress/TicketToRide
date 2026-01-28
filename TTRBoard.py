import networkx as nx
import pandas as pd
import numpy as np
import pylab


board = "north_america" # will be set by default
board_data = pd.read_csv("boards/" + board)

color_map = {'Todos': 'grey', # setting translations from Portuguese to English
              'Vermelha': 'red',
              'Azul': 'blue',
              'Laranja': 'orange',
              'Roxa': 'purple',
              'Branca': 'white',
              'Preto': 'black',
              'Verde': 'green',
              'Amarelo': 'yellow'}

class Board(object):
    def __init__(self):
        self.board_graph = nx.Graph()
        self.cities = np.unique(board_data[['city_a', 'city_b']].values)

        for city in self.cities:
            self.board_graph.add_node(city)

        for index, edge in board_data.iterrows():
            self.board_graph.add_edge(edge['city_a'], 
                                      edge['city_b'],
                                      cost = edge['cost'],
                                      color = edge['color'])
            
    
        #create a copy of the board to store the original state of the board
        self.copyBoard = self.board_graph.copy()
        
    def showBoard(self, board, pauseTime = 7):
        """display board
        """
        pos=nx.spring_layout(board)
        nx.draw(board, pos)
        nx.draw_networkx_edge_labels(board, pos)
        pylab.ion()
        pylab.show()
        pylab.pause(pauseTime)
        pylab.close()
    
    def hasEdge(self, city1, city2):
        """returns True an edge exists between city1, city2.  False otherwise
        city1, city2: string
        """
        return self.board_graph.has_edge(city1, city2)

    def removeEdge(self, city1, city2, edgeColor):
        """remove the edge between two cities that's colored edgeColor
        city1, city2:  string
        edgeColor:  string
        raises ValueError if edge does not exist
        """
        if not self.hasEdge(city1, city2):
            raise ValueError("Edge between %s and %s does not exist" 
                                % (city1, city2))
        
        posColors = self.getEdgeColors(city1, city2)
        
        #if the edge is grey, accept any color and remove grey
        if "grey" in posColors:
            self.board_graph.get_edge_data(city1, city2)['edgeColors'].remove("grey")
            if len(self.board_graph.get_edge_data(city1, city2)['edgeColors']) == 0:
                self.board_graph.remove_edge(city1, city2)
            
        else:
            if edgeColor not in posColors:
                raise ValueError("A %s edge does not exist between %s and %s" 
                                    % (edgeColor, city1, city2))
            
            #if edge has a color, remove that color
            self.board_graph.get_edge_data(city1, city2)['edgeColors'].remove(edgeColor)
            if len(self.board_graph.get_edge_data(city1, city2)['edgeColors']) == 0:
                self.board_graph.remove_edge(city1, city2)
            
    def getEdges(self):
        """returns a list of tuples of all remaining edges', [(city1, city2)]
        """
        return self.board_graph.edges()

    def getEdgeColors(self, city1, city2):
        """returns the edgeColors of edge
        city1, city2: string
        """
        return self.board_graph.get_edge_data(city1, city2)['edgeColors']

    def getEdgeWeight(self, city1, city2):
        """returns the weight of the edge (i.e. the distance between two cities)
        city1, city2: string
        """
        return self.board_graph.get_edge_data(city1, city2)['weight']
    
    def getPathWeight(self, city1, city2):
        """returns the weight of the shortest path between city1, city2
        """
        return nx.dijkstra_path_length(self.G, city1, city2)
    
    def getNodes(self):
        return self.board_graph.nodes()

    def getCities(self):
        """returns a list of all remaining cities
        that can be traveled to or from
        """
        return self.board_graph.nodes()
    
    def getAdjCities(self, city1):
        """returns a list of cities adjacent to city1 
        that still have available edges
        """
        return [x[1] for x in self.board_graph.edges(city1)]
        
    def hasPath(self, city1, city2):
        """returns True if a path exists between city1 and city2
        searches self.G (the graph the class uses)
        city1, city2: String
        """
        return nx.has_path(self.G, city1, city2)
    
    def iterEdges(self):
        """returns an interator over all edges and edge data"""
        return self.board_graph.edges_iter(data = True)
        
class PlayerBoard(Board):
    """Creates a custom graph for each player to represent their progress"""
    def __init__(self):
        self.G = nx.Graph()
    
    def addEdge(self, city1, city2, routeDist, color):
        """
        city1, city2, color: Strings
        routeDist          : int
        """
        self.board_graph.add_edge(city1, city2, weight = routeDist, edgeColors = [color])

    def longestPath(self, start):
        """returns a tuple: (len longestPath, tuple of cities along longestPath)
        This is a modification of BFS that uses edges instead of nodes
        It has no ending condition, rather it searches the whole graph and
        returns the weight of the longest path and the edges that of that path

        #Doctest

        >>> p = PlayerBoard()
        >>> p.addEdge('a', 'b', 1, 'blue')
        >>> p.addEdge('b', 'd', 1, 'blue')
        >>> p.addEdge('d', 'e', 1, 'blue')
        >>> p.addEdge('e', 'f', 98, 'blue')
        >>> p.addEdge('e', 'b', 1, 'blue')
        >>> p.addEdge('b', 'c', 1, 'blue')
        >>> p.addEdge('a', 'z', 1, 'blue')
        
        >>> p.longestPath('b')
        (100, (['b', 'd', 'e', 'f'], set([('d', 'e'), ('e', 'f'), ('b', 'd')])))
        
        # if p.addEdge('e', 'f', 1, 'blue')
        # (5, (['b', 'd', 'e', 'b', 'a', 'z'], \
        #    set([('b', 'a'), ('d', 'e'), ('a', 'z'), ('e', 'b'), ('b', 'd')])))

        """
        
        longestPath = (0, ())
        q = []
        
        q.append( ([start], set()) ) #( [path], set(exploredEdges) )
        
        while q:
            cur = q.pop() #pop() = DFS, pop(0) = BFS (consider Deque for O(1))
            
            if len(cur[1]) > 0:
                pathWeight = sum( [self.getEdgeWeight(x[0],x[1]) 
                                    for x in cur[1]] )
            
                if pathWeight > longestPath[0]:
                    longestPath = (pathWeight, cur)
            
            node = cur[0][-1]
            edgesExplored = cur[1]
            adjCities = set()
            for i in self.getAdjCities(node):
                #add if edge between cities not explored
                if (node, i) not in edgesExplored:
                    if (i, node) not in edgesExplored:
                        adjCities.add(i) 
            
            for suc in adjCities:
                proxy = cur[1].copy()
                proxy.add((node, suc))
                newPath = cur[0] + [suc]

                q.append((newPath, proxy)) #add to path, add edge
                    
        
        #Note: set of path edges will not be ordered
        return longestPath        

if __name__ == "__main__":
    import doctest
    doctest.testmod()