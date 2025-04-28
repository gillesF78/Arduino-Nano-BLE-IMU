# Arduino-Nano-BLE-IMU
Simple demonstration of streaming IMU data from the Arduino Nano 33 IOT module to a PC.

Example of usage: (press CTRL+C to stop acquisition)
````{verbatim}
>>> %Run nanobleimu.py
Arduino Nano IMU Service
- Discovering peripheral device...
* Peripheral device found!
* Device address: 63:C3:29:BF:C2:6A
* Device name: Arduino Nano 33 BLE
Connected.
sample count: 470	data rate: 52 Hz
Received Keyboard Interrupt
Write records to file out_04282025_170858.xlsx
[[ 1.4000000e-02 -2.1972656e-03  1.3122559e-01 ...  7.9345697e-01
   6.1035153e-02  4.2724606e-01]
 [ 1.4000000e-02 -2.1972656e-03  1.3122559e-01 ...  7.9345697e-01
   6.1035153e-02  4.2724606e-01]
 [ 3.0000001e-02 -2.6855469e-03  1.3049316e-01 ...  7.9345697e-01
   6.1035153e-02  3.6621091e-01]
 ...
 [ 8.9370003e+00 -1.8310547e-03  1.3073730e-01 ...  7.9345697e-01
   6.1035153e-02  4.2724606e-01]
 [ 8.9660006e+00 -1.9531250e-03  1.3208008e-01 ...  8.5449213e-01
   0.0000000e+00  4.2724606e-01]
 [ 8.9820004e+00 -1.9531250e-03  1.3146973e-01 ...  8.5449213e-01
   0.0000000e+00  3.0517578e-01]]
Program finished
````

