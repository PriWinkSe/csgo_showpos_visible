import math
import struct
from dataclasses import dataclass
import pymem
import tkinter as tk
import threading
import time
import sys
import os
import wmi
import socket
import requests
import yaml

def exact_sleep(delay_ns):
    #单位 纳秒
    target = int(time.perf_counter_ns()*1000) + delay_ns
    while int(time.perf_counter_ns()) < target:
        pass

def sp_sleep(delay):
    target = time.perf_counter()+delay
    while time.perf_counter() <= target:
        pass

pm = pymem.Pymem("csgo.exe")

client = pymem.process.module_from_name(pm.process_handle,"client.dll").lpBaseOfDll
materialSystem = pymem.process.module_from_name(pm.process_handle, "materialsystem.dll").lpBaseOfDll
enginedll = pymem.process.module_from_name(pm.process_handle, "engine.dll").lpBaseOfDll

root = tk.Tk()
root['background']='white'
root.attributes("-toolwindow", True)
'''禁止自己调整大小'''
root.resizable(False, False)
'''窗口置顶 显示在最前方'''
root.attributes("-topmost", 1)
'''透明度'''
root.attributes("-alpha", 0.9)
root.overrideredirect(False)
root.title('✔loc_visible')
root.geometry('145x105')

lb1 = tk.Label(root, text='X: none', font=('微软雅黑', 10), fg='Indigo', bg='white')
lb1.place(x=8, y=0)

lb2 = tk.Label(root, text='Z: none', font=('微软雅黑', 10), fg='Indigo', bg='white')
lb2.place(x=8, y=40)

lb3 = tk.Label(root, text='Y: none', font=('微软雅黑', 10), fg='Indigo', bg='white')
lb3.place(x=8, y=20)

angleLabel = tk.Label(root, text='A: none', font=('微软雅黑', 10), fg='Blue', bg='white')
angleLabel.place(x=8, y=60)

movement = tk.Label(root, text='V: none', font=('微软雅黑',10), fg='Magenta', bg='white')
movement.place(x=8,y=80)

link_url1 = "http://222.187.238.84:4232/list-files/csgo.yaml"
link_url2 = "http://222.187.238.84:4232/list-files/csgo_location.yaml"

class NotFindYamlFileException(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

try:
  req = requests.get(link_url1)
  req2 = requests.get(link_url2)
  yamlinfo = yaml.load(req.text,Loader=yaml.CLoader)
  locinfo = yaml.load(req2.text,Loader=yaml.CLoader)
except Exception:
  raise NotFindYamlFileException("验证基址失败! 请联系作者是否为文件失效!")
LOCAL_PLAYER = int(yamlinfo["signatures"]["dwLocalPlayer"])
HEALTH = int(yamlinfo["netvars"]["m_iHealth"])
FLAGS = int(yamlinfo["netvars"]["m_fFlags"])
m_vecVelocity = int(yamlinfo["netvars"]["m_vecVelocity"])

X_address = enginedll + int(locinfo["location"]["x"])
Y_address = enginedll + int(locinfo["location"]["y"])
Z_address = enginedll + int(locinfo["location"]["z"])
tangAddress = enginedll + int(locinfo["location"]["tang"]);


def flush_location():
     global X_address
     global Z_address
     global Y_address
     global pm
     while True:
          lb1.__setitem__("text", "X:  " + str(('%.0f' % pm.read_float(X_address))))
          lb3.__setitem__("text", "Y:  " + str(('%.0f' % pm.read_float(Y_address))))
          lb2.__setitem__("text", "Z:  " + str(('%.0f' % pm.read_float(Z_address))))
          time.sleep(0.01)

def flushAngle():
     global tangAddress
     global angleLabel
     global pm
     while True:
          angle = pm.read_float(tangAddress)
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
          angleLabel.__setitem__("text", "A:  " + str('%.0f' % angle) + "  " + bz)
          time.sleep(0.01)

@dataclass
class Vector3:
    x: float
    y: float
    z: float

def flushMovement():
    global X_address
    global Y_address
    global Z_address
    global LOCAL_PLAYER
    global pm
    global m_vecVelocity
    global HEALTH
    for module in list(pm.list_modules()):
        if module.name == 'client.dll':
            client_dll = module.lpBaseOfDll
    while True:
        local_player: int = pm.read_uint(client_dll + LOCAL_PLAYER)
        #三轴速度
        if not local_player:
            time.sleep(0.015)
            continue
        if not pm.read_int(local_player + HEALTH):
            time.sleep(0.015)
            continue
        vec_bytes = pm.read_bytes(local_player + m_vecVelocity, 0XC)
        velocity = Vector3(*struct.unpack("3f", vec_bytes))
        spd = round(math.sqrt(math.pow(velocity.x,2) + math.pow(velocity.y,2)),1)
        #print("S:   " + str(spd) + " u/s")
        movement.__setitem__("text", "V:  " + str(spd) + " u/s")
        time.sleep(0.015)



if __name__ == "__main__":
    xc1 = threading.Thread(target=flush_location, args=())
    xc1.daemon = True
    xc1.start()

    xc4 = threading.Thread(target=flushAngle, args=())
    xc4.daemon = True
    xc4.start()

    time.sleep(0.2)
    xc5 = threading.Thread(target=flushMovement, args=())
    xc5.daemon = True
    xc5.start()

    time.sleep(0.2)
    root.mainloop()
    sys.exit()
