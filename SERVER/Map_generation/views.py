from django.shortcuts import render
from django.http import HttpResponse
from .forms import noOfNodes, MapsForm
from .models import Maps, Node_details, Short, Regagv
from collections import deque, namedtuple
import socket
import os
import json
from _thread import *
from threading import Thread
import select

# Create your views here.

inf = float('inf')
Edge = namedtuple('Edge', 'start, end, cost')

agv_status = {}
read_list = []
idle_agv=[]
global ThreadCount
ThreadCount = 0
thread_success = [False]
global stop_threads
global server_status
global agv_id_to_assign
server_status = False
activeagv=['AGV1','AGV2','AGV6','AGV7','AGV8']
ar=[]

# Creates socket server with the specified port number
def create_socket():
    try:
        global host
        global port
        global ServerSocket
        host = ""
        port = 1234
        ServerSocket = socket.socket()

    except socket.error as msg:
        print("Socket creation error: " + str(msg))

# Binds the Server to host IP and port and starts listening 
def bind_socket():
    try:
        global host
        global port
        global ServerSocket
        print("Binding the Port: " + str(port))

        ServerSocket.bind((host, port))
        ServerSocket.listen(5)

    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        bind_socket()

def make_edge(start, end, cost=1):
  return Edge(start, end, cost)

# defining graph class
class Graph:
    def __init__(self, edges):
        # let's check that the data is right
        wrong_edges = [i for i in edges if len(i) not in [2, 3]]
        if wrong_edges:
            raise ValueError('Wrong edges data: {}'.format(wrong_edges))

        self.edges = [make_edge(*edge) for edge in edges]

    @property
    def vertices(self):
        return set(
            sum(
                ([edge.start, edge.end] for edge in self.edges), []
            )
        )

    def get_node_pairs(self, n1, n2, both_ends=True):
        if both_ends:
            node_pairs = [[n1, n2], [n2, n1]]
        else:
            node_pairs = [[n1, n2]]
        return node_pairs

    def remove_edge(self, n1, n2, both_ends=True):
        node_pairs = self.get_node_pairs(n1, n2, both_ends)
        edges = self.edges[:]
        for edge in edges:
            if [edge.start, edge.end] in node_pairs:
                self.edges.remove(edge)

    def add_edge(self, n1, n2, cost=1, both_ends=True):
        node_pairs = self.get_node_pairs(n1, n2, both_ends)
        for edge in self.edges:
            if [edge.start, edge.end] in node_pairs:
                return ValueError('Edge {} {} already exists'.format(n1, n2))

        self.edges.append(Edge(start=n1, end=n2, cost=cost))
        if both_ends:
            self.edges.append(Edge(start=n2, end=n1, cost=cost))

    @property
    def neighbours(self):
        neighbours = {vertex: set() for vertex in self.vertices}
        for edge in self.edges:
            neighbours[edge.start].add((edge.end, edge.cost))

        return neighbours
    
    #function to find the shortest path
    def dijkstra(self, source, dest):
        assert source in self.vertices, 'Such source node doesn\'t exist'
        distances = {vertex: inf for vertex in self.vertices}
        previous_vertices = {
            vertex: None for vertex in self.vertices
        }
        distances[source] = 0
        vertices = self.vertices.copy()

        while vertices:
            current_vertex = min(
                vertices, key=lambda vertex: distances[vertex])
            vertices.remove(current_vertex)
            if distances[current_vertex] == inf:
                break
            for neighbour, cost in self.neighbours[current_vertex]:
                alternative_route = distances[current_vertex] + cost
                if alternative_route < distances[neighbour]:
                    distances[neighbour] = alternative_route
                    previous_vertices[neighbour] = current_vertex

        path, current_vertex = deque(), dest
        while previous_vertices[current_vertex] is not None:
            path.appendleft(current_vertex)
            current_vertex = previous_vertices[current_vertex]
        if path:
            path.appendleft(current_vertex)
        return path
#calling homepage
def map1(request):

    return render(request, 'Map_generation/home page.html')

#function which processes the form which collects the information about number of nodes and number of stations and saves it  
def maps_detail(request):
    if request.method == 'POST':
        form = MapsForm(request.POST)
        if form.is_valid():
            nodes = form.cleaned_data['nodes']
            stations = form.cleaned_data['stations']
            lst=[]
            lst.append(nodes)
            lst.append(stations)
            tot = nodes+stations
            print(nodes,stations)
            form.save()
            total=[]
            delprevnodes = Node_details.objects.all()
            delprevnodes.delete()
            for i in range(1,tot+1):
                total.append(i)

            return render(request, 'Map_generation/Map2.html', {'tot':tot})
    form = MapsForm()

    return render(request, 'Map_generation/Map.html', {'form':form})

#function which processes the form which collects the information about each node and station and saves it 
def node_details_save(request):
    # for i in range(1,tot+1):
    if request.method == 'POST':
            node_details=Node_details()
            current= request.POST.get('current')
            left = request.POST.get('left')
            right = request.POST.get('right')
            straight = request.POST.get('straight')
            ldist = request.POST.get('ldist')
            rdist = request.POST.get('rdist')
            sdist = request.POST.get('sdist')
            tot = request.POST.get('tot')
            node_details.current = current
            node_details.left = left
            node_details.right = right
            node_details.straight = straight
            node_details.ldist = ldist
            node_details.rdist = rdist
            node_details.sdist = sdist
            node_details.save()
            graph1 = Node_details.objects.all()
            graph2 = list(graph1)
            graph = []
            t = []
            q = []
            g = []
            d = []
            for i in range(0, len(graph2)):
                curr = graph2[i].current
                left = graph2[i].left
                ldist = graph2[i].ldist
                right = graph2[i].right
                rdist = graph2[i].rdist
                straight = graph2[i].straight
                sdist = graph2[i].sdist
                t.clear()
                q.clear()
                t.append(curr)
                t.append(left)
                t.append(ldist)
                t.append(right)
                t.append(rdist)
                t.append(straight)
                t.append(sdist)
                if left != 'X':
                    q.clear()
                    q.append(curr)
                    q.append(left)
                    q.append(ldist)
                    g.append(tuple(q))
                    q.append('L')
                    d.append(tuple(q))

                if right != 'X':
                    q.clear()
                    q.append(curr)
                    q.append(right)
                    q.append(rdist)
                    g.append(tuple(q))
                    q.append('R')
                    d.append(tuple(q))

                if straight != 'X':
                    q.clear()
                    q.append(curr)
                    q.append(straight)
                    q.append(sdist)
                    g.append(tuple(q))
                    q.append('S')
                    d.append(tuple(q))
                graph.append(tuple(t))
            print(graph)
            print(g)
            print(d)
            print(tot)
            tot = int(tot)
            if tot==1:
                return HttpResponse("Maps Updated")
            else:
                tot = tot - 1
                return render(request, 'Map_generation/Map2.html', {'tot': tot})

    else:
            print("random error")
            return HttpResponse("random error")
#This function allows the user to manually assign tasks to agv from the server 
def shortest_dist(request):
    s=0
    t=0
    if request.method == 'POST':
        global server_status
        if 'startb' in request.POST:
            if server_status:
                s=1
                pass
            else:
                s=1
                start_server()
                server_status = True
            return render(request, 'Map_generation/Map3.html', {'status_list': idle_agv, 's': s})
        elif 'stop' in request.POST:
            if server_status:
                stop_server()
                server_status = False
                s=0
            else:
                s=0
                pass
            return render(request, 'Map_generation/Map3.html', {'status_list': idle_agv, 's': s})
        elif 'autoassign' in request.POST:
            start1 = request.POST.get('start')
            dest1 = request.POST.get('dest')
            auto_assign(start1,dest1)
            return HttpResponse(agv_id_to_assign)
        elif 'submit' in request.POST:
            delprev = Short.objects.all()
            delprev.delete()
            short = Short()
            start = request.POST.get('start')
            dest = request.POST.get('dest')
            short.start = start
            short.dest = dest
            graph1 = Node_details.objects.all()
            graph2 = list(graph1)
            graph=[]
            t=[]
            q=[]
            g=[]
            d=[]
            for i in range(0,len(graph2)):
                curr = graph2[i].current
                left = graph2[i].left
                ldist = graph2[i].ldist
                right = graph2[i].right
                rdist = graph2[i].rdist
                straight = graph2[i].straight
                sdist = graph2[i].sdist
                t.clear()
                q.clear()
                t.append(curr)
                t.append(left)
                t.append(ldist)
                t.append(right)
                t.append(rdist)
                t.append(straight)
                t.append(sdist)
                if left != 'X':
                    q.clear()
                    q.append(curr)
                    q.append(left)
                    q.append(ldist)
                    g.append(tuple(q))
                    q.append('L')
                    d.append(tuple(q))
                if right != 'X':
                    q.clear()
                    q.append(curr)
                    q.append(right)
                    q.append(rdist)
                    g.append(tuple(q))
                    q.append('R')
                    d.append(tuple(q))
                if straight != 'X':
                    q.clear()
                    q.append(curr)
                    q.append(straight)
                    q.append(sdist)
                    g.append(tuple(q))
                    q.append('S')
                    d.append(tuple(q))
                graph.append(tuple(t))
            print(graph)
            print(g)
            print(d)
            short.save()
            shortpath = Graph(g)
            print(list(shortpath.dijkstra(start, dest)))
            result = []
            x = list(shortpath.dijkstra(start, dest))
            for i in range(0, len(x) - 1):
                for j in range(0, len(d)):
                    if x[i] == d[j][0] and x[i + 1] == d[j][1]:
                        result.append(d[j][3])
            print(result)
            res = str(result)
            assign_task(request.POST.get('agvlist'),start,dest)
            return HttpResponse(res)
    return render(request, 'Map_generation/Map3.html',{'status_list': idle_agv, 's': s})

#function which returns the shortest path
def path(A,B):
    graph1 = Node_details.objects.all()
    graph2 = list(graph1)
    graph=[]
    t=[]
    q=[]
    g=[]
    d=[]
    Start = A
    Dest = B
    for i in range(0,len(graph2)):
        curr = graph2[i].current
        left = graph2[i].left
        ldist = graph2[i].ldist
        right = graph2[i].right
        rdist = graph2[i].rdist
        straight = graph2[i].straight
        sdist = graph2[i].sdist
        t.clear()
        q.clear()
        t.append(curr)
        t.append(left)
        t.append(ldist)
        t.append(right)
        t.append(rdist)
        t.append(straight)
        t.append(sdist)
        if left != 'X':
            q.clear()
            q.append(curr)
            q.append(left)
            q.append(ldist)
            g.append(tuple(q))
            q.append('L')
            d.append(tuple(q))
        if right != 'X':
            q.clear()
            q.append(curr)
            q.append(right)
            q.append(rdist)
            g.append(tuple(q))
            q.append('R')
            d.append(tuple(q))
        if straight != 'X':
            q.clear()
            q.append(curr)
            q.append(straight)
            q.append(sdist)
            g.append(tuple(q))
            q.append('S')
            d.append(tuple(q))
        graph.append(tuple(t))
    print(graph)
    print(g)
    print(d)
    shortpath = Graph(g)
    print(list(shortpath.dijkstra(Start, Dest)))
    result = []
    dist=0
    x = list(shortpath.dijkstra(Start, Dest))
    for i in range(0, len(x) - 1):
        for j in range(0, len(d)):
            if x[i] == d[j][0] and x[i + 1] == d[j][1]:
                result.append(d[j][3])
                dist=dist+d[j][2]
    print(result)
    return(dist,result,list(shortpath.dijkstra(Start, Dest)))

# Automatically assign the task to the AGV which is near to the start node & idle
# Parameters passed - Start Node and End Node of the Task
def auto_assign(start_node,end_node):
    dist=999
    global agv_id_to_assign
    for agv in idle_agv:
        distt,summa1,summa2=path(agv_status[agv]['CURRENT_LOCATION'],start_node) 
        if distt<dist:
            dist=distt
            agv_id_to_assign = agv
    print(f'agv to assign is {agv_id_to_assign}')
    assign_task(agv_id_to_assign,start_node,end_node)

# Creats a thread for each client request and process it
# Parameters passed - Server client connection object
def threaded_client(connection):
    #connection.send(str.encode('Welcome to the Server\n'))
    while True:
        jdata = connection.recv(2048)
        
        #reply = 'Server Says: ' + data.decode('utf-8')
        if not jdata:
            break
        data=json.loads(jdata)
        agv_status[data['AGV_ID']]={}
        agv_status[data['AGV_ID']]['STATUS']=data['STATUS']
        try:
            agv_status[data['AGV_ID']]['CURRENT_LOCATION']=data['CURRENT_LOCATION']
        except:
            pass
        agv_status[data['AGV_ID']]['OBJECT']=connection
        if data['STATUS']=='idle' and data['AGV_ID'] not in idle_agv:
            idle_agv.append(data['AGV_ID'])
        else:
            if data['AGV_ID'] in idle_agv:
                idle_agv.remove(data['AGV_ID']) 
        print(idle_agv)
        response(data,connection)
        #connection.sendall(str.encode(reply))
    connection.close()

# Sends the Direction Array and Node Array to a Particular AGV
# Parameters passed - AGV ID to be assigned, start node and end node of the task
def assign_task(id,start_node,end_node):
    distt,dirr,node=path(agv_status[id]['CURRENT_LOCATION'],start_node)
    dirr.append("X")
    dist,direction_array,node_array = path(start_node,end_node) 
    dirr.extend(direction_array)
    node.extend(node_array)
    dirr.append("X")
    responsejsons={}
    responsejsons={"COUNT":len(dirr),"PATH":dirr,"NODE":node}
    print(responsejsons)
    agv_status[id]['STATUS']="busy"
    idle_agv.remove(id)
    agv_status[id]['OBJECT'].sendall(str.encode(json.dumps(responsejsons)))

# This fucntion sends the Direction array and Node array to an AGV from which the Request is obtained
# Parameters Passed - JSON String From AGV and the Socket Client connection object 
def response(data,connection):
    responsejsons={}
    print(data)
    print(agv_status)
    if data.get('START'):
       dist,direction_array,node_array = path(data['START'],data['DESTINATION'])
       #assign_task(data['AGV_ID'],direction_array,node_array) 
       responsejsons={}
       pathai=direction_array #direction list must be assigned
       pathai.append("X")
       print(pathai)
       responsejsons={"COUNT":len(pathai),"PATH":pathai,"NODE":node_array}
       agv_status[data['AGV_ID']]['OBJECT'].sendall(str.encode(json.dumps(responsejsons)))

# Main Function that calls the threaded clinet function when ever there is new client request in the Socket Buffer
# This function runs all the time whever the Server is started (in a seperate thread)
def main():
    global ThreadCount
    global stop_threads
    global read_list
    while True:
        readable, writable, errored = select.select(read_list, [], [], 1)
        for s in readable:
            if s is ServerSocket:
                Client, address = ServerSocket.accept()
                read_list.append(Client)
                print(type(Client))
                print('Connected to: ' + address[0] + ':' + str(address[1]))
                start_new_thread(threaded_client, (Client, ))
                ThreadCount += 1
                print('Thread Number: ' + str(ThreadCount))
        if stop_threads:
            ServerSocket.close()
            break
# This function returns a page which allows the user to start the server 
def agvreq(request):
    if request.method == 'POST':
        start_server()
    return render(request, 'Map_generation/agvreq.html')

# This Function starts the Socket Server and starts listening to the port
def start_server():
    global stop_threads
    create_socket()
    bind_socket()
    global read_list
    read_list = [ServerSocket]
    stop_threads = False
    global server
    global server_status
    server = Thread(target=main)
    server.start()
    server_status = True
    print("Server Started!!")

# This Function Stops the Socket Server
def stop_server():
    global stop_threads
    global server_status
    stop_threads = True
    global server
    server.join()
    server_status = False
    print("Server Stopped!!")
    
#This function rediects to a page which shows current status of AGVs
def agvstat(request):
    agvs = Regagv.objects.all()
    agvs2 = list(agvs)
    an = []
    ai = []
    stat1=[]
    for i in range(0, len(agvs2)):
        aname = agvs2[i].agvsname
        aid = agvs2[i].agvsid
        an.append(aname)
        if aid in agv_status.keys():
            stat1.append('active')
        else:
            stat1.append('inactive')
    mylist = zip(an, stat1)
    context = {
        'mylist': mylist,
    }
    return render(request, 'Map_generation/list.html',{'mylist':mylist})
#This function allows the user to register the new agvs and give them a name
def regagv(request):
    if request.method == 'POST':
        agvdet=Regagv()
        agvsname= request.POST.get('agvsname')
        agvsid = request.POST.get('agvsid')
        agvdet.agvsid=agvsid
        agvdet.agvsname=agvsname
        agvdet.save()
        agvs = Regagv.objects.all()
        agvs2 = list(agvs)
        a1=[]
        for i in range(0, len(agvs2)):
            aname = agvs2[i].agvsname
            aid= agvs2[i].agvsid
            a1.append(aname)
            a1.append(aid)
        return render(request, 'Map_generation/Done.html')
    agvs1 = Regagv.objects.all()
    agvs12 = list(agvs1)
    for j in agv_status.keys():
        f=0
        for i in range(0, len(agvs12)):
            if agvs12[i].agvsid ==j:
                f=1
        if f==0:
            ar.append(j)
    return render(request, 'Map_generation/registeragv.html',{'ar': ar})
