#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  9 23:37:16 2019

@author: frankchao
AI introduction ntpu 2019
"""

"""
Please use the following search algorithms to solve the 15-puzzle problem.
(a) Iterative-Deepening Search (IDS)
(b) Uniform-Cost Search
(c) Greedy Best-First Search
(d) A* search
(e) Recursive Best-First Search (RBFS)
Input： A state of random layout of 1, 2, 3, …, 15, blank.

goal state

 1  2  3 4
12 13 14 5
11 15  * 6
10  9  8 7

Output for each algorithm：
(a) The number of movements (state changes) from the initial state to the goal state.
(b) The maximum number of states ever saved in the memory during the process.

explain the strategy
"""

import gc
import numpy as np

frontier=[]                 
expanded_node=[]           # 正在展開的state
state_changes=0            # 記錄展開過多少個state
MaxnumState=0              # maximun number of states ever saved in memory
find=False                 # 如果找到goal,find = True
Rbfsmax=0                  # 記錄rbfs最多的記憶的node
goal=None          

def moves(matrix,direction):
    output=[]
    matrix=np.array(matrix,dtype=np.str)
    if matrix.shape!=(4,4):
       matrix=matrix.reshape(4,4)
    for ii in range(4):
        for jj in range(4):
            if matrix[ii][jj]=='*':
                i=ii
                j=jj
    if i>0 and direction=='up':                        #move up 
        tempt=matrix[i-1][j]
        matrix[i-1][j]=matrix[i][j]  
        matrix[i][j]=tempt
        output.append(matrix)
    if i<3 and direction=='down':                      #move down
        tempt=matrix[i+1][j]
        matrix[i+1][j]=matrix[i][j]  
        matrix[i][j]=tempt
        output.append(matrix)
    if j<3 and direction=='right':                     #move right
        tempt=matrix[i][j+1]
        matrix[i][j+1]=matrix[i][j]  
        matrix[i][j]=tempt    
        output.append(matrix)
    if j>0 and direction=='left':                      #move left
        tempt=matrix[i][j-1]
        matrix[i][j-1]=matrix[i][j]  
        matrix[i][j]=tempt    
        output.append(matrix)
    if output==[]:
        return 0
    else:
        return output                                 #更新後的state

def heuristic(Node):
    '''
    使用 Manhattan distance 做為 g(n)
    '''
    distance=0
    #建表 代表goal＿state位置
    table={(2,2):'*',(0,0):'1',(0,1):'2',(0,2):'3',(0,3):'4',(1,3):'5',(2,3):'6',(3,3):'7',
           (3,2):'8',(3,1):'9',(3,0):'10',(2,0):'11',(1,0):'12',(1,1):'13',(1,2):'14',(2,1):'15'}
    table1={'*':(2,2),'1':(0,0),'2':(0,1),'3':(0,2),'4':(0,3),'5':(1,3),'6':(2,3),'7':(3,3),
           '8':(3,2),'9':(3,1),'10':(3,0),'11':(2,0),'12':(1,0),'13':(1,1),'14':(1,2),'15':(2,1)}
    for i in range(4):
        for j in range(4):
            Node.state=np.array(Node.state,dtype=np.str)
            if Node.state.shape!=(4,4):
               Node.state=Node.state.reshape(4,4)
            if Node.state[i][j]=='*': continue
            if Node.state[i][j]==table[(i,j)]:
                continue
            else:                               #Manhattan distance
                distance+=abs(table1[Node.state[i][j]][0]-i)+abs(table1[Node.state[i][j]][1]-i)                  
    return distance        

class Node:

    def __init__(self,state,level):
        self.state = state        #一個state
        self.expanded = False     #被展開過 = True
        self.children = []        #加入展開後的子state
        self.parent=[]            #父節點(state)
        self.level=level          #紀錄它是第幾層
        self.keep=None            #(rbfs)
        self.value=None           #(rbfs)
    
    def add_children(self):       #加入children
        
        if moves(self.state,'right')!=0:
            right=Node(moves(self.state,'right'),self.level)
            self.children.append(right)                         #加入子節點 
            right.parent.append(self.state)                     #記錄父節點
            right.level+=1
        if moves(self.state,'left')!=0:
            left=Node(moves(self.state,'left'),self.level)
            self.children.append(left)
            left.parent.append(self.state)                     
            left.level+=1
        if moves(self.state,'down')!=0:    
            down=Node(moves(self.state,'down'),self.level)
            self.children.append(down)
            down.parent.append(self.state)
            down.level+=1
        if moves(self.state,'up')!=0:        
            up=Node(moves(self.state,'up'),self.level)
            self.children.append(up)
            up.parent.append(self.state)
            up.level+=1
         
    def __repr__(self):          
        return str(self.state)    #print會印出state
    
    
class Iterative_Deepening_Search:
    
    '''
    IDS Algorithm
    LIFO 先加入的後展開-> 加入順序 右左下上(進入frontier的順序)
    node展開的順序為上下左右(*往上的state先展開 再來*往下的state ...)
    goal test when insert
    
    '''
    delete=0
    def __init__(self,initial,goal):
        global find
        self.start=initial
        self.goal=goal
        find=self.stack()             #如果找到goal,find會被改成true
        
    def add_frontier(self):
        global frontier
        global expanded_node
        global state_changes
        start = self.start
        if (start.state==self.goal).all():   #如果找到goal
            path=[]
            path.append(start)  
            while start.parent!=[]:          #找它的parent,直到initial
                for ii in range(0,len(expanded_node)):
                    if (np.array(expanded_node[ii].state).reshape(4,4)==np.array(start.parent).reshape(4,4)).all():
                       path.append(expanded_node[ii])
                       break
                start=expanded_node[ii]
            path.reverse()    
            for j in range(0,len(path)):
                if isinstance(path[j].state,np.ndarray)!=True:
                    path[j].state=np.array(path[j].state).reshape(4,4)
                print('move:',j)
                print(path[j])
            return True   
        frontier.append(start)               #沒找到goal,則加入forntier
        
    def stack(self):
        '''
        stack 後進先出
        因此把forntier由後展開
        並把展開的state從frontier刪除
        並把展開state的children加入frontier
        '''
        global frontier
        global expanded_node
        global MaxnumState
        global state_changes
        expanded_node.append(frontier[-1])             #展開frontier[-1]
        state_changes+=1                               #每展開一個frontier,state_change就加1
        del frontier[-1]
        expanded_node[-1].expanded = True
        expanded_node[-1].add_children()
        for n in expanded_node[-1].children:           #把展開state的children加入frontier
            if not n.expanded:
               self.start=n
               f=self.add_frontier()
               if len(expanded_node)+len(frontier)>MaxnumState:  #記錄maxnumstate           
                   MaxnumState=len(frontier)+len(expanded_node)  
               if f==True:                                       #如果在add_frontier過程中找到goal,f會＝true
                 return f   
       


class Uniform_Cost_Search:
    movement=[]                         #記錄最多有幾個node
    def __init__(self,initial,goal):
       global find
       self.start=initial
       self.goal=goal
       find=self.priority_queue()
       
       
    def add_frontier(self):
        global frontier
        global expanded_node
        start = self.start
        frontier.append(start)
        Uniform_Cost_Search.movement.append(start)   #多一個frontier,movement就加1
        
    def pop_off(self): 
        global frontier
        global expanded_node
        global state_changes
        if (frontier[0].state==self.goal).all():    #在pop_off的時候才做goal test
            path=[]
            path.append(frontier[0])  
            start=frontier[0]
            while start.parent!=[]:   
                for ii in range(0,len(expanded_node)):
                    if (np.array(expanded_node[ii].state).reshape(4,4)==np.array(start.parent).reshape(4,4)).all():
                       path.append(expanded_node[ii])
                       break
                start=expanded_node[ii]
            path.reverse()    
            for j in range(0,len(path)):
                if isinstance(path[j].state,np.ndarray)!=True:
                    path[j].state=np.array(path[j].state).reshape(4,4)
                print('move:',j)
                print(path[j])
            return True   
        else:
            expanded_node.append(frontier[0]) #先進先出
            state_changes+=1
            del frontier[0]
        
    def priority_queue(self):
        '''
        Uniform-cost Algorithm
        step cost(n)=1, for all n
        在此設定state和state間的step cost都是1 , 因此會和BFS的結果相當
        node展開的順序為右左下上(*往右的state先展開 再來*往左的state ...)
        goal test when pop off
        
        '''
        global frontier
        global expanded_node
        global MaxnumState
        f=self.pop_off()          #測試要expand的node是不是goal
        if f==True:
            return f    
        expanded_node[-1].expanded = True     #不是的話就展開
        expanded_node[-1].add_children()
        for n in expanded_node[-1].children:
            if not n.expanded:
               self.start=n
               self.add_frontier()
              

class Geedy_Bestfirst_Search:
    movement=[]                         #記錄最多有幾個node
    def __init__(self,initial,goal):
        global find
        self.start=initial
        self.goal=goal
        find=self.greedy()
         
    def add_frontier(self):                  #在加入fontier時做goal-test
        global frontier
        global expanded_node
        start = self.start
        if (start.state==self.goal).all():   #如果找到goal
            path=[]
            path.append(start) 
            Geedy_Bestfirst_Search.movement.append(start)
            while start.parent!=[]:          #找它的parent,直到initial
                for ii in range(0,len(expanded_node)):
                    if (np.array(expanded_node[ii].state).reshape(4,4)==np.array(start.parent).reshape(4,4)).all():
                       path.append(expanded_node[ii])
                       break
                start=expanded_node[ii]
            path.reverse()    
            for j in range(0,len(path)):
                if isinstance(path[j].state,np.ndarray)!=True:
                    path[j].state=np.array(path[j].state).reshape(4,4)
                print('move:',j)
                print(path[j])
            return True   
        frontier.append(start)
        Geedy_Bestfirst_Search.movement.append(start)
        
    def greedy(self):
        
        '''
        Greedy best-first search Algorithm
        h(n)使用heuristic中的定義，也就是Manhattan distance
        當h(n)相同時，先加入frontier的先展開
        h(n)為0時，為solution
        '''
        global frontier
        global expanded_node
        global MaxnumState
        global state_changes
        gmin=100000
        for k in range(0,len(frontier)):           #在frontier中,找h(n)最小者展開
            g=heuristic(frontier[k])
            if g<gmin:
                add=k
                gmin=g
        expanded_node.append(frontier[add])
        state_changes+=1
        del frontier[add]
        expanded_node[-1].expanded = True
        expanded_node[-1].add_children()
        for n in expanded_node[-1].children: 
            if not n.expanded:
               self.start=n
               f=self.add_frontier()
               if f==True:                       #如果在add_frontier過程中找到goal,f會＝true
                 return f 
       

class Astar:
    movement=[]                              #記錄最多有幾個node
    def __init__(self,initial,goal):
        global find
        self.start=initial
        self.goal=goal
        find=self.astar()
         
    def add_frontier(self):                  #在加入fontier時做goal-test
        global frontier
        global expanded_node
        start = self.start
        if (start.state==self.goal).all():   #如果找到goal
            path=[]
            path.append(start) 
            Astar.movement.append(start)
            while start.parent!=[]:          #找它的parent,直到initial
                for ii in range(0,len(expanded_node)):
                    if (np.array(expanded_node[ii].state).reshape(4,4)==np.array(start.parent).reshape(4,4)).all():
                       path.append(expanded_node[ii])
                       break
                start=expanded_node[ii]
            path.reverse()    
            for j in range(0,len(path)):
                if isinstance(path[j].state,np.ndarray)!=True:
                    path[j].state=np.array(path[j].state).reshape(4,4)
                print('move:',j)
                print(path[j])
            return True   
        frontier.append(start)
        Astar.movement.append(start)
        
    def astar(self):
        
        '''
        Astar_Search Algorithm
        f(n)=g(n)+h(n)
        g(n)的step cost均為1
        h(n)使用heuristic中的定義，也就是Manhattan distance
        當f(n)相同時，先加入frontier的先展開
        f(n)為0時，為solution
        '''
        global frontier
        global expanded_node
        global MaxnumState
        global state_changes
        fmin=100000
        for k in range(0,len(frontier)):           #在frontier中,找f(n)最小者展開
            g=heuristic(frontier[k])               #g為heuristic
            f=g+frontier[k].level                  #frontier[k].level=actual cost 因step cost均為1
            if f<fmin:
                add=k
                fmin=f
        expanded_node.append(frontier[add])
        state_changes+=1
        del frontier[add]
        expanded_node[-1].expanded = True
        expanded_node[-1].add_children()
        for n in expanded_node[-1].children: 
            if not n.expanded:
               self.start=n
               f=self.add_frontier()
               if f==True:                       #如果在add_frontier過程中找到goal,f會＝true
                 return f 
class Rbfs:
    movement=[]                              #記錄有幾個node
    def __init__(self,initial,goal):
        global find
        self.start=initial
        self.goal=goal
        find=self.rbfs()
         
    def add_frontier(self):                  #在加入fontier時做goal-test
        global frontier
        global expanded_node
        global Rbfsmax
        start = self.start
        frontier.append(start)
        Rbfs.movement.append(start)          #frontier多1,Rbfs.movement就多1
        if len(Rbfs.movement)>Rbfsmax:       #Rbfsmax記錄最多的node數目
           Rbfsmax=len(Rbfs.movement)
        goal=Rbfs.goal_test(self.goal)       #goal test
        if goal==True:
            return True

    
    @classmethod    
    def goal_test(cls,goal):
        global frontier
        global expanded_node
        global MaxnumState
        global Rbfsmax
        for ii in range(0,len(frontier)):
            if (frontier[ii].state==goal).all():          #如果找到goal
                start=frontier[ii]
                path=[]
                path.append(start) 
                Rbfs.movement.append(start)
                if len(Rbfs.movement)>Rbfsmax:
                    Rbfsmax=len(Rbfs.movement)
                while start.parent!=[]:                        #找它的parent,直到initial
                    for ii in range(0,len(expanded_node)):
                        if (np.array(expanded_node[ii].state).reshape(4,4)==np.array(start.parent).reshape(4,4)).all():
                             path.append(expanded_node[ii])
                             break
                    start=expanded_node[ii]
                path.reverse()    
                for j in range(0,len(path)):
                    if isinstance(path[j].state,np.ndarray)!=True:
                        path[j].state=np.array(path[j].state).reshape(4,4)
                    print('move:',j)
                    print(path[j])
                return True
           
    def rbfs(self):
        
        
        '''
        Recursive Best-First Search (RBFS)
        f(n)=g(n)+h(n)
        g(n)的step cost均為1
        h(n)使用heuristic中的定義，也就是Manhattan distance
        記住次好的goal,轉換時忘掉
        '''
        global frontier
        global expanded_node
        global MaxnumState
        global Rbfsmax
        global state_changes
        if len(frontier)==1 and frontier[-1].level==0 :        #第一次的時候直接展開
            expanded_node.append(frontier[-1])
            state_changes+=1
            del frontier[-1]
            expanded_node[-1].expanded = True
            expanded_node[-1].add_children()
            for n in expanded_node[-1].children: 
              if not n.expanded:
                self.start=n
                f=self.add_frontier()
                if f==True:
                  return True      
            return None                    
        for m in expanded_node[-1].children:                  #如果沒找到goal
           if m.value==None:
              g=heuristic(m)                                  #記錄children的f(n)
              f=g+m.level    
              m.value=f 
        def fsort(x):                                         
             return x.value      
        expanded_node[-1].children.sort(key=fsort)            #按照children的f(n)值排序,最小的在第一個
        fmin=expanded_node[-1].children[0].value  
        fsecond=expanded_node[-1].children[1].value          
        add=expanded_node[-1].children[0]                     #add為f(n)最小者,並找frontier第二小的值
        
        if add.value>expanded_node[-1].keep:                  #如果fmin>keep
            expanded_node[-1].value=add.value                 #expanded_node[-1].value改為fmin       
            expanded_node[-1].keep=None
            expanded_node[-1].expanded=False 
            num=len(expanded_node[-1].children)
            for j in range(0,num):                            #把expanded_node[-1]的children自frontier去除
                del frontier[-1]
                del Rbfs.movement[-1]
            frontier.append(expanded_node[-1])                #把expanded_node[-1]加回frontier
            del expanded_node[-1]                             #自expanded_node刪除
        
        else:                                                 #如果fmin<keep
            add.keep=fsecond        
            expanded_node.append(add)                         #則展開add
            state_changes+=1
            if expanded_node[-1].children==[]:
               expanded_node[-1].add_children()
            expanded_node[-1].expanded=True
            for n in expanded_node[-1].children: 
               if not n.expanded:
                 self.start=n
                 f=self.add_frontier()
                 if f==True:
                  return True 
  
    
def IDS(initial_state,goal,initial):
    print('')
    print('This is IDS')
    print('####################')
    global find
    global MaxnumState
    global state_changes
    for i in range(1,10):                          #limit層數
        if find==True:
            MaxnumState=MaxnumState
            print('The number of state changes:',state_changes)
            state_changes=0
            print('Max states ever saved:',MaxnumState)
            print('############################')
            print('\n')      
            find=False
            MaxnumState=0
            break
        if i==9:                                  #9層後解不出來停止(超過16分鐘)
           print('unsolvable')
           print('############################')
           expanded_node.clear()
           frontier.clear()  
           MaxnumState=0
           state_changes=0
           break
        if (initial_state==goal).all():
            print('move:',0)
            print(initial)
            print('The number of state changes:',0)
            print('Max states ever saved:',1)
            print('############################')
            print('\n')
            break
        else:
            frontier.append(Node(initial_state,0))
        while find!=True: 
           gc.collect() 
           if initial.level==i:                   #如果要展開的state == limit,則不展
              del frontier[-1]
           else:   
              Iterative_Deepening_Search(initial,goal)  
           if len(frontier)!=0:
              initial=frontier[-1]                #展開forntier[-1],後進先出
              for n in expanded_node:             #如果在expanded_node裡有比forntier[-1]層數高的 
                  if n.level>=initial.level: 
                     expanded_node.remove(n)      #就刪除，代表回溯 
           else:
               expanded_node.clear()              #做下一層時，清空expanded_node
               frontier.clear()                   #          清空frontier
               break   
        expanded_node.clear()
        frontier.clear()   


def UCS(initial_state,goal,initial):
    print('This is UCS')
    print('####################')
    global find
    global MaxnumState
    global state_changes
    frontier.append(Node(initial_state,0))
    if (initial_state==goal).all():
        print('move:',0)
        print(initial)
        print('The number of state changes:',0)
        print('Max states ever saved:',1)
        print('############################')
        print('\n')      
        return None
    while len(expanded_node)==0 or expanded_node[-1].level<8 :   #大於7層時停止，記憶體問題
        if find==True:
           MaxnumState=len(Uniform_Cost_Search.movement)+1       #加1,因initial_state沒算到 
           print('The number of state changes:',state_changes)
           state_changes=0
           print('Max states ever saved:',MaxnumState)
           print('############################')
           print('\n')      
           find=False
           MaxnumState=0
           Uniform_Cost_Search.movement=[]
           expanded_node.clear()
           frontier.clear()
           return None
        else:
           Uniform_Cost_Search(initial,goal)
    print('unsolvable') 
    print('############################')
    find=False
    state_changes=0
    MaxnumState=0
    Uniform_Cost_Search.movement=[]
    expanded_node.clear()
    frontier.clear()

def GREEDY(initial_state,goal,initial):
    print('This is GREEDY')
    print('####################')
    global find
    global MaxnumState
    global state_changes
    frontier.append(Node(initial_state,0))
    if (initial_state==goal).all():
        print('move:',0)
        print(initial)
        print('The number of state changes:',0)
        print('Max states ever saved:',1)
        print('############################')
        print('\n')      
        return None
    while len(expanded_node)==0 or len(expanded_node)<100 :
        if find==True:
           MaxnumState=len(Geedy_Bestfirst_Search.movement)+1   #加1,因initial_state沒算到 
           print('The number of state changes:',state_changes)
           state_changes=0
           print('Max states ever saved:',MaxnumState)
           print('############################')
           print('\n')      
           find=False
           MaxnumState=0
           expanded_node.clear()
           frontier.clear()
           return None
        else:
           Geedy_Bestfirst_Search(initial,goal)         
    print('unsolvable') 
    find=False
    MaxnumState=0
    state_changes=0
    Geedy_Bestfirst_Search.movement=[]
    expanded_node.clear()
    frontier.clear()

def ASTAR(initial_state,goal,initial):
    print('This is ASTAR')
    print('####################')
    global find
    global MaxnumState
    global state_changes
    frontier.append(Node(initial_state,0))
    if (initial_state==goal).all():
        print('move:',0)
        print(initial)
        print('The number of state changes:',0)
        print('Max states ever saved:',1)
        print('############################')
        print('\n')      
        return None
    while len(expanded_node)==0 or len(expanded_node)<100 :
        if find==True:
           MaxnumState=len(Astar.movement)+1                    #加1,因initial_state沒算到 
           print('The number of state changes:',state_changes)
           state_changes=0
           print('Max states ever saved:',MaxnumState)
           print('############################')
           print('\n')      
           find=False
           MaxnumState=0
           expanded_node.clear()
           frontier.clear()
           return None
        else:
           Astar(initial,goal)         
    print('unsolvable') 
    find=False
    MaxnumState=0
    state_changes=0
    Astar.movement=[]
    expanded_node.clear()
    frontier.clear()

def RBFS(initial_state,goal,initial):
    print('This is RBFS')
    print('####################')
    global find
    global MaxnumState
    global Rbfsmax 
    global state_changes
    initial.keep=100000
    frontier.append(initial)
    if (initial_state==goal).all():
        print('move:',0)
        print(initial)
        print('The number of state changes:',0)
        print('Max states ever saved:',1)
        print('############################')
        print('\n')      
        return None
    while len(expanded_node)==0 or len(expanded_node)<30 :
        if find==True:  
           MaxnumState=Rbfsmax+1                               #加1,因initial_state沒算到 
           print('The number of state changes:',state_changes)
           state_changes=0
           print('Max states ever saved:',MaxnumState)
           print('############################')
           print('\n')      
           find=False
           MaxnumState=0
           Rbfs.movement=[]
           Rbfsmax=0
           expanded_node.clear()
           frontier.clear()
           return None
        else:
           Rbfs(initial,goal)         
    print('unsolvable') 
    find=False
    MaxnumState=0
    state_changes=0
    Rbfs.movement=[]
    Rbfsmax=0
    expanded_node.clear()
    frontier.clear()    


def main():    
    global find
    global MaxnumState
    global goal
    initial_state=list()
    number=list()
    for i in range(4):
        for j in range(4):
            x=input("請隨意輸入1,2,...,15,*:")   #使用＊代表blank
            number.append(x)
        initial_state.append(number.copy())    
        number.clear()
    initial_state=np.array(initial_state,dtype=np.str)                                       #initial
    goal_state=np.array(([[1,2,3,4],[12,13,14,5],[11,15,'*',6],[10,9,8,7]]),dtype=np.str)    #goal
    goal=goal_state
    initial=Node(initial_state,0)
    GREEDY(initial_state,goal,initial)           #GREEDY   結果
    ASTAR(initial_state,goal,initial)            #ASTAR    結果
    RBFS(initial_state,goal,initial)             #RBFS     結果
    IDS(initial_state,goal,initial)              #IDS      結果
    UCS(initial_state,goal,initial)              #UCS      結果
    

if __name__=='__main__':
    main()

