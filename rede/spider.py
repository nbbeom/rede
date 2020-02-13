from enum import Enum, IntEnum
import json
import os
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from loguru import logger
from pydantic import BaseModel, Schema
from starlette.middleware.cors import CORSMiddleware
from starlette.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_202_ACCEPTED,
    HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, 
    HTTP_500_INTERNAL_SERVER_ERROR)
from typing import List
from rede.eth import get_Eth
import rede.wifi_test as wi

app = FastAPI()

@app.get(
    '/devices/',
    tags=['devices'])
def get_device():
    return get_Eth().get_device()

# @app.get(
#     '/ipconfig/',
#     tags=['ipconfig'])
# def get_network():
#     return get_Eth().show_detail2('wlan0')

@app.put(
    '/select_device/',
    tags=['show_dhcp'])
def select_device(device):
    if device == 'eth' :
        return get_Eth().dev_dict2()
    else :
        return get_Eth().show_detail2('eth'+device)

@app.put(
    '/select_device2/',
    tags=['show_parse'])

def select_device(device):
    if device == 'eth' :
        return get_Eth().dev_dict()
    else :
        return get_Eth().show_detail(device)
    
    device = input()
    ip =input()
    s.set_ip(device,ip)
# @app.put(
#     '/set_deviceIp/',
#     tags=['set_deviceAdress'])
# def set_address(device, ipaddr, mask, broadcast):
#     return get_Eth().set_address(device, ipaddr, mask, broadcast)
@app.put(
    '/wifi_List/',
    tags=['wifi_List'])
def wifi_List(device):
    wl = wi.Search(device)
    wifi_List = []

    for cell in wl :
        wifi_List.append(cell.ssid) 
        
    return wifi_List

#add wifi 
@app.put(
    '/wifi_Access/',
    tags=['wifi_Access'])
def wifi_Access(device,ssid,passwd=None):
    return wi.Connect(device,ssid,passwd)

@app.put(
    '/wifi_Delete/',
    tags=['wifi_Delete'])
def wifi_Access(ssid):
    return wi.Delete(ssid)

@app.put(
    '/set_deviceRoute/',
    tags=['set_deviceRoute'])
def set_Route(device, addr, mask,broadcast ,gateway):
    return get_Eth().set_route_rule(device, addr, mask,broadcast, gateway)