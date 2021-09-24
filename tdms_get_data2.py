# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 10:09:05 2021

@author: ShendR


"""

from nptdms import TdmsFile      # 0.18.1 version
import numpy as np
import matplotlib.pyplot as plt


class SPI_tDMS_Data(object):
    def __init__(self, file):
        self.channels = []
        self.groups = []
        self.root_obj_keys=[]
        self.root_obj_values=[]
        self.tdms_file = self.run_open_tdms()
        self.time_sec = self.time_convert()
            
    
    def run_open_tdms(self):
        self.tdms_file = TdmsFile(file)        
            # Get basic info from file
        root_object=self.tdms_file.object()
        root_properties=root_object.properties.items()
        for key, value in root_properties:
            self.root_obj_keys.append(key)
            self.root_obj_values.append(value)
            
            # Get Channels names from file Groups
        self.groups = self.tdms_file.groups()    
        channel_list = self.tdms_file.group_channels(self.groups[0])
        for c in channel_list:
            self.channels.append(c.channel)
                    
        return self.tdms_file
    
    
        # Get data and unit from tdms file in to numpy array
    def get_data_nparray(self, channel='TimeStamp'):
        channels_data = self.tdms_file.object(self.groups[0], channel)
        data = channels_data.data
        unit = channels_data.property('Unit') #-------------Unit
        nparray = np.array(data)
        return [nparray, unit]
    
    
        # Shows how long was the measurement
    def measurement_length(self):
        time_array = self.get_data_nparray()[0]
        time_length = time_array[-1]-time_array[0]
        time_length_item = time_length.item()
        time_length_sec = time_length_item.seconds
        print("Measurement start: {}".format(time_array[0]))
        print("Measurement length is {}".format(str(time_length)))
        print("Measurement length is {} seconds".format(str(time_length_sec)))
 

        # Converts and saves datetime64 into u-seconds - self.time_sec       
    def time_convert(self):
        time_array = self.get_data_nparray()[0]
        time_sec = []
        for i in range(len(time_array)):
            a = time_array[i] - time_array[0]
            b = a.astype(float)/1000000
            time_sec.append(b)
        return time_sec
    
    
        # Get the index of TimeStamp from time list
    def get_time_index(self, time_val=None):
        if time_val == None:
            index = self.time_sec.index(self.time_sec[-1]) + 1
        else:
            closest_val = min(self.time_sec, key=lambda x: abs(x - time_val))
            index = self.time_sec.index(closest_val)
        return index
    
    
        # Get tdms data (with unit) from a time window - from_t to to_t
    def get_data_interval(self, from_t=None, to_t=None, channel='TimeStamp'):
        if from_t == None:
            from_time = 0
        else:
            from_time = self.get_time_index(from_t)
        if to_t == None:
            to_time = self.get_time_index()
        else:
            to_time = self.get_time_index(to_t)
        if channel == "TimeStamp":
            data = self.time_sec[from_time:to_time]
            unit = 's'
        else:
            data = self.get_data_nparray(channel)[0][from_time:to_time]
            unit = self.get_data_nparray(channel)[1]
        return [data, unit]


        
        # Plot one channel data in function of time
    def plot_one_channel(self, from_t=None, to_t=None, channel='Cryo Press 1 (PM2)'):
        x_data = self.get_data_interval(from_t, to_t)
        y_data = self.get_data_interval(from_t, to_t, channel)
        plt.plot(x_data[0], y_data[0])
        plt.title(channel)
        plt.xlabel(x_data[1])
        plt.ylabel(y_data[1])
        
        
        # Compare multiple channels data in function of time - max 6 channels
    def plot_multi_ch(self, from_t=None, to_t=None, ch1='Cryo Press 1 (PM2)', ch2='Cryo Press 2 (PM3)', ch3=None, ch4=None, ch5=None, ch6=None):
        dict1 = {}
        channels_data = [ch1, ch2, ch3, ch4, ch5, ch6]
        x_data = self.get_data_interval(from_t, to_t, "TimeStamp")
        for i in channels_data:
            if i != None:
                dict1[i] = self.get_data_interval(from_t, to_t, i)
            else:
                break
                
        channels_no = 0
        for j in channels_data:
            if j != None:
                channels_no+=1
                
        nrow=channels_no
        if channels_no == 2:
            nrow = 2
            ncol = 1
        elif channels_no == 3:
            nrow = 3
            ncol = 1
        elif channels_no == 4:
            nrow = 2
            ncol = 2
        elif channels_no == 5 or 6:
            nrow = 3
            ncol = 2
        else:
            ncol=1
            nrow=channels_no
            
        fig, axes = plt.subplots(nrow, ncol, sharex=True)
        plt.tight_layout()   
        count=0
        for r in range(nrow):
            
            if ncol==1:  
                axes[r].plot(x_data[0], dict1[channels_data[count]][0])
                axes[r].set_xlabel('TimeStamp [s]')
                axes[r].set_ylabel(channels_data[count] + " [" + dict1[channels_data[count]][1] + "]")
                count+=1
            else:
                for c in range(ncol):
                    axes[r,c].plot(x_data[0], dict1[channels_data[count]][0])
                    axes[r,c].set_xlabel('TimeStamp [s]')
                    axes[r,c].set_ylabel(channels_data[count] + " [" + dict1[channels_data[count]][1] + "]")
                    count+=1
        return [dict1, channels_data, x_data, nrow, ncol]

    
            
    # tDMS file - location
file = 'C:\\ShendR\\Python\\SPI tDMS\\TDMS files\\20210901_110529_MonitorData.tdms'    


    # Testing SPI_Data Class methods
spi_data = SPI_tDMS_Data(file)
channels = spi_data.channels
#tdms_filename = spi_data.root_obj_values[0]
#date1 = tdms_filename.split('_')[0]
#shotid = tdms_filename.split('_')[1]
#time_sec = spi_data.time_sec
measurement_length = spi_data.measurement_length()
plot_one_channel = spi_data.plot_one_channel(19000,21000)
multi_plot = spi_data.plot_multi_ch()