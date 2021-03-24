from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from pandas import DataFrame
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import math

GUI = Tk()
GUI.geometry("500x200")
GUI.title("SIMBAGAS Sensor Visualizer")


def OpenFile():
    fileName = askopenfilename(
        filetypes=(("Sensor Data", "*.csv"), ("All Files", "*.*")),
        title="Choose a file."
    )
    with open(fileName) as fileData:
        fileNameFull = fileName.split('/')
        if len(fileNameFull) > 1:
            arguments = fileNameFull[len(fileNameFull) - 1].split('-')
            print(arguments)
            if int(arguments[0]):
                X, Y, timestamps = [], [], []
                firstTimestamp = 0
                chain = 1
                chainData = {}
                chainDatas = {}
                count = 0
                for row in fileData:
                    rawData = row.replace('\n', '').split(',')
                    timestamp = int(rawData[0])
                    counterTS = math.trunc(timestamp/1000)
                    count += 1
                    if count == 90:
                        break
                    if firstTimestamp == 0:
                        firstTimestamp = counterTS
                    else:
                        if firstTimestamp != counterTS and counterTS - firstTimestamp == 1:
                            firstTimestamp = counterTS
                            pass
                        else:
                            firstTimestamp = counterTS
                            chain += 1
                            continue
                    if chain in chainData:
                        if counterTS*1000 in chainData[chain]:
                            pass
                        else:
                            chainData[chain].append(counterTS*1000)
                            chainDatas[chain].append(rawData)
                    else:
                        chainData[chain] = [counterTS*1000]
                        chainDatas[chain] = [rawData]
                        
                maxChain = 0
                
                for index in chainData:
                    if maxChain < len(chainData[index]):
                        maxChain = len(chainData[index])
                newData = []
                for index in chainDatas:
                    if len(chainDatas[index]) == maxChain:
                        newData = chainDatas[index]
                for index in range(len(newData)):
                    timestamp = int(newData[index].pop(0))
                    for indexD in range(len(newData[index])):
                        if int(indexD) % 2 == 0:
                            X.append(float(newData[index][indexD]))
                        else:
                            Y.append(float(newData[index][indexD]))
                            timestamps.append(
                                datetime.fromtimestamp(timestamp/1000.0))
                            timestamp += 20

                n = 1
                while 2**(n+1) <= len(timestamps):
                    n += 1
                print(2**n)
                print(len(X[0:2**n]))
                print(len(timestamps))
                df = DataFrame({
                    'Time': timestamps[0:2**n],
                    'Vertikal': X[0:2**n],
                    'Lintang': Y[0:2**n]
                })

                df.plot(x='Time', subplots=True, layout=(2, 1), sharey=True)
                plt.title(arguments[2].replace('_', ' ').replace('.csv', ''))
                plt.gca().xaxis_date('Asia/Jakarta')
                XData = np.array(df['Vertikal'])
                YData = np.array(df['Lintang'])

                XOutput = np.fft.fft(XData)
                YOutput = np.fft.fft(YData)

                fa = 1.0/0.02
                N = math.ceil(len(XOutput)/2)
                frequency = np.linspace(0, fa/2, N)[1:]

                XOutput_real = np.abs(XOutput[1:N])
                YOutput_real = np.abs(YOutput[1:N])
                XMax = np.amax(XOutput_real)
                YMax = np.amax(YOutput_real)

                df = DataFrame({
                    'Frequency': frequency,
                    'X (Max value = ' + str(round(XMax, 3)) + ')': XOutput_real,
                    'Y (Max Value = ' + str(round(YMax, 3)) + ')': YOutput_real
                }).sort_values(by=['Frequency'])

                df.plot(x='Frequency', subplots=True,
                        layout=(2, 1), sharey=True)
                plt.title('analisis getaran dari ' + arguments[2].replace('_', ' ').replace('.csv', ''))
                plt.show()

label = ttk.Label(
    GUI, text="Pastikan anda tidak mengubah format file dataset", font=("", 12))
label.pack()

menu = Menu(GUI)
button = Button(text="Pilih Dataset", command=OpenFile)
button.pack()
GUI.config(menu=menu)

GUI.mainloop()
