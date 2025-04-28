"""
A simple program to read IMU data at approx.50Hz from the Arduino Nano 33 IOT board.
"""

import asyncio
import sys
from typing import Dict
from datetime import datetime
import numpy as np
import pandas as pd

from bleak import BleakClient
from bleak import discover
from bleak import BleakScanner


# These values have been randomly generated - they must match between the Central and Peripheral devices
# Any changes you make here must be suitably made in the Arduino program as well
IMU_UUID = '13012F01-F8C3-4F4A-A8F4-15CD926DA146'

# Class for handling BLE communication with a Nano board for receiving IMU data.
class NanoIMUBLEClient(object):
    
    def __init__(self, uuid:str, csvout:bool=False) -> None:
        super().__init__()
        self._client = None
        self._device = None
        self._connected = False
        self._running = False
        self._uuid = uuid
        self._found = False
        self._data = np.zeros(7, dtype=np.float32)
        self._csvout = csvout 
        self.newdata = False
        self.debug = False
        self._records = np.array([])#np.zeros(7, dtype=np.float32)
        self.printdata = True
        self.starttime = datetime.now().strftime("_%m%d%Y_%H%M%S")
        self.csvfile = open(f"out{self.starttime}.csv", 'w', newline='')
    
    @property
    def connected(self) -> bool:
        return self._connected
    
    @property
    def data(self):
        return self._data

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def running(self) -> bool:
        return self._running
    
    @property
    def device(self):
        return self._device
    
    async def connect(self) -> None:
        if self._connected:
            return
        
        # Currently not connected.
        print('Arduino Nano IMU Service')
        print("- Discovering peripheral device...")
        device = await BleakScanner.find_device_by_filter(lambda d, ad: d.name == "Arduino Nano 33 BLE", timeout=1)
        
        if device:
            print("* Peripheral device found!")
            print(f"* Device address: {device.address}")
            print(f"* Device name: {device.name}")
            self._found = True
            self._device = device
            # Connect and do stuff.
            async with BleakClient(device.address) as self._client:
                sys.stdout.write(f'Connected.\n')
                self._connected = True
                # Start getting data.
                await self.start()
                # Run while connected.
                while self._connected:
                    if self._running:
                        # Print data.
                        if(self.debug): print(f"self.newdata: {self.newdata}")
                        if self.printdata and self.newdata:
                            self.print_newdata()
                            self.record_newdata()
                            self.newdata = False
                    else:
                        print("Not running")
                    await asyncio.sleep(0)
        else:
            print("* No peripheral device found!")
    
    async def disconnect(self) -> None:
        if self._connected:
            # Stop notification first.
            self._client.stop_notify()
            self._client.disconnect()
            self._connected = False
            self._running = False
    
    async def start(self) -> None:
        if self._connected:
            # Start notification
            if(self.debug): print("BLE: start notify")
            await self._client.start_notify(self._uuid, self.newdata_hndlr)
            self._running = True
            if(self.debug): print("BLE: running")
    
    async def stop(self) -> None:
        if self._running:
            # Stop notification
            await self._client.stop_notify(self._uuid)
        
    def newdata_hndlr(self, sender, data):
        self._data[:] = np.frombuffer(data, dtype=np.float32, count=7)
        self.newdata = True
        if(self.debug): print(f"receiving newdata: {self._data[0]}")
    
    def record_newdata(self) -> None:
        sample_count = int(self._records.size/self._data.size);
        freq = 0
        if(self._records.size):
            self._data[0] = (self._data[0] - self._start_recording_time) * 1E-3
            self._records = np.vstack((self._records, self._data))
            freq = sample_count/self._data[0]
        else:
            self._records = self._data
            self._start_recording_time = self._data[0]
            self._data[0] = 0
        sys.stdout.write(f"\rsample count: {sample_count}\tdata rate: {round(freq)} Hz")
        sys.stdout.flush()
    
    def print_newdata(self) -> None:
        if self._csvout:
            _str = (f"{self.data[0]*0.001:+3.3f}, " +
                    f"{self.data[1]:+1.3f}, " + 
                    f"{self.data[2]:+1.3f}, " + 
                    f"{self.data[3]:+1.3f}, " +
                    f"{self.data[4]:+3.3f}, " +
                    f"{self.data[5]:+3.3f}, " +
                    f"{self.data[6]:+3.3f}\n")
            self.csvfile.write(_str)
        else:
            _str = (f"\r Time: {self.data[0]*0.001:+3.3f} | " +
                    "Accl: " +
                    f"{self.data[1]:+1.3f}, " + 
                    f"{self.data[2]:+1.3f}, " + 
                    f"{self.data[3]:+1.3f} | " +
                    "Gyro: " +
                    f"{self.data[4]:+3.3f}, " +
                    f"{self.data[5]:+3.3f}, " +
                    f"{self.data[6]:+3.3f}")
            sys.stdout.write(_str)
            sys.stdout.flush()
            
    def write_records_to_csv(self) -> None:
        starttime = datetime.now().strftime("_%m%d%Y_%H%M%S")
        filename = f"out{starttime}.csv"
        print(f"Write records to file {filename}")
        np.savetxt(filename, self._records, delimiter=',', fmt='%3.3f',
                   header="time,ax,ay,az,gx,gy,gz", comments='')
        
    def write_records_to_excel(self) -> None:
        starttime = datetime.now().strftime("_%m%d%Y_%H%M%S")
        filename = f"out{starttime}.xlsx"
        print(f"Write records to file {filename}")
        #df = pd.DataFrame.from_records(self._records)
        print(self._records)
        df = pd.DataFrame(self._records, columns=['time','ax','ay','az','gx','gy','gz'])
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            df.to_excel(writer)
        

imu_client = NanoIMUBLEClient(uuid=IMU_UUID, csvout=True)
async def run():
    # Create a new IMU client.
    global imu_client
    await imu_client.connect()


if __name__ == "__main__":
    # First create an object
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run())
        print("sdgdsag")
    except KeyboardInterrupt:
        print('\nReceived Keyboard Interrupt')
        imu_client.write_records_to_excel()
    finally:
        print('Program finished')

