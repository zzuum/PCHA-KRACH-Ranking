#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
author: Niklas

"""

from Tkinter import Frame, Tk, BOTH, Text, Menu, END
import tkFileDialog 
from SportRanking import PCHAranking

class RankGui(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent        
        self.initUI()
        
        
    def initUI(self):
      
        self.parent.title("File dialog")
        self.pack(fill=BOTH, expand=1)
        
        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)
        
        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Open", command=self.onOpen)
        menubar.add_cascade(label="File", menu=fileMenu)        
        
        self.txt = Text(self)
        self.txt.pack(fill=BOTH, expand=1)


    def onOpen(self):
      
        ftypes = [('CSV Files', '*.csv'), ('All files', '*')]
        dlg = tkFileDialog.Open(self, filetypes = ftypes)
        fl = dlg.show()
        
        if fl != '':
            text = self.readFile(fl)
            self.txt.insert(END, text)
            

    def readFile(self, filename):

        f = open(filename, "r")
        rankobj = PCHA_KRACH(f)
        rpiranks = rankobj.RPI_ranking('ranking.csv')
        return(rpiranks)

def main():
  
    root = Tk()
    ex = RankGui(root)
    root.geometry("400x300")
    root.mainloop()  


if __name__ == '__main__':
    main()  
