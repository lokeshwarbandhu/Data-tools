from struct import unpack
import pyvisa as visa
import numpy as np
import xlsxwriter

rm = visa.ResourceManager()
print(rm)

def acquire(channel, port):
    try:
        scope = rm.open_resource(port)
        scope.write("DATA:SOURCE " + channel)
        scope.write('DATA:WIDTH 1')
        scope.write('DATA:ENC RPB')
        ymult = float(scope.query('WFMPRE:YMULT?'))
        yzero = float(scope.query('WFMPRE:YZERO?'))
        yoff = float(scope.query('WFMPRE:YOFF?'))
        xincr = float(scope.query('WFMPRE:XINCR?'))
        xdelay = float(scope.query('HORizontal:POSition?'))
        scope.write('CURVE?')
        data = scope.read_raw()
        headerlen = 2 + int(data[1])
        header = data[:headerlen]
        ADC_wave = data[headerlen:-1]
        ADC_wave = np.array(unpack('%sB' % len(ADC_wave),ADC_wave))
        Volts = (ADC_wave - yoff) * ymult  + yzero
        Time = np.arange(0, (xincr * len(Volts)), xincr)-((xincr * len(Volts))/2-xdelay)
        return Time,Volts
    except IndexError:
        return 0,0

# save data in xlsx file
def save_data(t,ch1,ch2, filename): 
    workbook = xlsxwriter.Workbook(filename + '.xlsx')
    worksheet = workbook.add_worksheet()
    # Write some data headers.
    worksheet.write('A1', 'Time (s)')
    worksheet.write('B1', 'CH1 (V)')
    worksheet.write('C1', 'CH2 (V)')
    # Start from the first cell.
    # Rows and columns are indexed.
    row = 1
    col = 0
    # iterating through x, y and z
    for time in t :
        # write operation perform
        worksheet.write(row, col, time)
        # incrementing the value of row by one with each iterations.
        row += 1
    # start from new column
    row = 1
    col = 1
    for data in ch1 :
        # write operation perform
        worksheet.write(row, col, data)
        # incrementing the value of row by one with each iterations.
        row += 1
    # start from new column
    row = 1
    col = 2
    for data in ch2 :
        # write operation perform
        worksheet.write(row, col, data)
        # incrementing the value of row by one with each iterations.
        row += 1  
    #close workbook
    workbook.close()

channel = "CH1"
filename = channel
(t,ch1) = acquire(channel,"GPIB0::1::INSTR")

channel = "CH2"
(t,ch2) = acquire(channel,"GPIB0::1::INSTR")
save_data(t,ch1,ch2, filename)