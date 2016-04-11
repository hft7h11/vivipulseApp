# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 15:12:09 2016
Updated on Sun Apr 10
Version = 0.2
@author: zhen

Update note:
Connecting to Bluetooth device and receive streams of data enabled
"""

import os
import sys
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from math import sin
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.garden.graph import MeshLinePlot
from functools import partial
import random
import time
from jnius import autoclass

BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
InputStreamReader = autoclass('java.io.InputStreamReader')
BufferedReader = autoclass('java.io.BufferedReader')
UUID = autoclass('java.util.UUID')
# Create a listener function
class ViViChart(Widget):
    paired_device = StringProperty('No Paired Device')
    n_paired_devices = NumericProperty(0)
    data = StringProperty(0)
    #exception = StringProperty(None)
    
    def __init__(self):
        super(ViViChart, self).__init__()
        graph_theme = {'background_color': 'f8f8f2'}
        self.graph = self.ids.graph
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot.points = []
        self.graph.add_plot(self.plot)
        self.start = time.time()
    
    def discover(self):
        paired_devices = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        btns = []
        for device in paired_devices:
            btns.append(Device(text = device.getName()))
        return btns
        '''
            if device.getName() == 'MDR-XB950BT':
                socket = device.createRfcommSocketToServiceRecord(
                    self.UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
                recv_stream = socket.getInputStream()
                self.paired_device = 'MDR-XB950BT'
                break
        socket.connect()
        '''
    
    def search_for_devices(self):
        self.popup=Popup(title='Paired devices', size_hint = [0.8, 0.8],
                         on_open=self.ids.popup2.dismiss)
        btns = self.discover()
        popup_grid = GridLayout(rows = len(btns))
        for btn in btns:        
            popup_grid.add_widget(btn) 
        self.popup.add_widget(popup_grid)
        self.popup.open()
        #return recv_stream
        #return len(paired_devices)#, recv_stream
    
    def update(self, outfile, dt):
        # Plot data in real time
        self.graph.remove_plot(self.plot)
        self.plot.points = [( x, sin(x / 10.)) for x in range(0, int(200*random.random()) )] # This is just some mock data
        self.graph.add_plot(self.plot)
        try:
            recv_stream = BufferedReader(InputStreamReader(BluetoothSocket.getInputStream(), 'utf-8'))
            #self.data = 1
        except Exception:
            #self.data = 2
            pass
        #self.paired_device = self.get_socket_stream()
        #self.n_paired_devices = self.get_socket_stream()
        # Data logging
        now = time.time() - self.start # Generate a time stamp
        try:
            self.data = recv_stream.readLine()
            outfile.write(str(now) + "," + str(self.data)  + "\n")
            sys.stdout.write(".")
            sys.stdout.flush()
            #self.DataHandler(self, outfile)
        except Exception:
            #self.data = 100
            pass
        
class Device(Button):
    def on_release(self):
        paired_devices = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        for device in paired_devices:
            if device.getName() == self.text:
                socket = device.createRfcommSocketToServiceRecord(
                    UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
                break
        try:
            socket.connect()
        except Exception:
            pass
            
class Exception_popup(Popup):
    pass

class ViViTestApp(App):
    def build(self):
        # Clear and open the data file for writing
        outfile = open(self.user_data_dir + "/vivipulse_data.csv", "w")
        # Write a header to the text file first thing
        outfile.write("Time, Data\n")
        chart = ViViChart()
        Clock.schedule_interval(partial(chart.update, outfile), 1.0/100)
        return chart
     
    def exit(self):
        exit()

if __name__ == '__main__':
    ViViTestApp().run()