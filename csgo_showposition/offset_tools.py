import math
import struct

import pymem
import requests
import yaml
from PosRunTimeError import *
from ContainerHelp import *

link_url1 = "http://222.187.238.84:4232/list-files/csgo.yaml"
link_url2 = "http://222.187.238.84:4232/list-files/csgo_location.yaml"

try:
  req = requests.get(link_url1)
  req2 = requests.get(link_url2)
  yamlinfo = yaml.load(req.text,Loader=yaml.CLoader)
  locinfo = yaml.load(req2.text,Loader=yaml.CLoader)
except Exception:
  raise PosRunTimeError("验证基址失败! 请联系作者是否为文件失效!")

LOCAL_PLAYER = int(yamlinfo["signatures"]["dwLocalPlayer"])
HEALTH = int(yamlinfo["netvars"]["m_iHealth"])
FLAGS = int(yamlinfo["netvars"]["m_fFlags"])
m_vecVelocity = int(yamlinfo["netvars"]["m_vecVelocity"])

class _Offsets:
    def __init__(self):
        print("Start read csgo offsets...")
        try:
          self.pm_csgo = pymem.Pymem("csgo.exe")
        except Exception as E:
          raise PosRunTimeError("未找到csgo进程!")
        self.client = pymem.process.module_from_name(self.pm_csgo.process_handle, "client.dll").lpBaseOfDll
        self.materialSystem = pymem.process.module_from_name(self.pm_csgo.process_handle, "materialsystem.dll").lpBaseOfDll
        self.enginedll = pymem.process.module_from_name(self.pm_csgo.process_handle, "engine.dll").lpBaseOfDll
        self.X_address = self.enginedll + int(locinfo["location"]["x"])
        self.Y_address = self.enginedll + int(locinfo["location"]["y"])
        self.Z_address = self.enginedll + int(locinfo["location"]["z"])
        self.tangAddress = self.enginedll + int(locinfo["location"]["tang"])
        print("Finish read")

    @property
    def X(self) -> float:
        return self.pm_csgo.read_float(self.X_address)
    @property
    def Y(self) -> float:
        return self.pm_csgo.read_float(self.Y_address)
    @property
    def Z(self) -> float:
        return self.pm_csgo.read_float(self.Z_address)
    @property
    def Angle(self) -> float:
        return self.pm_csgo.read_float(self.tangAddress)
    @property
    def Velocity(self) -> float:
        client_dll = None
        for module in list(self.pm_csgo.list_modules()):
            if module.name == 'client.dll':
                client_dll = module.lpBaseOfDll

        local_player: int = self.pm_csgo.read_uint(client_dll + LOCAL_PLAYER)
        # 三轴速度
        if not local_player:
            return 0
        if not self.pm_csgo.read_int(local_player + HEALTH):
            return 0
        vec_bytes = self.pm_csgo.read_bytes(local_player + m_vecVelocity, 0XC)
        velocity = SpeedVector(*struct.unpack("3f", vec_bytes))
        spd = round(math.sqrt(math.pow(velocity.x_speed, 2) + math.pow(velocity.y_speed, 2)), 1)
        return spd

    def __str__(self):
        return "X: " + str(self.X) + " Y: " + str(self.Y) + " Z: " + str(self.Z)\
          + " Angle: " + str(self.Angle) + " Vel: " + str(self.Velocity)


offsets = _Offsets()







