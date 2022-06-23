import datetime as dt
from multiprocessing.dummy import Array
from os.path import exists
import sys
sys.executable

import numpy as np

import PySimpleGUI as sg 

import matplotlib 
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import pandas as pd
import pandas_datareader.data as web

inputOptions = ["File", "yahoo"]

def CreateRow(i):
    main = [[
        sg.Combo(inputOptions, key="dataPullType"+str(i), default_value="File", readonly=True, enable_events=True),
        sg.Input(key='dataInput'+str(i),expand_x=True, enable_events=True, default_text="test"),
        sg.Input(key="columnInput"+str(i),size=(10,20))
    ]]
    Frame = sg.Frame(layout=main, key="Row"+str(i), title="")
    
    return [[Frame]]

def Frame(element):
    return sg.Frame(title="", layout=element)

sg.theme("BlueMono")

header = "Input Type   Data Input                                                                      Column #"

dayoptions = np.arange(1, 32).tolist()
monthoptions = np.arange(1, 13).tolist()
yearoptions = np.arange(2022, 1970, -1).tolist()

layout=[
    # Top Row
    [
        sg.Text("", key="RowCounter"), 
        sg.Button("Add Row", key="addRow"), 
        sg.Button("Remove Row", key="rmRow"),
        sg.Button("Refresh")
    ],

    # Date input
    [
        sg.Text("Start: "),
        sg.Combo(yearoptions,  key="startYear", size=(5, 10), readonly=True, default_value="2021"), 
        sg.Combo(monthoptions, key="startMonth",  size=(5, 10), readonly=True, default_value="1"), 
        sg.Combo(dayoptions,   key="startDay",    size=(5, 10), readonly=True, default_value="1")
    ],
    [
        sg.Text("End:  "),
        sg.Combo(yearoptions,  key="endYear", size=(5, 10), readonly=True, default_value="2021"), 
        sg.Combo(monthoptions, key="endMonth",  size=(5, 10), readonly=True, default_value="1"), 
        sg.Combo(dayoptions,   key="endDay",    size=(5, 10), readonly=True, default_value="1")
    ],

    [sg.Column([[Frame([[sg.Text(header)]])]], key="inputRows")],
    [sg.Canvas(key='Canvas')]
]

window=sg.Window('Graphing',layout, finalize=True)

# matplotlib
fig=matplotlib.figure.Figure(figsize=(5,4))
figure_canvas_agg=FigureCanvasTkAgg(fig,window['Canvas'].TKCanvas)
figure_canvas_agg.draw()
figure_canvas_agg.get_tk_widget().pack()

rows = 0
rowArray = []
def rowUpdate():
    window["RowCounter"].update(str(rows))
    window["rmRow"].update(visible=rows>0)

rowUpdate()

Tinkerdf = pd.read_csv("Tickers.csv")
symbols = Tinkerdf.values[:, 2]
names = Tinkerdf.values[:, 1]

for i in range(len(names)):
    names[i] = names[i].upper()

def getTinker(string):
    string = string.upper()

    if string == "":
        return

    if len(np.where(symbols == string)[0]) > 0:
        return string
    else:
        cases = np.where(names == string)
        if len(cases[0]) > 0:
            return cases[0][0]

        for i in range(len(names)):
            if names[i].startswith(string):
                return symbols[i]

    return ""

def DateError(values, element, elementType):
    valrangeMax, valrangeMin = 0, 0
    if elementType == "Year":
        valrangeMin = 1970
        valrangeMax = 2022
    elif elementType == "Month":
        valrangeMin = 1
        valrangeMax = 12
    elif elementType == "Day":
        valrangeMin = 1
        valrangeMax = 31

    try:
        val = int(values[element])

        if val <= valrangeMax and val >= valrangeMin:
            return val
        # else:

    except:
        return

def Refresh(values):
    # Clearing and Getting Ready for new plots
    fig.clear()
    fig.add_subplot(111).plot([],[])
    axes=fig.axes

    # Drawing all rows
    for i in range(rows):

        # Getting Data Pull type
        dataPullType = values["dataPullType"+str(i)]

        # Getting Data Frame
        df = ""
        if dataPullType == "File":
            if not exists(values['dataInput'+str(i)]):
                continue
            df = pd.read_csv(values['dataInput'+str(i)])
        elif dataPullType == "yahoo":
            start=dt.datetime(int(values["startYear"]),int(values["startMonth"]),int(values["startDay"]))
            end=dt.datetime(int(values["endYear"]),int(values["endMonth"]),int(values["endDay"]))
            df = web.DataReader(getTinker(values['dataInput'+str(i)]), "yahoo", start, end)

        data = df.values[:, int(values["columnInput"+str(i)] or 0)]

        # Potting data
        x=range(len(data))
        y=data
        axes[0].plot(x,y,'-')
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack()

while True:
    event,values=window.read()
    if event == sg.WIN_CLOSED:
        break

    if event=='addRow':
        rowArray.append(CreateRow(rows))
        window.extend_layout(window['inputRows'], rowArray[rows])
        rowArray[rows] = rowArray[rows][0][0]

        rows+=1
        rowUpdate()
    elif event=="rmRow":
        rows-=1
        rowUpdate()

        rowArray[rows].update(visible=False)
        rowArray[rows].Widget.master.pack_forget()
        rowArray.__delitem__(rows)
    elif event=="Refresh":
        Refresh(values)


window.close()