
import os
import sys
import tkinter as tk
from tkinter import ttk
import requests

ramEnter = 0
holeAddEnter = 1
holeSizeEnter = 2
selectMethodEnter = 3
processEnter = 4
segmentEnter = 5

state = 0
holes = []
ramSize = 0
Segments = []
Processes = []
AllocationQueue = []

old_state = 0
def ShowHoles():
    global holes
    for index in range(len(holes)):
        print(holes[index].startHole,holes[index].sizeHole,holes[index].remaining,holes[index].AllocatedSegments)

class Hole:

    def __init__(self, startHole, sizeHole):
        self.startHole = startHole
        self.sizeHole = sizeHole
        self.AllocatedSegments = []
        self.remaining = sizeHole

class Segment:
    def __init__(self,name,base,limit):
        self.name = name
        self.base = base
        self.limit = limit
        self.AllocatedHole = None
class Process:
    def __init__(self,name, segments):
        self.name = name
        self.segments = segments
        self.SegmentButtons = []
    def tryAllocate(self):
        global holes
        global Selection
        allocated = 0
        tryHoles = []
        for index1 in range(len(self.segments)):
            for index2 in range(len(holes)):
                if   (holes[index2].remaining >= self.segments[index1].limit):
                    #tk.Label(RAM, bg='blue').place(rely=holes[index2].startHole / ramSize, relwidth=1,  relheight=holes[index2].sizeHole / ramSize)
                    startHole =  holes[index2].startHole
                    sizeHole =  holes[index2].sizeHole
                    remaining =  holes[index2].remaining
                    allocated += 1
                    holes[index2].AllocatedSegments.append(self.segments[index1])
                    self.segments[index1].AllocatedHole = holes[index2]
                    holes[index2].remaining = remaining - self.segments[index1].limit
                    self.segments[index1].base = startHole + sizeHole -remaining
                    #first fit
                    if (Selection[-1] == 0):
                        holes.sort(key=lambda x: x.startHole)
                    # best fit
                    elif (Selection[-1] == 1):
                        holes.sort(key=lambda x: x.remaining)

                    print('allocated',self.segments[index1].name,'to',holes[index2].sizeHole)
                    tryHoles.append(index2)
                    break


        if (allocated == len(self.segments)):
            return 1
        else:
            for index3 in range(len(self.segments)):
                if (self.segments[index3].AllocatedHole != None):
                    self.segments[index3].AllocatedHole.AllocatedSegments = []
                    self.segments[index3].AllocatedHole.remaining = self.segments[index3].AllocatedHole.remaining +  self.segments[index3].limit
                    self.segments[index3].AllocatedHole = None


            return 0

    def ShowsSegments(self):
        SegmentTable.insert('', 'end', self.name, text=self.name)
        for index in range(len(self.segments)):
            self.SegmentButtons.append(tk.Button(RAM,text = self.name + ' ' + self.segments[index].name,bg = 'black',fg = 'white',command = lambda :SegmentPressed(self)))
            self.SegmentButtons[-1].place(rely=self.segments[index].base / ramSize, relwidth=1,  relheight=self.segments[index].limit / ramSize)
            SegmentTable.insert(self.name,'end',self.segments[index].name, text = self.segments[index].name +'  '+'Base: '+ str(self.segments[index].base) + '  '+ 'Limit: '+str(self.segments[index].limit))
    def DeleteSegments(self):
        SegmentTable.delete(self.name)
        for index in range(len(self.SegmentButtons)):
            self.SegmentButtons[index].destroy()
            self.segments[index].AllocatedHole.AllocatedSegments = []
            self.segments[index].AllocatedHole.remaining = self.segments[index].AllocatedHole.remaining + self.segments[index].limit
            self.segments[index].AllocatedHole = None
            # first fit
            if (Selection[-1] == 0):
                holes.sort(key=lambda x: x.startHole)
            # best fit
            elif (Selection[-1] == 1):
                holes.sort(key=lambda x: x.remaining)
            OutputMessage.config(text = 'Process ' + self.name +' deallocated successfully')
        ShowHoles()

def EnterPressed():
    global state
    global ramSize
    global holes
    global Segments
    global holesadd
    global holessize
    if (state == ramEnter):
        ramSize = int(InputEntry.get())
        state = holeAddEnter
    elif (state == holeAddEnter):
        holes.append(Hole(int(InputEntry.get()), 0))
        state = holeSizeEnter
    elif (state == holeSizeEnter):
        holes[-1].sizeHole = int(InputEntry.get())
        holes[-1].remaining = holes[-1].sizeHole
        tk.Label(RAM,bg='blue',text = 'HOLE').place(rely=holes[-1].startHole/ramSize, relwidth=1, relheight=holes[-1].sizeHole/ramSize )
        state = holeAddEnter
    elif (state == processEnter):
        Processes.append(Process(str(InputEntry.get()),[]))
        state = segmentEnter
    elif (state == segmentEnter):
        Processes[-1].segments.append(Segment(str(InputSegmentName.get()),0,int(InputSegmentLimit.get())))
        InputSegmentName.delete(0,'end')
        InputSegmentLimit.delete(0,'end')
        state = segmentEnter
    InputEntry.delete(0,'end')
def DonePressed():
    global state
    global Processes
    global holes
    global ramSize
    if (state == holeAddEnter):
        state = selectMethodEnter
    if (state == segmentEnter):
        if(Processes[-1].tryAllocate() == 1):
            OutputMessage.config(text='Process '+Processes[-1].name+' allocated succefully')
            Processes[-1].ShowsSegments()
            SegmentTableLabel.place(relx=0.5, rely=0.2)
            SegmentTable.place(relx=0.35, rely=0.25, relwidth=0.4, relheight=0.7)
        else:
            OutputMessage.config(text='Process ' + Processes[-1].name + ' could not be allocated and is queued')
            AllocationQueue.append(Processes[-1])
        state = processEnter

def SegmentPressed (process):
    process.DeleteSegments()
    if (len(AllocationQueue) != 0):
        if(AllocationQueue[-1].tryAllocate() == 1):
            OutputMessage.config(text='Process '+AllocationQueue[-1].name+' allocated succefully')
            AllocationQueue.pop().ShowsSegments()
        else:
            OutputMessage.config(text='Process ' + AllocationQueue[-1].name + ' could not be allocated and is queued')


root = tk.Tk()
canvas = tk.Canvas(root, height = 1000, width = 1000 )
canvas.pack()
RAM = tk.Frame(root, bd = 5,highlightthickness = 2) # #33cc33 is the colour in 0x
RAM.config(highlightbackground='black')
RAM.place(relx = 0.8, rely = 0, relwidth = 0.2, relheight = 1)
OutputFrame = tk.Frame(root,bg = 'black')
OutputFrame.place(relx = 0.4,rely=0,relwidth=0.2,relheight=0.1)
OutputMessage = tk.Message(OutputFrame,text="Blank")
OutputMessage.place(relwidth = 1,relheight = 1)
InputFrame = tk.Frame(root)
InputFrame.place(relx = 0,rely=0,relwidth=0.3,relheight=1)
EnterButton = tk.Button(InputFrame,text = "Enter",command = lambda :EnterPressed())
EnterButton.place(relx=0,rely=0.3,relwidth = 1,relheight=0.1)
InputLabel = tk.Label(InputFrame,text ='Enter input')
InputLabel.place(relx=0,rely=0,relwidth=1,relheight=0.1)
InputEntry = tk.Entry(InputFrame)
InputEntry.place(rely = 0.2,relwidth = 1,relheight = 0.1)
SegmentTableLabel = tk.Label(root,text = 'Segment Table')
SegmentTable = ttk.Treeview(root)
DoneButton = tk.Button(InputFrame,text = "Done",command = lambda :DonePressed())
MethodList = tk.Listbox(InputFrame)
MethodList.insert(1,"First Fit")
MethodList.insert(2,"Best Fit")

InputSegmentName = tk.Entry(InputFrame)
InputSegmentLimit = tk.Entry(InputFrame)



#main loop
while(1):
    if (state != old_state):
        print(state)
        old_state = state
    if (state == processEnter):
        InputLabel.config(text='enter process name')
        MethodList.place_forget()
        InputSegmentName.place_forget()
        InputSegmentLimit.place_forget()
        DoneButton.place_forget()
        InputEntry.place(rely=0.2, relwidth=1, relheight=0.1)
        EnterButton.place(relx=0, rely=0.3, relwidth=1, relheight=0.1)

    elif (state == segmentEnter):
        InputLabel.config(text='enter segment name and size')
        InputEntry.place_forget()
        InputSegmentName.place(relx = 0,rely=0.2, relwidth=0.5, relheight=0.1)
        InputSegmentLimit.place(relx = 0.5,rely=0.2, relwidth=0.5, relheight=0.1)
        DoneButton.place(relx=0, rely=0.4, relwidth=1, relheight=0.1)

    elif (state == holeAddEnter):
        InputLabel.config(text='enter hole address')
        DoneButton.place(relx=0, rely=0.4, relwidth=1, relheight=0.1)

    elif (state == holeSizeEnter):
        InputLabel.config(text='enter hole size')
        DoneButton.place_forget()

    elif (state == ramEnter):
        InputLabel.config(text='enter memory')

    elif (state == selectMethodEnter):
        InputLabel.config(text='Choose Allocation Method')
        InputEntry.place_forget()
        EnterButton.place_forget()
        DoneButton.place_forget()
        MethodList.place(relx = 0,rely = 0.1,relwidth = 1,relheight = 0.1)
        Selection = MethodList.curselection()
        if(len(Selection) != 0):
            #first fit
            if(Selection[-1] == 0):
                holes.sort(key=lambda x: x.startHole)
                OutputMessage.config(text='First       Fit Selected')
            #best fit
            elif(Selection[-1] == 1):
                holes.sort(key=lambda x: x.remaining)
                OutputMessage.config(text='Best       Fit Selected')
            state = processEnter


    root.update()
