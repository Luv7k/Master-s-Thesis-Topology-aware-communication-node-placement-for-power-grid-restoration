from copy import copy
from itertools import combinations
import folium
# number to words
import n2w 
# for subscript and superscript
import unicodedata

# we use ast to evaluate the literal of string to a tuple to perform calculations
from ast import literal_eval

from tkinter import *
from tkinter import filedialog as fd
import tkinter.messagebox as tmsg

import csv 
import math
import numpy as np
import pandas as pd
from random import randrange

import os
import shutil
import steiner
import networkx as nx
from matplotlib import pyplot as plt


def create_circle(x, y, r, canvasName, tag, color='green'): 
    """ 
    Provide x,y coordinate of Tkinter canvas
    r is the radius of the circle for point (x, y)
    CanvasName, name of the
    tag is id of the circle
    color which is green by default
    """

    x = float(x)
    y = float(y)
    r = float(r)

    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r

    return canvasName.create_oval(x0, y0, x1, y1, fill=color, tags=(tag))

def create_region(x, y, r, canvasName, tag, color = "#dbbfc3", w=3):
    """ 
    provide with x,y coordinate
    r is the radius for the region
    canvas-name, which canvas you want to add the region
    tag is for id of the region
    color which is #dbbfc3 by default
    """
    x = float(x)
    y = float(y)
    r = float(r)

    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r

    return canvasName.create_oval(x0, y0, x1, y1, tags=(tag), outline=color, width=w)

def create_text_label(x0, y0, node_name,canvasName, tag, color='darkgreen'):
    """
    Using this we can add name labels for our nodes/circles on the canvas
    """

    x0 = float(x0) 
    y0 = float(y0) + 16

    name = node_name
    name = name.split('_')
    new_subscript = name[0]

    for i in list(name[1]):
        n = int(i)
        word = n2w.convert(n)
        subscript = unicodedata.lookup(f'subscript {word}')
        new_subscript += subscript

    return canvasName.create_text(x0, y0, text=new_subscript, fill=color, font=('Times 14'), tag=tag)

def add_island_superscript(old_name:str, island_number:int):
    """Add island number to node name"""

    for i in list(str(island_number)):
        n = int(i)
        word = n2w.convert(n)
        superscript = unicodedata.lookup(f'superscript {word}')
        old_name += superscript

    return old_name

def create_line(x0,y0,x1,y1,canvasName, tag, color="black", w=1):
    """ 
    provide with x0,y0 coordinate of start of line
    provide with x1,y1 coordinate of end of line
    canvas-name, which canvas you want to add the line
    tag is for id of the line
    color which is black by default
    """

    x0 = float(x0)
    y0 = float(y0)
 
    x1 = float(x1)
    y1 = float(y1)

    return canvasName.create_line(x0,y0,x1,y1, fill=color, width=w, tags=(tag))

def check_ps_in_range(ict_or_rr: list, ps: list, check: str):
    """Checks if the power station nodes are in range of repair resources and also in range of Base Station node"""

    information_of_ps_in_range = []

    if check == 'ict':
        for each_ict in ict_or_rr:
            # print(each_ict['node_name'])
            radius_range = float(each_ict['node_range']) / 75
            # print(float(each_ict['node_range'])/100)
            x0 = each_ict['coord'][0]
            y0 = each_ict['coord'][1]
            # print(each_ict['coord'])
            # print(radius_range, x0, y0)

            for each_ps in ps:

                p_nodes_inside = {}

                x1 = each_ps['coords'][0]
                y1 = each_ps['coords'][1]

                distance = math.hypot(x1-x0, y1-y0)
                # distance = math.dist((x0,y0), (x1,y1))

                if (distance < radius_range+1):
                    
                    p_nodes_inside['name'] = each_ict['node_name']
                    p_nodes_inside['coords'] = (x0,y0)
                    p_nodes_inside['ps'] = each_ps['power_node_name']
                    p_nodes_inside['ps_coords'] = (x1,y1)

                    information_of_ps_in_range.append(p_nodes_inside)
                
    elif check == 'rr':

        # lowest = []
        for each_rr in ict_or_rr:

            x0,y0 = each_rr['coords']
            radius_range = each_rr['range']

            for each_ps in ps:

                p_nodes_inside = {}

                x1 = each_ps['coords'][0]
                y1 = each_ps['coords'][1]

                distance = math.hypot(x1-x0, y1-y0)
                # distance = math.dist((x0,y0), (x1,y1))

                if (distance < radius_range + 1) :
                    # print(distance)
                    p_nodes_inside['name'] = 'repair_resource'
                    p_nodes_inside['coords'] = (x0,y0)
                    p_nodes_inside['ps'] = each_ps['power_node_name']
                    p_nodes_inside['ps_coords'] = (x1,y1)

                    information_of_ps_in_range.append(p_nodes_inside)
    
    return information_of_ps_in_range

def check_rr_in_range_of_bs(data, ict_content):

    steiner_point = data['steiner_point']

    n1,n2,n3 = data['coords']
    x1,y1,name1 = n1
    x2,y2,name2 = n2
    x3,y3,name3 = n3

    all_range = []

    for i in ict_content:
        if i['id'] == name1 or i['id'] == name2 or i['id'] == name3 :
            all_range.append( (float(i['range(m)'])/75, i['id']) )

    for i in data['coords']:
        for j in all_range:
            _,_,bs_name = i
            _, node_name = j
            if bs_name == node_name:
                x,y,_ = i
                bs_range,_ = j

                d = math.dist((x,y), (steiner_point))
                # if d <= bs_range :
                #     return 'hide steiner_point'
                if d == 0.0 or d == 0 :
                    return 'hide steiner_point'

#  clear terminal window --------------------------------------
def clear():
    """
    When reset screen button is clicked, this function is triggered
    and it clears the terminal/console window for any operating system
    """
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
    # for mac and linux
    else:
        _ = os.system('clear')

def save_in_map(ict_data, off_node_data, psb_data):


    map1 = folium.Map(location = [53.62,11.38], zoom_start=13, prefer_canvas=True)
    #map1 = folium.Map()
        
    for each_node in ict_data:

        folium.Marker(location=[each_node['x'], each_node['y']],
                    popup=each_node['id'],
                    tooltip=each_node['id'],
                    icon=folium.Icon(icon="info-sign", color='green')).add_to(map1)    

        folium.Circle(location=[each_node['x'], each_node['y']],
                        # radius= float(each_node['range(m)'])/30,
                        # radius = each_node['range(m)'],
                        radius = 50,
                        popup=each_node['id'],
                        color="green",
                        fill=True,
                        fill_color="green",
                    ).add_to(map1)

    for each_node in off_node_data:

        folium.Marker(location=[each_node['x'], each_node['y']],
                    popup=each_node['id'],
                    tooltip=each_node['id'],
                    icon=folium.Icon(icon="info-sign", color='red')).add_to(map1)

        folium.Circle(location=[each_node['x'], each_node['y']],
                        # radius= float(each_node['range(m)'])/30,
                        # radius = each_node['range(m)'],
                        radius = 50,
                        popup=each_node['id'],
                        color="red",
                        fill=True,
                        fill_color="red",
                    ).add_to(map1)

    for each_node in psb_data:
        folium.Marker(location=[each_node['x'], each_node['y']],
                    popup=each_node['id'],
                    tooltip=each_node['id'],
                    icon=folium.Icon(icon="info-sign", color='lightblue')).add_to(map1)

    with open('cist_data/RR_for_CIST.csv', 'r+', newline='') as f:
        data = csv.DictReader(f)
        for i in data:
            folium.Marker(location=[i['Latitude'], i['Longitude']],
                    popup=i['Name'],
                    tooltip=i['Name'],
                    icon=folium.Icon(icon="info-sign", color='purple')).add_to(map1)
            folium.Circle(location=[i['Latitude'], i['Longitude']],
                        radius = 50,
                        popup=i['Name'],
                        color="purple",
                        fill=True,
                        fill_color="purple",
                    ).add_to(map1)


    map1.save('cist_data/cist_map.html')
    
    map_path = os.path.abspath('cist_data')
    os.system(f"start {map_path}\\cist_map.html")


class GUI(Tk):
    """
    This is the Tkinter window 
    """
    range_in_km = 8
    range_in_m = range_in_km*1000
    range_for_canvas = range_in_m / 75

    # constructor
    def __init__(self):
        super().__init__()
        self.title("CIST")
        self.geometry("800x850")
        #self.iconbitmap('conn.ico')
        self.maxsize(800,850)
        self.minsize(800,850)

        # self.range = 100.00
        self.range = GUI.range_for_canvas
        
        self.long_min = 11.38
        self.long_max = 11.435
        self.lat_min = 53.615
        self.lat_max = 53.67
        # 11.38 - 11.435      53.62 - 53.66

        self.repair_resources = []

        # top frame with canvas----------------------------
        top_frame = Frame(self)
        top_frame.grid(row=0,column=0)

        my_can = Canvas(top_frame, width=800,height=800,bg="white")

        my_can.grid(row=0,column=0)
        self.can = my_can
        # bottom frame with buttons-------------------------
        bottom_frame = Frame(self)
        bottom_frame.grid(row=1,column=0)

        load_ict_button = Button(bottom_frame,text='Load ICT', width=10, command = self.load_ict_file)
        load_ict_button.grid(row=0,column=0, pady=7, padx=7)

        load_psb_button = Button(bottom_frame,text='Load PSB', width=10, command = self.load_psb_file, state=DISABLED)
        load_psb_button.grid(row=0,column=1, pady=7, padx=7)
        self.psb_button = load_psb_button

        connect_nodes = Button(bottom_frame, text="Connect", command = self.check_gain_triangular_subsets , state=DISABLED, width=10)
        connect_nodes.grid(row=0,column=2, pady=7, padx=7)
        self.connect_nodes = connect_nodes

        reset_button = Button(bottom_frame, text="Reset Screen", command = self.reset_screen)
        reset_button.grid(row=0,column=3, pady=7, padx=7)

        zoom_button = Button(bottom_frame, text='Zoom/Pan', command=self.add_zoom_and_pan, state=DISABLED)
        zoom_button.grid(row=0,column=4, padx=7, pady=7)
        self.zoom_button = zoom_button

    def add_zoom_and_pan(self):
        # /zooming function 
        # from tkinter import ALL, EventType
        self.can.bind("<MouseWheel>", self.do_zoom)
        self.can.bind('<ButtonPress-1>', lambda event: self.can.scan_mark(event.x, event.y))
        self.can.bind("<B1-Motion>", lambda event: self.can.scan_dragto(event.x, event.y, gain = 1) )

    def do_zoom(self,event):
        x = self.can.canvasx(event.x)
        y = self.can.canvasy(event.y)
        factor = 1.001 ** event.delta
        self.can.scale(ALL, x, y, factor, factor)

    # ask user for csv file-----------------------
    def load_ict_file(self):
        """Here, We load the input file user selected, convert their latitudes and longitudes in to x and y coordinates
        based on our canvas size, draw them on canvas, connect the nodes according to their ICT-links from file and
        then form islands of those nodes."""
        # to use csv file data 
        filetypes = (
                     ('csv files', '*.csv'),
                     ('excel files', '*.xlsx')
                     )
        ict_file = fd.askopenfilename(filetypes=filetypes)
        
        """create empty lists, we will add coordinates of nodes in coordinates list,
        label of nodes in labels list
        and the node object created in circles list"""

        self.co_ordinates_of_all_nodes = []
        self.circles = []
        self.labels = []

        """If user selects a file then run the following"""

        if ict_file :
            
            """we will save our content in csv_content list and create self.ict_content so that it can be used for same object further.
            We open the file and append each line from file in csv_content"""
            
            ict_content = []
            
            # read the file and get co-ordinates
            with open(ict_file, "r") as ict_f:
                ict_data = csv.DictReader(ict_f, delimiter=";")

                for line in ict_data:
                    ict_content.append(line)

            self.ict_content = ict_content

            #  start conversion of lats and longs-----------------
            """we need to change the latitudes and longitude values into x-y coordinates to fit our canvas window hence we try to convert using the following
            - create empty longitude, latitude, x value and y value list
            - loop through the csv-content get data from file convert it into float and store it into respectively latitude and longitude lists.
            - get the min and max values for both and round them for 2 decimal places
            """
            lat_val = []
            x_val = []
            
            lon_val = []
            y_val = []
            
            for each_n in ict_content:
                lat_val.append(float(each_n['x']))
                lon_val.append(float(each_n['y']))
            
            """
            - loop through the lat list and long list, calculate the x and y according to canvas size
            - some values might be negative, so we get the absolute values (abs) of those, round them for 2 decimal places and append them to their respective x and v value list
            """

            for lon in lon_val:
                converted_y = (lon - self.long_min) * 800 / (self.long_max - self.long_min)
                y_val.append(round(converted_y,2))

            for lat in lat_val:
                converted_x = self.lat_max - (lat - self.lat_min) * 800 / (self.lat_max - self.lat_min)
                x_val.append(round(converted_x,2))
            
            """ once we have the lattitude and longitude converted to x and y, we replace them with our values in dataset file in our variable 
            # NOTE: we are not changing the actual values in dataset"""

            for x_index, canvas_x in enumerate(x_val):
                for index , each_node in enumerate(ict_content):
                    if x_index == index :
                        each_node['X'] = canvas_x


            for y_index, canvas_y in enumerate(y_val):
                for index , each_node in enumerate(ict_content):
                    if y_index == index :
                        each_node['Y'] = canvas_y

            #  end conversion-----------------

            """
            - now we loop through each item in our self.ict_content list, assume radius as 5 for node and use create circle and create text label functions for labelling the name of node and creation of nodes
            """
            nodes_which_are_ON = []
            nodes_which_are_OFF = []
            
            for each_node in self.ict_content:
                if each_node['status'] == 'on':
                    nodes_which_are_ON.append(each_node)
                else:
                    nodes_which_are_OFF.append(each_node)


            # display nodes which are OFF
            self.ict_node_off = nodes_which_are_OFF
            for each_node in nodes_which_are_OFF:
                each_node['r'] = 5
                circle = create_circle(abs(each_node['X']),abs(each_node['Y']),each_node['r'],self.can, each_node['id'], color='red')
                node_name = each_node['id']
                node_label = create_text_label(abs(each_node['X']), abs(each_node['Y']), each_node['id'], self.can, tag=(node_name), color='red')
                self.can.tag_lower(node_label)
                
            

            # display nodes which are ON
            self.ict_content = nodes_which_are_ON

            for each_node in self.ict_content:
            
                each_node['r'] = 5

                circle = create_circle(abs(each_node['X']), abs(each_node['Y']),each_node['r'],self.can, each_node['id'])

                self.circles.append(circle)
                # get the x y coordinate of node points
                x_y_points = self.can.coords(circle)
                # get the node - name
                node_name = each_node['id']

                node_label = create_text_label(abs(each_node['X']), abs(each_node['Y']), each_node['id'], self.can, tag=(node_name))

                self.can.tag_lower(node_label)
                self.labels.append(node_label)

                """adding range to node object"""
                range_of_node = each_node['range(m)']

                """
                We create a dictionary of information of a particular node and add that to the coordinates of all nodes list

                - node_obj = {"node_name": node_name,
                            "coord": x_y_points , 
                            "status": "on", 
                            "connection" : each_node['connection']}
                """

                node_obj = {"node_name": node_name,"coord": x_y_points , "status": "on", "ict_links" : each_node['ict_links'], "node_range": range_of_node}
                self.co_ordinates_of_all_nodes.append(node_obj)
                
            """
            Once our nodes are created on canvas, we create their links,
            - first we loop over csv_content and get teh links data
            - this data is in 'string' format, so we need to make a 'list' in python
            - hence we have make a new list and add that to the csv_content.. 
            """

            for each_node in self.ict_content:

                conn = each_node['ict_links']
                conn = conn[1:len(conn)-1].split(",")

                new_conn = []
                for each_conn in conn:
                    c = str(each_conn).strip()
                    c = c[1:len(c)-1]
                    new_conn.append(c)
                
                each_node['ict_links'] = new_conn
                # connections for each node
                """
                finally we draw the connection lines using new connection (which is a list, so that we can use loops) for each node in csv_content with a color green
                """
                self.draw_connection_lines(new_conn, each_node, "green") 

                # showing range in canvas by drawing
                range_of_node = each_node['range(m)']
                # dividing it by 75 to convert it into cm from m 
                range_of_node = float(range_of_node)/75
                range_circle = create_region(abs(each_node['X']), abs(each_node['Y']), range_of_node, self.can, tag=(f'range_of_{node_name}'), color='green', w=1)
                self.can.tag_lower(range_circle)

            """
            Once we draw the connection lines, we need to form islands based on those connections formed, here we use 'form-islands' function to form those islands and create a region around the nodes
            """
            self.form_islands()
        self.psb_button.config(state=NORMAL)

    # ----------------------------- 
    def load_psb_file(self):

        # to use csv file data 
        filetypes = (
            ('csv files', '*.csv'),
            ('excel files', '*.xlsx')
        )
        psb_file = fd.askopenfilename(filetypes=filetypes)

        if psb_file:
            psb_content = []
            # read the file and get co-ordinates
            with open(psb_file, "r") as psb_f:
                psb_data = csv.DictReader(psb_f, delimiter=";")

                for line in psb_data:
                    psb_content.append(line)

            lat_val = []
            x_val = []
            
            lon_val = []
            y_val = []
            
            for each_n in psb_content:
                lat_val.append(float(each_n['x']))
                lon_val.append(float(each_n['y']))

            for lon in lon_val:
                converted_y = (lon - self.long_min) * 800 / (self.long_max - self.long_min)
                y_val.append(round(converted_y,2))
                # y_val.append(round(abs(converted_y),2))

            for lat in lat_val:
                converted_x = self.lat_max - (lat - self.lat_min) * 800 / (self.lat_max - self.lat_min)
                x_val.append(round(converted_x,2))
                # x_val.append(round(abs(converted_x),2))

            for x_index, canvas_x in enumerate(x_val):
                for index , each_node in enumerate(psb_content):
                    if x_index == index :
                        each_node['X'] = canvas_x

            for y_index, canvas_y in enumerate(y_val):
                for index , each_node in enumerate(psb_content):
                    if y_index == index :
                        each_node['Y'] = canvas_y

            self.psb_content = psb_content
            self.power_nodes = []
            self.power_circles = []

            for each_node in self.psb_content:
                power_nodes = {}
                
                each_node['r'] = 5

                circle = create_circle(abs(each_node['X']), abs(each_node['Y']), each_node['r'],self.can, tag = ((each_node['id'],)), color='grey')
                self.power_circles.append(circle)
                
                # get the x y coordinate of node points
                x_y_points = self.can.coords(circle)

                power_nodes['power_node_name'] = each_node['id'] 
                power_nodes['coords'] = x_y_points 
                
                self.power_nodes.append(power_nodes)

        self.connect_nodes.config(state=NORMAL)
        return 0

    # draw connection lines red or green-------------------------------
    def draw_connection_lines(self, connection_nodes, node_start,  color):
        """
        This takes list of connection for particular node , the starting node and the color,
        to form the line, here we are using create line function which we created in the beginning to draw lines
        """
        # if  there's one connection
        if len(connection_nodes) == 1:
            for node_end in self.ict_content:
                if node_end['id'] == connection_nodes[0] :
                    tag = f"{node_start['id']} {node_end['id']}"
                    s = create_line(abs(node_start['X']), abs(node_start['Y']), abs(node_end['X']), abs(node_end['Y']), self.can, tag, color)
                    self.can.tag_lower(s)

        # if there's more than one connection 
        elif len(connection_nodes) > 1:

            for i in connection_nodes :
                for node_end in self.ict_content:
                    if node_end['id'] == i :
                        tag = f"{node_start['id']} {node_end['id']}"
                        s = create_line(abs(node_start['X']), abs(node_start['Y']), abs(node_end['X']), abs(node_end['Y']), self.can, tag, color)
                        self.can.tag_lower(s)
    # -------------------------------- 
    
    # get points of all islands---------------------
    def get_points_of_islands(self, all_islands):
        """
        We get the non-repeating islands here as arguments,
        we create empty list of coordinates namely 'all-coords',
        loop over island list we have as argument,
        then we create another empty list of coords,
        loop over each island, then loop over self.coordinates-of-all-nodes,
        if the node name matches to names in our data file,
        then we get its coordinates and add it to coords list
        and inside outermost loop we add coordinate list.

        Finally we make a tuple, by looping over all-coords list,
        and assigning color to regions depending on number of nodes present inside that island,
        considering radius as 30, adding the tuple to the list 'all-cents' and finally returning the 'all-cents'list

        """

        all_coords = []
        for island in all_islands:
            coords = []

            for each in island:

                for each_coord in self.co_ordinates_of_all_nodes:
 
                    if each == each_coord['node_name']:

                        coords.append( (each_coord['coord'], each_coord['node_name']) )
            
            all_coords.append(coords)

        # now we have the co-ordinates for island nodes, we need to calculate centroids 
        all_cents = []
        radius = 30
        
        for counter, i in enumerate(all_coords):

            if len(i) == 1:
                color = '#f5f5ab'
            elif len(i) == 2:
                color = '#8da2e3'
            elif len(i) == 3:
                color = '#a8dbed'
            elif len(i) == 4:
                color = '#d0f5d2'
            else:
                color = "#f3d0f5"

            x_y_points_islands = []

            for points in i:
                each_point, point_name = points
                px,py = each_point[0], each_point[1]
                x_y_points_islands.append( ( (int(px) + 5), (int(py) + 5) ,point_name) )

            all_cents.append((x_y_points_islands, radius, (counter), color))

        return all_cents                   
    # -----------------------------

    # form islands-----------------
    def island_info(self,island_list):
        """
        create empty list = final-island
        We get island list (island-A) as argument,
        loop over that list, sort the list and check if island-A element is in final-island list, if yes then do nothing, if its not present, then add that island in final-islands
        and return the final-island list 
        """
        final_islands = []

        for val in island_list:
            val = sorted(val)
            if val not in final_islands:
                final_islands.append(val)

        return final_islands

    # form islands according to connections----------------------------
    def form_islands(self):
        """
        We've used this function in load-csv function to form islands,
        island formation was difficult but we've used 'networkx' from python so that we can visualize our graph and perform functions on it from networkx which will give us all information about islands and connections 
        """

        """ This converts the string data of ict-links into list so that we can
        use functions on that"""
        # remove connection from the node which was connected
        for node in self.co_ordinates_of_all_nodes:

            new_conn = []
            conn_list = node['ict_links']

            conn_list = conn_list[1:len(conn_list)-1].split(',')

            for conn in conn_list:
                # remove spaces from text
                c = conn.strip()
                c = c[1:len(c)-1]
                
                new_conn.append(c)
            
            node['ict_links'] = new_conn

        """
        We loop over coordinates of all nodes, and create a separate list where we have kept all our nodes which have status ON and name list as 'self.nodes_on'. Status was being added in older version where we created dictionary of 'node object' for node information above in load-csv file function 
        """
        # get all the nodes which are on
        self.nodes_on = []
        for node in self.co_ordinates_of_all_nodes:
            if node['status'] == 'on':
                self.nodes_on.append(node) 

        # use networkx to get neighbors and group them---------------
        """
        Now we use networkX to form our graph based on data,
        - create an empty graph using 'nx.Graph()'
        - loop over 'self.nodes_on' and add each node using the node_name from node-object
        - once we have our nodes on graph, we take their connections (ict-links), loop over them and add edges between the node and its respective links (we also check if the link are empty (''), if they are then we don't connect it to anyone)
        """
        self.G = nx.Graph()
        for a in self.nodes_on:
            self.G.add_node(a['node_name'])
    
            c = a['ict_links']
            # print(a['node_name'], c)
            for c_inner in c:
                # print(c_inner)
                if c_inner != '':
                    self.G.add_edge(a['node_name'] , c_inner)

        # ------------------------------------
        """
        - Get nodes from the networkX graph, sort them and put it in one list (sorted_arr)
        - get the nodes again and put it in another list (all_nodes)
        - create 2 empty lists of island-A and island-B
        - loop over sorted nodes and find their neighbors using networkX function 'neighbors' (this will give us data in set, we convert it into python-list)
        - Then we check if length of that list is 0 or not, if it is 0 that means it has no connection/links to other nodes and it is a single island,
            so we create a list on-spot( you can see '[ (node_1) ]' squared brackets) which contains that node and append that list in 'island-A' list
        - Then if length of list is not 0 that means it has some links with other nodes,
            so we loop over 'all_nodes' list, check if the node is in neighbors, if yes then we add it in 'island-B'
        """
        # sorted nodes and all nodes 
        sorted_arr = sorted(self.G.nodes())
        all_nodes = list(self.G.nodes())
        # make 2 empty lists
        island_a = []
        island_b = []

        for node_1 in sorted_arr:
            neighbours = list(self.G.neighbors(node_1))

            # if no connection present then create separate island and put them in island-A
            if len(neighbours) == 0:
                island_a.append([(node_1)])

            # connection present then group together and add to island-B list
            else:
                for node_2 in all_nodes:
                    if node_2 in neighbours:
                        if node_2 not in island_b:
                            island_b.append(node_2)

        """
        Now we need to check if there is a path between the nodes, since the nodes which are connected would have a path
        - we loop over 'island-B', create empty set 'island-C'
        - we loop over 'all-nodes', we check if outer-loop element is equal to inside-loop element or not
        - if its not equal that means it is a different node, so we check path between those two nodes using networkX graph function 'has_path'
        - if we get a path then we add both nodes to set 'island-C', and convert this set into 'list' and add it to 'island-A' 
        """
        # # use for loop on island-B to check their paths if connected for longer connection
        for each_i in island_b :
            island_c = set()
            for each_i2 in all_nodes:
                if each_i != each_i2:
                    t = nx.has_path(self.G, each_i, each_i2)

                    if t :
                        island_c.add(each_i)
                        island_c.add(each_i2)
            
            island_a.append(list(island_c))

        """
        Finally we have, islands formed in 'island-A' variable, but some values are repeating and in ascending and descending both forms,
        hence, we use 'island_info' function which gives us the non-repeating islands 
        """
        # # create final island list where we have all our final island information
        self.islands = self.island_info(island_list = island_a)

        # check islands and change the label
        for counter,island in enumerate(self.islands):
            for each_i in island:
                for l in self.labels:
                    tag = self.can.gettags(l)
                    if tag[0] == each_i:
                        name = self.can.itemcget(l, "text")
                        new_name = add_island_superscript(name, counter)
                        self.can.itemconfig(l, text=new_name)

        # # get of islands 
        """
        Once we have the non-repeating islands,
        we then get their points by using this function 'get_points_of_islands',
        which returns us all points in a particular island and other color information of the region
        """
        self.separate_islands = self.get_points_of_islands(self.islands)
        
        # ----------------------------------------------------------

        """
        We are simply drawing the regions heres,
        looping over 'separate-islands',
        since there are tuples present, we unpack them into variables on left side
        then if we have more than one point, we loop over those points,
        get the x and y coordinate and draw regions
        """
   
    # ------------------------------------
    """
    Below functions would run after clicking the 'connect' button
    """
    #  get euclidean distance 
    def get_distance(self, point_1, point_2):
        """
        Get the distance between 2 points,
        both points can be in a tuple or a list,
        (x1,y1) or [x1,y1]
        returns distance between those 2 points
        """

        d = math.dist(point_1, point_2)
        return d
    # -----------------------------

    # MST FOR CIST algorithm---------------------
    def mst_for_CIST(self):
        """
        This is the initial mst-check for CIST algorithm, which loops over the islands created and forms mst and adds the result to self.mst_for_cist which is a list
        """
        # get mst distances
        self.mst_for_cist = []
        
        # ------------------------- 
        """
        Here we create another graph object of networkX, which will help us find if 
        all the nodes (islands in our case) in the graph are connected or not, if
        not then we will combine all points from connected islands and form another island and similarly do it for remaining connected islands and then check for shortest distance between them and then connect them accordingly.
        """
        """ create the graph M"""
        self.M = nx.Graph()

        for i in self.separate_islands:
            
            pp,r,clus,color = i
            """
            add islands as node in the graph
            """
            self.M.add_node(clus)

        # ------------------------------
        # # 
        """This loop iterates over all island points
        - we create empty list named, 'each_distance' 
        - when looping we unpack the tuples and get the points and tag(island) data from it
        - we further get those points as x1 and y1 
        - Now we loop over same self.separate sialnds which has all island information
            and we check if the islands are same or not,
            if not then we move ahead in loop and get the points of those islands
            as x2 and y2
        - finally, we get the distance between those points and make a list of 
            - distance between points
            - x1,y1,island_1 as tuple 
            - x2,y2,island_2 as tuple all in this list and then add this information to each_distance list which we created in the beginning of this main outermost loop"""
        each_distance = []
        for each_c1 in self.separate_islands:
        
            points_1, r_1, tag_1, color_1 = each_c1

            for each_c2 in self.separate_islands:
                points_2, r_2, tag_2, color_2 = each_c2

                if tag_1 != tag_2 :
                    dist = []

                    for p_1 in points_1:
                        x1,y1,node_name_1 = p_1

                        for p_2 in points_2:
                            x2,y2,node_name_2 = p_2
 
                            dist.append( [self.get_distance(point_1=[x1,y1], point_2=[x2,y2]), (x1,y1,tag_1,node_name_1), (x2,y2,tag_2,node_name_2)] )

                    # pick the sorted minimum distance between 2 islands
                    sorted_minimum_dist = sorted(dist, key = lambda x: x[0])[0]

                    each_distance.append(sorted_minimum_dist)

        """
        We are still inside the main outermost loop, now we will have all distances from each point to all other points 
        suppose x1 = 2 and y1 = 3, so each_distances list will contain all distances from these points to all other points, and we will sort them out based on the distances and pick the shortest distance and save it in variable d
        """

        results = []
        distances_for_mst = []
        for dd in each_distance:
            if dd[0] not in results:
                results.append(dd[0])
                distances_for_mst.append(dd)
                
                """Here we add edges to our graph of islands and attribute 'link' as to add extra information to the edge"""
                self.M.add_edge(dd[1][2], dd[2][2], weight = dd[0], link=(dd[1], dd[2]) ) 

        nx.draw(self.M,with_labels = True)
        plt.show(block=False)

        self.mst_islands = nx.minimum_spanning_tree(self.M)
        mst = sorted(self.mst_islands.edges(data=True))

        nx.draw(self.mst_islands ,with_labels = True)
        plt.show(block=False)

        self.mst_for_cist = mst
        
        """We draw the final mst lines, by looping over final-mst-to-draw list
        - we get the stat point, end point and create a line between them"""
        # draw the mst line or see the mst data
        self.mst_line_data = []

        for i in mst:
            start,end = i[2]['link']
            x1,y1,ii1,n1 = start
            x2,y2,ii2,n2 = end

            l = create_line(x1,y1,x2,y2,self.can,tag=(n1,n2), color='green', w=3)
            self.can.tag_lower(l)
            self.mst_line_data.append(l)

        return mst
    # -------------------------------------------

    # Minimum spanning tree----------------------
    def mst(self):
        """This function is similar to mst_for_CIST but this calculates mst on only the three islands set. Here, we create an empty list of mst_distances as seen below and add the distances to this list."""
        # get mst distances
        self.mst_distances = []

        # # draw regions 
        self.T = nx.Graph()

        for i in self.three_islands_set:
            pp,r,clus,color = i
            """
            add islands as node in the graph
            """
            self.T.add_node(clus)

        """We loop over the three island set list, create an empty list of each_distance"""
        each_distance = []
        for each_c1 in self.three_islands_set:
            """unpack our tuple of each island"""
            points_1, r_1, tag_1, color_1 = each_c1

            """Here, we again loop over three islands set list and get the points of other islands"""
            for each_c2 in self.three_islands_set:
                points_2, r_2, tag_2, color_2 = each_c2

                """get the points of that island in x1,y1 and loop over the nodes(points) of that island"""
                if tag_1 != tag_2 :
                    dist = []
                    for p_1 in points_1:
                        x1,y1,name_1 = p_1

                        for p_2 in points_2:
                            x2,y2,name_2 = p_2

                            dist.append( [self.get_distance(point_1=[x1,y1], point_2=[x2,y2]), (x1,y1,tag_1,name_1), (x2,y2,tag_2,name_2)] )

                    # pick the sorted minimum distance between 2 islands
                    sorted_minimum_dist = sorted(dist, key = lambda x: x[0])[0]

                    each_distance.append(sorted_minimum_dist)

        results = []
        distances_for_mst = []

        for dd in each_distance:
            if dd[0] not in results:
                results.append(dd[0])
                distances_for_mst.append(dd)

                """Here we add edges to our graph of islands and attribute 'link' as to add extra information to the edge"""
                self.T.add_edge(dd[1][2], dd[2][2], weight = dd[0], link=(dd[1], dd[2]) ) 

        mst_g = nx.minimum_spanning_tree(self.T)
        mst = sorted(mst_g.edges(data=True))

        self.mst_weight = self.mst_weight_of_triangle(mst)

        return mst

    def mst_weight_of_triangle(self,  mst_dist : list):
        """This function returns, mst weight of the particular triangular subset.
        We consider range as 100"""
        
        # for triangular 
        # print(mst_dist)
        # |uv/r| + |uw/r| - 2
        # ceil step function for x

        """Check if mst_distance list contains more than 1 item which means one node has more 
        than one connection and calculate weight accordingly"""
        if len(mst_dist) > 1:

            uv = mst_dist[0][2]['weight']
            uw = mst_dist[1][2]['weight']
            
            self.mst_weight_triangle = math.ceil(abs(uv)/self.range) + math.ceil(abs(uw)/self.range) - 2 
            return self.mst_weight_triangle

        else:

            uv = mst_dist[0][2]['weight']
            self.mst_weight_of_path = math.ceil(abs(uv)/self.range) - 1 
            return self.mst_weight_of_path

    # -----------------------------
    # Steiner points and steiner minimum tree
    def smt(self):
        """This function calculates the smt data of three islands set"""

        regions = []

        """We create an empty list named regions, and loop over the three island set,
        get the points and island information in variable tag_1 by unpacking the tuple.
        we create an empty dictionary named cluster_points and add the island number and points to the dictionary."""
        # # consider only 3 islands for now
        for each_c1 in self.three_islands_set:
            cluster_points = {} 

            points_1, r_1, tag_1, color_1 = each_c1
            cluster_points['cluster'] = tag_1
            cluster_points['points'] = []

            """We get the points of the island and add that to the cluster 
            points dictionary key 'points' which is initiated as list just above"""
            for p_1 in points_1:
                x1,y1,name_1 = p_1
                cluster_points['points'].append((x1,y1,name_1))
            
            """finally we add the cluster points details to the regions list we created in
            beginning of this function"""
            regions.append(cluster_points)
        
        """We create another empty list of full_triangle where we add the triangular points
        of all the three islands"""

        self.full_triangle = []

        if len(regions) == 3:
            
            """The following loop considers all three islands and checks if they are not same as they are in the inside loops and when we get a combination we sorted the points and append it to the full_triangle list above"""
            for each_i in regions:

                for each_j in regions:
                    if each_i['cluster'] != each_j['cluster']:

                        for p1 in each_i['points']:
                            for p2 in each_j['points']:
                                
                                for each_k in regions:
                                    if each_i['cluster'] != each_k['cluster'] and each_j['cluster'] != each_k['cluster']:

                                        for p3 in each_k['points']:

                                            t = []
                                            t.append(p1)
                                            t.append(p2)
                                            t.append(p3)
                                            t.append((each_i['cluster'], each_j['cluster'], each_k['cluster']))

                                            self.full_triangle.append(sorted(t))

                                    else:
                                        break
                    else:
                        break
        
            """We then find the steiner_points and distances of the points/nodes from each of
            the three islands and save it variable sp which is steiner point"""
            sp = self.find_steiner_points_and_distance()
            
            """We then pick the minimum steiner distance and calculate the SMT-weight
            of that distance using the smt-weight-of-triangle function"""
   

            weight_data = []
            for mini in sp:
                self.smt_weight, sp_data = self.smt_weight_of_triangle(mini)
                weight_data.append((self.smt_weight, sp_data))
            
            sorted_weight_data = sorted(weight_data, key = lambda x: x[0])
            minimum_smt_dist = sorted_weight_data[0][1]
            self.smt_weight = sorted_weight_data[0][0]

            return minimum_smt_dist

        else:
            minimum_smt_dist = None
            return minimum_smt_dist
    
    def smt_weight_of_triangle(self, sp_data : dict):
        """This function calculates the SMT-weight of triangular subset. We provide this
        function with the dictionary with minimum distance as argument"""

        """We consider the range as 100,
        get the 3 points we have from dictionary
        get the steiner point
        calculate the weight and save it in self.mst_weight_triangle variable"""

        coords = sp_data['coords']
        sp_point = sp_data['steiner_point']

        point1, point2, point3 = coords
        sp_x, sp_y = sp_point

        us = self.get_distance( point_1 = (point1[0], point1[1]), 
                                point_2 = (sp_x, sp_y) )

        vs = self.get_distance( point_1 = (point2[0], point2[1]), 
                                point_2 = (sp_x, sp_y) )

        ws = self.get_distance( point_1 = (point3[0], point3[1]), 
                                point_2 = (sp_x, sp_y) )
        
        self.smt_weight_triangle = math.ceil(abs(us)/self.range) + math.ceil(abs(vs)/self.range) + math.ceil(abs(ws)/self.range) - 2
        #print(self.smt_weight_triangle)
        return (self.smt_weight_triangle, sp_data)

    def find_steiner_points_and_distance(self):
        """This function returns the steiner point and the distance"""

        """We create empty list all_sp known as all_steiner_points and then we loop
        over the full_triangle list we have"""
        all_sp = []

        for ft_points in self.full_triangle:
            sp_with_coords = {}
            
            """We"""
            islands, point_1, point_2, point_3  = ft_points
            # point_1, point_2, point_3, islands  = ft_points

            sp_point = steiner.steiner_point( (point_1[0], point_1[1]), 
                                            (point_2[0], point_2[1]), 
                                            (point_3[0], point_3[1]) )
            sp_x = sp_point[0]
            sp_y = sp_point[1]

            # now we have our steiner points
            # we need to find us, vs, ws and add them up according to ppt formula

            d1 = self.get_distance(point_1 = (point_1[0],point_1[1]), 
                                    point_2 = (sp_x,sp_y))

            d2 = self.get_distance(point_1 = (point_2[0], point_2[1]), 
                                    point_2 = (sp_x,sp_y))

            d3 = self.get_distance(point_1 = (point_3[0], point_3[1]), 
                                    point_2 = (sp_x,sp_y))
            # print(d1, d2, d3)
            total_dist = d1 + d2 + d3

            sp_with_coords['island_set'] = tuple(sorted(islands))
            sp_with_coords['coords'] = [point_1, point_2, point_3]
            sp_with_coords['steiner_point'] = (sp_x, sp_y)
            sp_with_coords['smt_distance'] = total_dist

            all_sp.append(sp_with_coords)
        
        all_sp = sorted(all_sp, key = lambda x : x['smt_distance'])

        return all_sp

    # -----------------------------
    # check Gain and then make lines
    def net_gain(self):

        self.gain = self.mst_weight - self.smt_weight

        # print(f"MST weight = {self.mst_weight}")
        # print(f"SMT weight = {self.smt_weight}")
        
        if self.gain > 0 :
            return ('SMT', self.gain)
        elif self.gain < 0 or self.gain == 0 :
            return ('MST', self.gain)
    # ------------------------------

    #  form triangular subsets of islands using MST
    def form_triangular_subsets(self):
        """
        to form triangular subsets of linked islands, 
        since, we are having non-cyclic graph, we form non-repeating 
        combinations of 3 islands using the MST data as blueprint
        This is called a triad, where 3 nodes are connected,
        we are considering 3 nodes connected with 2 edges between them,
        """

        """
        This line creates networkX graph 'self.M' and connects all 
        the nodes(islands) according to their connection links,
        once we initiate the 'graph M' then we can form our triads,
        that is triangular subsets with 2 edges between 3 nodes according
        to our MST data
        """
        mst_for_cist = self.mst_for_CIST()

        triad_class = {}
        for nodes in combinations(self.mst_islands.nodes, 3):
            n_edges = self.mst_islands.subgraph(nodes).number_of_edges()
            if n_edges == 2:
                triad_class.setdefault('triangular_subsets', []).append(tuple(sorted(nodes)))
        
        # form triangular subsets of islands------------
        self.triangular_subset_of_islands = []
        self.triangular_subset_of_islands = triad_class['triangular_subsets']

        return self.triangular_subset_of_islands
    # ---------------------------------
    def check_for_repeating_gain(self, sorted_gain: list):
        """To check multiple same gain, and pick the one which has lowest distance"""
        same_gain_set = []
        set_and_distances = []

        # print(sorted_gain)
        gain_value = sorted_gain[0][1]
        same_gain_set.append(sorted_gain[0])

        for count in range(1, len(sorted_gain)):
            if sorted_gain[count][1] == gain_value :
                same_gain_set.append(sorted_gain[count])

        for counter, i in enumerate(same_gain_set):
            
            self.three_islands_set = i[2]

            smt_data = self.smt()
        
            set_and_distances.append((counter, smt_data))
        
        p = sorted(set_and_distances, key = lambda x: x[1]['smt_distance'])

        return same_gain_set[ p[0][0] ]

    # check their gain and Connect
    def check_gain_triangular_subsets(self):
        """
        Here we check the gain for each triangular subset we formed,
        pick the highest gain and form SMT connection for those nodes,
        then remove the subsets which has islands of the SMT formed,
        since we will be considering it as one island now, then pick highest gain for next subset and continue the process
        untill we connect all islands 
        """    
        print("\n*************************************************************** CIST Algorithm *****************************************************************\n")

        # make a new graph with islands as nodes to connect them accordingly

        t_sets = self.form_triangular_subsets()
        t_sets_2 = copy(t_sets)
        print("List of Triangular subsets according to the MST connection:", t_sets)
        print("------------------------------------------------------------------------------------------------------------------------------------------------")

        while len(t_sets) != 0:

            gain_sets = []
            terminal_display_gain = []
            for each_set in t_sets:

                """Make three islands set as an empty list and we will add 
                three islands in this list on which we will calculate MST and SMT 
                calculate their gain"""

                self.three_islands_set = []

                # get island information for subset 
                """ This will have three islands in i1,i2,i3,
                and we will loop over separate islands where we have all the island information
                and check if those islands are same as these three islands"""
                i1,i2,i3 = each_set

                for each_island in self.separate_islands:
                    # print(each_island)
                    pp,r,island,color = each_island

                    if i1 == island or i2 == island or i3 == island:
    
                        """If they are same then we add them to three island list"""
                        self.three_islands_set.append(each_island)

                """Then we calculate gain of those three islands which calculates MST and SMT
                first in that function and returns tree value = 'MST' or 'SMT', their gain and the islands set"""
                # check gain for each set
                g = self.check_gain(self.three_islands_set)
                tree, gain, island_set = g

                # print(f"\n{i1},{i2},{i3} gain = {gain}\n")
                islands = (i1,i2,i3)
                obj_1 = {
                            'Subset': islands,
                            'Gain': gain
                        }
                terminal_display_gain.append(obj_1)
                gain_sets.append(g)
            
            print(f"\nTriangular island subset with their Gain: {terminal_display_gain}\n")

            sorted_gain_set = sorted(gain_sets, key=lambda x:x[1], reverse=True)

            highest_gain_value = self.check_for_repeating_gain(sorted_gain_set)

            # highest_gain_value = sorted_gain_set[0]

            # clear three island set
            tree, gain_val, triangle_set = highest_gain_value

            # add those islands to three island set
            self.three_islands_set = triangle_set

            # check if gain is positive
            if gain_val >= 1:

                smt_data = self.smt()
                
                self.draw_MST_or_SMT('SMT', smt_data, highest_gain_value)
                
                i1 = i2 = i3 = 0
                
                for counter,i_info in enumerate(triangle_set):
                    if counter == 0 :
                        i1 = i_info[2]
                    elif counter == 1:
                        i2 = i_info[2]
                    elif counter == 2:
                        i3 = i_info[2]

                for val in t_sets_2[:]:
                    if (i1 in val and i2 in val) or (i2 in val and i3 in val) or (i1 in val and i3 in val) :
                        t_sets_2.remove(val)
                        t_sets = t_sets_2

                # remove the connection from initial MST------------
                for each_line in self.mst_for_cist:

                    if (i1 in each_line and i2 in each_line) or (i2 in each_line and i3 in each_line) or (i1 in each_line and i3 in each_line) :
                        
                        island_1, island_2, connection_info = each_line

                        start_p, end_p = connection_info['link']
                        start_node = start_p[3] 
                        end_node = end_p[3]

                        for l in self.mst_line_data:
                            tags = self.can.gettags(l)
                            if tags:
                                start_to_remove, end_to_remove = tags
                                if start_to_remove == start_node and end_to_remove == end_node:
                                    self.can.delete(l)
            
            else:

                # draw MST
                mst_data = self.mst()

                self.draw_MST_or_SMT('MST', mst_data, highest_gain_value)

                i1 = i2 = i3 = 0
                
                for counter,i_info in enumerate(triangle_set):
                    if counter == 0 :
                        i1 = i_info[2]
                    elif counter == 1:
                        i2 = i_info[2]
                    elif counter == 2:
                        i3 = i_info[2]

                for val in t_sets_2[:]:
                    if (i1 in val and i2 in val) or (i2 in val and i3 in val) or (i1 in val and i3 in val) :
                        t_sets_2.remove(val)
                        t_sets = t_sets_2

        # add repair resources for MST 
        for data in self.mst_line_data:
            t = self.can.gettags(data)
            if len(t) != 0:
                s_tag, e_tag = t
        
                for each_l in self.mst_for_cist:
                    ii1,ii2,data = each_l
                    s_data, e_data = data['link']

                    if s_data[3] == s_tag and e_data[3] == e_tag :
                        
                        x1,y1,isl1,n1 = s_data
                        x2,y2,isl2,n2 = e_data

                        dist, repair_nodes = self.get_repair_resources((x1,y1), (x2,y2))
                        if repair_nodes == 0:
                            repair_nodes = 1
                        xr = np.linspace(x1,x2,repair_nodes+1,endpoint=False)
                        yr = np.linspace(y1,y2,repair_nodes+1,endpoint=False)

                        self.draw_repair_resources(zip(xr,yr))

        # -----------------------------------
        # get all PS nodes which are inside repair-resource nodes
        data_rr = check_ps_in_range(self.repair_resources, self.power_nodes, 'rr')

        total_PS_nodes_connected_in_RR = set()
        total_PS_nodes_connected_in_ICT = set()
        total_PS_nodes_not_connected = set()

        for each_data in data_rr:
            ps_name = each_data['ps'] 
            total_PS_nodes_connected_in_RR.add(ps_name)
            for each in self.power_circles:
                t = self.can.gettags(each)
                if len(t) != 0 :
                    if ps_name == t[0]: 
                        self.can.itemconfig(each, fill='#41fdfe')

        # get all PS nodes which are inside ICT nodes
        data_ict = check_ps_in_range(self.nodes_on, self.power_nodes, 'ict')
        for each_data in data_ict:
            ps_name = each_data['ps']
            total_PS_nodes_connected_in_ICT.add(ps_name)
            if ps_name in total_PS_nodes_connected_in_RR:
                total_PS_nodes_connected_in_RR.remove(ps_name)
            for each in self.power_circles:
                t = self.can.gettags(each)
                if len(t) != 0 :
                    if ps_name == t[0]:
                        self.can.itemconfig(each, fill='#406bd6')
        # ------------------------------------

        # check PS-nodes which are not connected and add to not-connected set
        for nodes in self.power_nodes:
            ps_name = nodes['power_node_name']
            if (ps_name not in total_PS_nodes_connected_in_RR) and (ps_name not in total_PS_nodes_connected_in_ICT):
                total_PS_nodes_not_connected.add(ps_name)
                for each in self.power_circles:
                    t = self.can.gettags(each)
                    if len(t) != 0 :
                        if ps_name == t[0]:
                            self.can.itemconfig(each, fill='grey')
    
        # to remove duplicate repair resource from repair_resources
        coords_check = []
        final_repair_resources_data = []
        for item in self.repair_resources:
            if item['coords'] not in coords_check:
                coords_check.append(item['coords'])
                final_repair_resources_data.append(item)

        print("\nFor restoring disjointed ICT network connectivity using CIST Algorithm:")
        print(f"\nTotal number of Repair Resources (RRs) required = {len(final_repair_resources_data)}")
        print(f"Total number of extra Power Systems (PSs) connected through RRs = {len(total_PS_nodes_connected_in_RR)}\n")

        print("************************************************************* Program ends here ****************************************************************")

        # ********remove duplicates from data-2 file for optimization*******

        # zoom_button activate
        self.zoom_button.config(state=NORMAL)

        # a_long = ( ( x_y[0][0] * (self.long_max - self.long_min)) / 800 ) + self.long_min
        # a_lat = ( ( (self.lat_max - self.lat_min) * (self.lat_max - x_y[0][1]) ) + (800 * self.lat_min) ) / 800 
        # create a directory called psa data

        dir_loc = os.getcwd()
        files_present = os.listdir(dir_loc)
        if 'cist_data' in files_present :
            shutil.rmtree('cist_data')
        os.mkdir('cist_data')

        with open('cist_data/RR_for_CIST.csv', 'w+', newline='') as f:
            fieldnames = ["Name", "Longitude", "Latitude"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            # remove duplicates
            seen = set()
            new_l = []
            for d in self.repair_resources:
                t = tuple(d.items())
                if t not in seen:
                    seen.add(t)
                    new_l.append(d)
            self.repair_resources = new_l

            # write to file
            for counter,i in enumerate(self.repair_resources):
                x,y = i['coords']
                x = -x

                lon = ( ( y * (self.long_max - self.long_min)) / 800 ) + self.long_min
                lat = ( ( (self.lat_max - self.lat_min) * (self.lat_max - x) ) + (800 * self.lat_min) ) / 800 
                writer.writerow({"Name" : f"CIST_RR_{counter+1}",
                                "Longitude" : lon,
                                "Latitude" : lat
                                })

        save_in_map(self.ict_content, self.ict_node_off, self.psb_content)
        
    # _______________________________________________________ 

    def check_gain(self, three_islands_set:list):
        """This function calculates gain of three islands, using mst and smt functions,
        we save that in mst_data and smt_data respectively. This function returns a tuple of
        which minimum tree connection, gain value and three island set"""
        mst_data = self.mst()
        smt_data = self.smt()

        """Once we have their data, we calculate the gain using net_gain() function
        which returns 'MST or SMT' as which minimum tree and gain_value respectively"""
        
        which_minimum_tree, gain_value = self.net_gain()
        
        return (which_minimum_tree, gain_value, three_islands_set)

    def get_repair_resources(self,point1:tuple, point2:tuple):
        """Calculate repair resources"""
        
        repair_resource_distance = self.get_distance( point1, point2 )
        repair_resources = math.ceil(abs(repair_resource_distance)/self.range) - 1

        return (repair_resource_distance, repair_resources)
    
    def draw_repair_resources(self, points:tuple):
        """Draw repair resources"""
        # we will use this self.repair resources list further, for our calculations
        # self.repair resources have been initialized in the beginning of the GUI with range 

        for index,i in enumerate(points):

            self.repair = {}

            if index != 0 :

                xr,yr = i
                
                rr = create_circle(xr, yr, 5, self.can, tag=('repair_resources'), color='purple')
                self.repair['coords'] = (xr,yr)

                range_of_rr = create_region(xr, yr, self.range, self.can, tag=('range_of_rr'), color='purple', w=1)
                self.can.tag_lower(range_of_rr)

                self.repair['range'] = self.range
                
                self.repair_resources.append(self.repair)

        return 0
      
    def draw_MST_or_SMT(self, tree: str, data_tree, highest_g_value):
       
        # # # draw  MST lines
        if tree == 'MST':
            i1=i2=i3=0
            for counter,i in enumerate(highest_g_value[2]):
                if counter == 0:
                    i1 = i[2]
                elif counter == 1:
                    i2 = i[2]
                elif counter == 2:
                    i3 = i[2]

            print(f"Highest gain = {highest_g_value[1]} which is not a positive gain for triangular subset: ({i1},{i2},{i3}). Hence, connecting these islands via MST edges.")

            for d in data_tree:
                n1,n2 = d[2]['link']
                node1 = n1[3]
                node2 = n2[3]
                print(f"MST link between Islands: {d[0]} and Island: {d[1]}")
                print(f"Connecting BS nodes: {node1} and {node2}")

            print("------------------------------------------------------------------------------------------------------------------------------------------------")


            for data in data_tree:

                start_point = data[2]['link'][0]

                x1,y1,cluster1,name1 = start_point
                
                end_point = data[2]['link'][1]
                x2,y2,cluster2,name2 = end_point

                # get repair nodes
                dist, repair_nodes = self.get_repair_resources((x1,y1), (x2,y2))
                if repair_nodes == 0:
                    repair_nodes = 1
                # draw repair resources
                xs = np.linspace(x1,x2,repair_nodes+1,endpoint=False)
                ys = np.linspace(y1,y2,repair_nodes+1,endpoint=False)
                self.draw_repair_resources(zip(xs,ys))

                m_lines = create_line(x1,y1,x2,y2, self.can, tag=('mst_lines'), color='green',w=3)
                self.can.tag_lower(m_lines)

        # # draw SMT lines
        elif tree == 'SMT':
            # To show the data in terminal
            # print('draw SMT', data_tree, highest_g_value)
            s1,s2,s3 = data_tree['coords']
            s11,s12,node1 = s1
            s21,s22,node2 = s2
            s31,s32,node3 = s3

            i1=i2=i3=0
            for counter,i in enumerate(highest_g_value[2]):
                if counter == 0:
                    i1 = i[2]
                elif counter == 1:
                    i2 = i[2]
                elif counter == 2:
                    i3 = i[2]

            print(f"Highest gain = {highest_g_value[1]} which is a positive gain for triangular subset: ({i1},{i2},{i3}). Hence, connecting these islands via SMT edges.")
            print(f"SMT link between Islands: {node1}, {node2}, and {node3}")
            print("------------------------------------------------------------------------------------------------------------------------------------------------")

            spx, spy = data_tree['steiner_point']
             
            show_or_hide_steiner = check_rr_in_range_of_bs(data_tree, self.ict_content)
            
            if show_or_hide_steiner == None:
                rr = {}
                steiner_range = create_region(spx, spy, self.range, self.can, tag=('steiner_point'),color='purple', w=1)
                self.can.tag_lower(steiner_range)
                rr['coords'] = (spx,spy)
                rr['range'] = self.range

                self.repair_resources.append(rr)

                create_circle(spx,spy,6,self.can,tag=('steiner_point'),color='purple')
                
                coord_points = data_tree['coords']
                
                for each_point in coord_points:
                
                    x,y,name = each_point
                    
                    # get repair nodes
                    dist, repair_nodes = self.get_repair_resources((x,y), (spx,spy))

                    # draw repair resources
                    xs = np.linspace(x,spx,repair_nodes+1,endpoint=False)
                    ys = np.linspace(y,spy,repair_nodes+1,endpoint=False)
                    self.draw_repair_resources(zip(xs,ys)) 

                    s_line = create_line(x,y,spx,spy,self.can,tag=('smt_lines'),color='green',w=3)
                    self.can.tag_lower(s_line)  
            
            else:

                coord_points = data_tree['coords']
                
                for each_point in coord_points:
                
                    x,y,name = each_point
                    
                    # get repair nodes
                    dist, repair_nodes = self.get_repair_resources((x,y), (spx,spy))

                    # draw repair resources
                    xs = np.linspace(x,spx,repair_nodes+1,endpoint=False)
                    ys = np.linspace(y,spy,repair_nodes+1,endpoint=False)
                    self.draw_repair_resources(zip(xs,ys)) 

                    s_line = create_line(x,y,spx,spy,self.can,tag=('smt_lines'),color='green',w=3)
                    self.can.tag_lower(s_line) 

    # clear the canvas screen and terminal---------------------
    def reset_screen(self):
        """Operates on reset button,
        clears the terminal screen and the canvas screen as well as 
        removes the nx graph information"""

        self.connect_nodes.config(state=DISABLED)
        self.zoom_button.config(state=DISABLED)
        self.psb_button.config(state=DISABLED)

        self.power_nodes = []
        self.power_circles = []
        self.repair_resources = []

        self.can.delete('all') 

        self.G.clear()
        if self.M :
            self.M.clear()
        if self.T :
            self.T.clear()

        clear()


# =========================
if __name__ == "__main__":
    window = GUI()
    window.mainloop()
