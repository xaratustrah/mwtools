'''
This module will work with Vector Network Analyzer ZVL Rohde and Schwarz
connect, set parameters of measurement, get raw data in format
(float) Re(S11) (float) Im(S11) and save data to .txt

06.02.2018 D.Dmytriiev
'''
import socket#to use TCP
import sys
import os
import numpy as np
import datetime

class NetworkAnalyser:

    def __init__(self, cal_filename, host, port=5025, BUFF_SIZE=1, center=407, span=2000, n_points=4001, bandwidth=1.0, power=0.0, average=10, measurement="S11" ):#Initialize object. Socket, adress, everything for start work
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address=host# VNA adress
        self.portnumber=port
        self.BUFF_SIZE=BUFF_SIZE#I want take one symbol per time. TCP destroy every formatting and send bytes
        self.cal_filename=cal_filename
        self.center = center # MHz
        self.span = span  # kHz
        self.n_points = n_points
        self.bandwidth = bandwidth # kHz
        self.power = power #  dBm
        self.average = average #samples for averaging
        self.measurement = measurement #S-parameter we measure

    def connect(self): #connect to NA and tell it about settings and procedures
        self.sock.connect((self.address, self.portnumber)) #connect to VNA
        self.sock.send("@REM".encode('ascii')) # invoke remote mode
        self.sock.send("*RST;*WAI;*CLS".encode('ascii')) # reset everything
        self.sock.send(("CALC:PAR:MEAS 'TRC1','"+self.measurement+"'").encode('ascii'))
        self.sock.send("INIT:CONT OFF".encode('ascii')) # single sweep
        self.sock.send(("SWE:COUN " + str(self.average)).encode('ascii'))
        self.sock.send(("SWE:POIN " + str(self.n_points)).encode('ascii'))
        self.sock.send(("AVER:COUN " + str(self.average)).encode('ascii'))
        self.sock.send("AVER ON".encode('ascii'))
        self.sock.send(("BAND " + str(self.bandwidth) + "KHZ").encode('ascii'))
        self.sock.send(("FREQ:CENT " + str(self.center) + "MHZ").encode('ascii'))
        self.sock.send(("FREQ:SPAN " + str(self.span) + "KHZ").encode('ascii'))
        self.sock.send(("SOUR:POW " + str(self.power)).encode('ascii'))
        self.sock.send(("MMEM:LOAD:CORR 1,"+str(self.cal_filename)).encode('ascii')) # calibration file, to be replaced in every test

    def get_data(self):#get string from TCP, char array to string, split string and convert to floats. Returns float array of data with frequencies
        data = [] #empty array to put symbols in it

        self.sock.send("*WAI;SYST:ERR:ALL?".encode('ascii'))
        self.sock.send("AVER:CLE\n".encode('ascii')) #clean previous frames
        self.sock.send("INIT\n".encode('ascii')) #initiate new cycle
        self.sock.send("*WAI;CALC:DATA? SDAT\n".encode('ascii')) #send data

        tmp = self.sock.recv(self.BUFF_SIZE).decode('ascii')#first symbol in TCP port in non-byte format. Normal number
        data.append(tmp)#add first symbol

        while tmp != '\n':#until the end of the data in TCP
            tmp = self.sock.recv(self.BUFF_SIZE).decode('ascii')
            
            data.append(tmp) #add symbol to array

        data = (''.join(map(str, data))) #create string from char array
        data_array = np.fromstring(data, sep=',')
        data_array = np.reshape(data_array, (int(len(data_array)/2),2))
        freqs= np.linspace(start = self.center - self.span / 2000, stop = self.center + self.span / 2000, num = self.n_points)
        freqs = np.reshape(freqs, (self.n_points, 1))
        data_array = np.append(freqs, data_array, axis=1)
        return data_array

    def save_to_file(self, filename, data_array, touchstone=False):
       
       
        if touchstone:
            filename=filename+'.s1p'
            np.savetxt(filename, data_array, header="""# HZ   S   RI   R     50.0\n! Rohde & Schwarz ZVL\n!\n!\n! """, comments='')     

        else:
            filename=filename+".csv"
            np.savetxt(filename, data_array)     

        return filename
    
    def get_nice_filename(self):#delete datafiles directory
        return  str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        
#--------------

if __name__ == "__main__":

    myvna=NetworkAnalyser('2018-02-01_P1_600Mhz.cal','192.168.254.2')
    myvna.connect()
    print("Filename " + myvna.save_to_file(myvna.get_nice_filename(), myvna.get_data(),touchstone=False)  + " was created")
