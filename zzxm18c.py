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

user_name = os.getlogin()
s = wmi.WMI()

def exact_sleep(delay_ns):
    #单位 纳秒
    target = int(time.perf_counter_ns()*1000) + delay_ns
    while int(time.perf_counter_ns()) < target:
        pass
#用法和普通的sleep一样
def zzxm_sleep(delay):
    target = time.perf_counter()+delay
    while time.perf_counter() <= target:
        pass

def getSerialNum():
    cp = s.Win32_Processor()
    cpu = []
    cp = s.Win32_Processor()
    for u in cp:
        cpu.append(
            {
                "Name": u.Name,
                "Serial Number": u.ProcessorId,
                "CoreNum": u.NumberOfCores
            }
        )

    disk = []
    for pd in s.Win32_DiskDrive():
        disk.append(
            {
                "Serial": s.Win32_PhysicalMedia()[0].SerialNumber.lstrip().rstrip(),  # 获取硬盘序列号，调用另外一个win32 API
                "ID": pd.deviceid,
                "Caption": pd.Caption,
                "size": str(int(float(pd.Size) / 1024 / 1024 / 1024)) + "G"
            }
        )

    network = []
    for nw in s.Win32_NetworkAdapterConfiguration():  # IPEnabled=0
         if nw.MACAddress != None:
            network.append(
                   {
                     "MAC": nw.MACAddress,  # 无线局域网适配器 WLAN 物理地址
                      "ip": nw.IPAddress
                   }
              )


    mainboard = []
    for board_id in s.Win32_BaseBoard():
        mainboard.append(board_id.SerialNumber.strip().strip('.'))
    r = u.ProcessorId + s.Win32_PhysicalMedia()[0].SerialNumber.replace("_","").replace(".","") + nw.MACAddress.replace(":","") + board_id.SerialNumber.replace(":","").replace("-","")
    return r

def getpack():
       return user_name + ";" + getSerialNum()


def st():
      try:
           sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           sock.connect(('114.132.189.96', 7799))
           sock.send(getpack().encode('gbk'))
      except Exception as E:
           print("connect failed!")

#st()    #验证



#dwEntityPointer = (0x4DCEB7C)

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
root.title('Zzxm_Final')
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

#想要精确睡眠就得学好python的多线程
def flushAngle():
     global tangAddress
     global angleLabel
     global pm
     while True:
          angle = pm.read_float(tangAddress)
          bz = ""
          if angle <= 100 and angle >= 80:
            bz = "↑"
          elif angle >= -110 and angle <= -80:
            bz = "↓"
          elif angle >= -10 and angle <= 10:
            bz = "←."
          elif (angle <= -170 and angle < 0) or (angle >= 170):
            bz = ".→"
          elif angle <= 90-35 and angle >= 90-55:  # 90 - 180    45  35~55
            bz = "↖."
          elif angle <= 90+55 and angle >= 90+35:
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
