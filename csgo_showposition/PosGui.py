import threading
import tkinter as tk
import sys
from dataclasses import dataclass
from offset_tools import offsets
import time

@dataclass
class PostionGui:
    def __init__(self):
        self._root = tk.Tk()
        self._root['background'] = 'white'
        self._root.attributes("-toolwindow", True)
        self._root.resizable(False, False)
        self._root.attributes("-topmost", 1)
        self._root.attributes("-alpha", 0.9)
        self._root.overrideredirect(False)
        self._root.title('✔loc_visible')
        self._root.geometry('145x105')
        self.lb1 = tk.Label(self._root, text='X: none', font=('微软雅黑', 10), fg='Indigo', bg='white')
        self.lb1.place(x=8, y=0)
        self.lb2 = tk.Label(self._root, text='Z: none', font=('微软雅黑', 10), fg='Indigo', bg='white')
        self.lb2.place(x=8, y=40)
        self.lb3 = tk.Label(self._root, text='Y: none', font=('微软雅黑', 10), fg='Indigo', bg='white')
        self.lb3.place(x=8, y=20)
        self.angleLabel = tk.Label(self._root, text='A: none', font=('微软雅黑', 10), fg='Blue', bg='white')
        self.angleLabel.place(x=8, y=60)
        self.movement = tk.Label(self._root, text='V: none', font=('微软雅黑', 10), fg='Magenta', bg='white')
        self.movement.place(x=8, y=80)
    def StartPaint(self):
        self._root.mainloop()
        sys.exit()

gui = PostionGui()

#启动方法
def StartPaint():
    sleep_time = 0.01
    def paintAngle():
        while True:
            angle = offsets.Angle
            bz = ""
            if 100 >= angle >= 80:
                bz = "↑"
            elif -110 <= angle <= -80:
                bz = "↓"
            elif -10 <= angle <= 10:
                bz = "←."
            elif (angle <= -170 and angle < 0) or (angle >= 170):
                bz = ".→"
            elif 55 >= angle >= 35:  # 90 - 180    45  35~55
                bz = "↖."
            elif 145 >= angle >= 125:
                bz = ".↗"
            gui.angleLabel.__setitem__("text", "A:  " + str('%.0f' % angle) + "  " + bz)
            time.sleep(sleep_time)
    def paintX():
        while True:
            gui.lb1.__setitem__("text", "X:  " + str(('%.0f' % offsets.X)))
            time.sleep(sleep_time)
    def paintY():
        while True:
            gui.lb3.__setitem__("text", "Y:  " + str(('%.0f' % offsets.Y)))
            time.sleep(sleep_time)
    def paintZ():
        while True:
            gui.lb2.__setitem__("text", "Z:  " + str(('%.0f' % offsets.Z)))
            time.sleep(sleep_time)
    def paintVel():
        while True:
            gui.movement.__setitem__("text", "V:  " + str(offsets.Velocity) + " u/s")
            time.sleep(sleep_time)
    t1 = threading.Thread(target=paintX,args=())
    t1.daemon = True
    t1.start()
    time.sleep(0.2)
    t2 = threading.Thread(target=paintY, args=())
    t2.daemon = True
    t2.start()
    time.sleep(0.2)
    t3 = threading.Thread(target=paintZ, args=())
    t3.daemon = True
    t3.start()
    time.sleep(0.2)
    t4 = threading.Thread(target=paintVel, args=())
    t4.daemon = True
    t4.start()
    t5 = threading.Thread(target=paintAngle,args=())
    t5.daemon=True
    t5.start()
    gui.StartPaint()


