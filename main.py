import sys

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

import lf_support
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame

import matplotlib.pyplot as plt

from scipy.fftpack import rfft, fftfreq

def bandPass(df, lowCutoff = 0.1, highCutoff = 0.3):
    fL = lowCutoff
    fH = highCutoff
    b = 0.08
    N = int(np.ceil((4 / b)))
    if not N % 2: N += 1  # Make sure that N is odd.
    n = np.arange(N)

    # low-pass filter
    hlpf = np.sinc(2 * fH * (n - (N - 1) / 2.))
    hlpf *= np.blackman(N)
    hlpf = hlpf / np.sum(hlpf)

    # high-pass filter 
    hhpf = np.sinc(2 * fL * (n - (N - 1) / 2.))
    hhpf *= np.blackman(N)
    hhpf = hhpf / np.sum(hhpf)
    hhpf = -hhpf
    hhpf[int((N - 1) / 2)] += 1

    h = np.convolve(hlpf, hhpf)
    s = list(df)
    return np.convolve(s, h)

def FFT(df, sampleRate = 200.0):
    N = len(df)
    T = 1.0 / sampleRate
    yf = rfft(list(df))
    xf = fftfreq(N, T)[:N//2]
    return list(2.0/N * np.abs(yf[0:N//2]))[2:], list(xf)[2:]

def openFile():
    fileName = askopenfilename(
        filetypes=(("Sensor Data", "*.csv"), ("All Files", "*.*")),
        title="Choose a file."
    )
    global dataRaw
    dataRaw = DataFrame(pd.read_csv(fileName))

def rawSignal():
    try:
        print(dataRaw)
        df = DataFrame({
            'Data point': list(range(len(dataRaw['data']))),
            'Data': list(dataRaw['data'])
        })
        print(df)
        df.plot(x='Data point')
        plt.grid(linestyle = '--', linewidth = 0.45)
        plt.show()
    except NameError:
        messagebox.showerror('Data is not defined.', 'Please open a sensor data first.')

def fourierTransform():
    try:
        finalY, finalX = FFT(dataRaw['data'])
        df = DataFrame({
            'Data point':finalX,
            'Data': finalY
        })
        df.plot(x='Data point')
        plt.grid(linestyle = '--', linewidth = 0.45)
        plt.show()
    except NameError:
        messagebox.showerror('Data is not defined.', 'Please open a sensor data first.')

def bandpassFilter(low = 0.05, high = 0.05):
    try:
        filteredSignal = bandPass(dataRaw['data'], float(low), float(high))
        df = DataFrame({
            'Data point': list(range(len(filteredSignal))),
            'Data': filteredSignal
        })
        df.plot(x='Data point')
        plt.grid(linestyle = '--', linewidth = 0.45)

        finalY, finalX = FFT(filteredSignal)
        df = DataFrame({
            'Data point': finalX,
            'Data': finalY
        })
        df.plot(x='Data point')
        plt.grid(linestyle = '--', linewidth = 0.45)
        plt.show()
    except NameError:
        messagebox.showerror('Data is not defined.', 'Please open a sensor data first.')
    except ValueError:
        messagebox.showerror('Invalid input value', 'Please review your input format. Make sure it is a number.')

def manualFilter(low = 12, high = 20):
    try:
        finalY, finalX = FFT(dataRaw['data'])
        for i in range(len(finalX)):
            if finalX[i] <= float(low) or finalX[i] >= float(high):
                finalY[i] = 0
        df = DataFrame({
            'Data point':finalX,
            'Data': finalY
        })
        df.plot(x='Data point')
        plt.grid(linestyle = '--', linewidth = 0.45)
        plt.show()
    except NameError:
        messagebox.showerror('Data is not defined.', 'Please open a sensor data first.')
    except ValueError:
        messagebox.showerror('Invalid input value', 'Please review your input format. Make sure it is a number.')

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = tk.Tk()
    top = Toplevel1 (root)
    lf_support.init(root, top)
    root.mainloop()

w = None
def create_Toplevel1(rt, *args, **kwargs):
    '''Starting point when module is imported by another module.
       Correct form of call: 'create_Toplevel1(root, *args, **kwargs)' .'''
    global w, w_win, root
    #rt = root
    root = rt
    w = tk.Toplevel (root)
    top = Toplevel1 (w)
    lf_support.init(w, top, *args, **kwargs)
    return (w, top)

def destroy_Toplevel1():
    global w
    w.destroy()
    w = None

class Toplevel1:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'

        top.geometry("717x232+332+225")
        top.minsize(120, 1)
        top.maxsize(1905, 1050)
        top.resizable(0,  0)
        top.title("Accelerometer Signal Visualizer")
        top.configure(background="#d9d9d9")
        top.configure(highlightbackground="#f5deb3")
        top.configure(highlightcolor="black")

        self.Labelframe3 = tk.LabelFrame(top)
        self.Labelframe3.place(x=219, y=8, height=217, width=241)
        self.Labelframe3.configure(relief='groove')
        self.Labelframe3.configure(foreground="black")
        self.Labelframe3.configure(text='''Bandpass Filter''')
        self.Labelframe3.configure(background="#d9d9d9")
        self.Labelframe3.configure(highlightbackground="#f5deb3")
        self.Labelframe3.configure(highlightcolor="black")

        self.Entry1 = tk.Entry(self.Labelframe3)
        self.Entry1.place(x=10, y=50, height=20, width=144, bordermode='ignore')
        self.Entry1.configure(background="white")
        self.Entry1.configure(disabledforeground="#b8a786")
        self.Entry1.configure(font="-family {DejaVu Sans Mono} -size 10")
        self.Entry1.configure(foreground="#000000")
        self.Entry1.configure(highlightbackground="#f5deb3")
        self.Entry1.configure(highlightcolor="black")
        self.Entry1.configure(insertbackground="black")
        self.Entry1.configure(selectbackground="#c4c4c4")
        self.Entry1.configure(selectforeground="black")

        self.Label6 = tk.Label(self.Labelframe3)
        self.Label6.place(x=10, y=20, height=21, width=115, bordermode='ignore')
        self.Label6.configure(activebackground="#f9f9f9")
        self.Label6.configure(activeforeground="black")
        self.Label6.configure(background="#d9d9d9")
        self.Label6.configure(disabledforeground="#b8a786")
        self.Label6.configure(foreground="#000000")
        self.Label6.configure(highlightbackground="#f5deb3")
        self.Label6.configure(highlightcolor="black")
        self.Label6.configure(text='''High Fraction Cutoff''')

        self.Entry1_1 = tk.Entry(self.Labelframe3)
        self.Entry1_1.place(x=11, y=117, height=20, width=144
                , bordermode='ignore')
        self.Entry1_1.configure(background="white")
        self.Entry1_1.configure(disabledforeground="#b8a786")
        self.Entry1_1.configure(font="-family {DejaVu Sans Mono} -size 10")
        self.Entry1_1.configure(foreground="#000000")
        self.Entry1_1.configure(highlightbackground="#f5deb3")
        self.Entry1_1.configure(highlightcolor="black")
        self.Entry1_1.configure(insertbackground="black")
        self.Entry1_1.configure(selectbackground="#c4c4c4")
        self.Entry1_1.configure(selectforeground="black")

        self.Label6_1 = tk.Label(self.Labelframe3)
        self.Label6_1.place(x=11, y=85, height=22, width=129
                , bordermode='ignore')
        self.Label6_1.configure(activebackground="#f9f9f9")
        self.Label6_1.configure(activeforeground="black")
        self.Label6_1.configure(anchor='w')
        self.Label6_1.configure(background="#d9d9d9")
        self.Label6_1.configure(disabledforeground="#b8a786")
        self.Label6_1.configure(foreground="#000000")
        self.Label6_1.configure(highlightbackground="#f5deb3")
        self.Label6_1.configure(highlightcolor="black")
        self.Label6_1.configure(text='''Low Fraction Cutoff''')

        self.Generate2 = tk.Button(self.Labelframe3, command=lambda: bandpassFilter(self.Entry1.get(), self.Entry1_1.get()))
        self.Generate2.place(x=30, y=180, height=24, width=177
                , bordermode='ignore')
        self.Generate2.configure(activebackground="#ececec")
        self.Generate2.configure(activeforeground="#000000")
        self.Generate2.configure(background="#d9d9d9")
        self.Generate2.configure(disabledforeground="#a3a3a3")
        self.Generate2.configure(foreground="#000000")
        self.Generate2.configure(highlightbackground="#d9d9d9")
        self.Generate2.configure(highlightcolor="black")
        self.Generate2.configure(pady="0")
        self.Generate2.configure(text='''Generate''')

        self.Labelframe3_1 = tk.LabelFrame(top)
        self.Labelframe3_1.place(x=460, y=8, height=217, width=249)
        self.Labelframe3_1.configure(relief='groove')
        self.Labelframe3_1.configure(foreground="black")
        self.Labelframe3_1.configure(text='''Manual Filter''')
        self.Labelframe3_1.configure(background="#d9d9d9")
        self.Labelframe3_1.configure(highlightbackground="#f5deb3")
        self.Labelframe3_1.configure(highlightcolor="black")

        self.Entry1_2 = tk.Entry(self.Labelframe3_1)
        self.Entry1_2.place(x=10, y=50, height=20, width=144
                , bordermode='ignore')
        self.Entry1_2.configure(background="white")
        self.Entry1_2.configure(disabledforeground="#b8a786")
        self.Entry1_2.configure(font="-family {DejaVu Sans Mono} -size 10")
        self.Entry1_2.configure(foreground="#000000")
        self.Entry1_2.configure(highlightbackground="#f5deb3")
        self.Entry1_2.configure(highlightcolor="black")
        self.Entry1_2.configure(insertbackground="black")
        self.Entry1_2.configure(selectbackground="#c4c4c4")
        self.Entry1_2.configure(selectforeground="black")

        self.Label6_2 = tk.Label(self.Labelframe3_1)
        self.Label6_2.place(x=10, y=20, height=21, width=94, bordermode='ignore')

        self.Label6_2.configure(activebackground="#f9f9f9")
        self.Label6_2.configure(activeforeground="black")
        self.Label6_2.configure(background="#d9d9d9")
        self.Label6_2.configure(disabledforeground="#b8a786")
        self.Label6_2.configure(foreground="#000000")
        self.Label6_2.configure(highlightbackground="#f5deb3")
        self.Label6_2.configure(highlightcolor="black")
        self.Label6_2.configure(text='''High Cutoff (Hz)''')

        self.Entry1_1_1 = tk.Entry(self.Labelframe3_1)
        self.Entry1_1_1.place(x=11, y=117, height=20, width=144
                , bordermode='ignore')
        self.Entry1_1_1.configure(background="white")
        self.Entry1_1_1.configure(disabledforeground="#b8a786")
        self.Entry1_1_1.configure(font="-family {DejaVu Sans Mono} -size 10")
        self.Entry1_1_1.configure(foreground="#000000")
        self.Entry1_1_1.configure(highlightbackground="#f5deb3")
        self.Entry1_1_1.configure(highlightcolor="black")
        self.Entry1_1_1.configure(insertbackground="black")
        self.Entry1_1_1.configure(selectbackground="#c4c4c4")
        self.Entry1_1_1.configure(selectforeground="black")

        self.Label6_1_1 = tk.Label(self.Labelframe3_1)
        self.Label6_1_1.place(x=11, y=85, height=22, width=134
                , bordermode='ignore')
        self.Label6_1_1.configure(activebackground="#f9f9f9")
        self.Label6_1_1.configure(activeforeground="black")
        self.Label6_1_1.configure(anchor='w')
        self.Label6_1_1.configure(background="#d9d9d9")
        self.Label6_1_1.configure(disabledforeground="#b8a786")
        self.Label6_1_1.configure(foreground="#000000")
        self.Label6_1_1.configure(highlightbackground="#f5deb3")
        self.Label6_1_1.configure(highlightcolor="black")
        self.Label6_1_1.configure(text='''Low Cutoff (Hz)''')

        self.Generate1 = tk.Button(self.Labelframe3_1, command=lambda: manualFilter(self.Entry1_2.get(), self.Entry1_1_1.get()))
        self.Generate1.place(x=30, y=180, height=24, width=187
                , bordermode='ignore')
        self.Generate1.configure(activebackground="#ececec")
        self.Generate1.configure(activeforeground="#000000")
        self.Generate1.configure(background="#d9d9d9")
        self.Generate1.configure(disabledforeground="#a3a3a3")
        self.Generate1.configure(foreground="#000000")
        self.Generate1.configure(highlightbackground="#d9d9d9")
        self.Generate1.configure(highlightcolor="black")
        self.Generate1.configure(pady="0")
        self.Generate1.configure(text='''Generate''')

        self.Labelframe3_2 = tk.LabelFrame(top)
        self.Labelframe3_2.place(x=8, y=8, height=216, width=211)
        self.Labelframe3_2.configure(relief='groove')
        self.Labelframe3_2.configure(foreground="black")
        self.Labelframe3_2.configure(text='''Raw Data''')
        self.Labelframe3_2.configure(background="#d9d9d9")
        self.Labelframe3_2.configure(highlightbackground="#f5deb3")
        self.Labelframe3_2.configure(highlightcolor="black")

        self.Open = tk.Button(self.Labelframe3_2)
        self.Open.place(x=40, y=40, height=24, width=127, bordermode='ignore')
        self.Open.configure(activebackground="#ececec")
        self.Open.configure(activeforeground="#000000")
        self.Open.configure(background="#d9d9d9")
        self.Open.configure(disabledforeground="#a3a3a3")
        self.Open.configure(foreground="#000000")
        self.Open.configure(highlightbackground="#d9d9d9")
        self.Open.configure(highlightcolor="black")
        self.Open.configure(pady="0")
        self.Open.configure(text='''Open file''', command=openFile)

        self.Open_1 = tk.Button(self.Labelframe3_2)
        self.Open_1.place(x=40, y=90, height=24, width=127, bordermode='ignore')
        self.Open_1.configure(activebackground="#ececec")
        self.Open_1.configure(activeforeground="#000000")
        self.Open_1.configure(background="#d9d9d9")
        self.Open_1.configure(disabledforeground="#a3a3a3")
        self.Open_1.configure(foreground="#000000")
        self.Open_1.configure(highlightbackground="#d9d9d9")
        self.Open_1.configure(highlightcolor="black")
        self.Open_1.configure(pady="0")
        self.Open_1.configure(text='''Raw Signal''', command=rawSignal)

        self.Open_2 = tk.Button(self.Labelframe3_2, command=fourierTransform)
        self.Open_2.place(x=40, y=140, height=24, width=127, bordermode='ignore')

        self.Open_2.configure(activebackground="#ececec")
        self.Open_2.configure(activeforeground="#000000")
        self.Open_2.configure(background="#d9d9d9")
        self.Open_2.configure(disabledforeground="#a3a3a3")
        self.Open_2.configure(foreground="#000000")
        self.Open_2.configure(highlightbackground="#d9d9d9")
        self.Open_2.configure(highlightcolor="black")
        self.Open_2.configure(pady="0")
        self.Open_2.configure(text='''Fourier Transfom''')

if __name__ == '__main__':
    vp_start_gui()
