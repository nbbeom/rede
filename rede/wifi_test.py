# # -*- coding: utf-8 -*-
# #scheme.py 내부를 수정함
# #    subprocess.check_output(['/sbin/ifdown', self.interface], stderr=subprocess.STDOUT) ->
# #    subprocess.check_output(['/sbin/ifconfig', self.interface,'down'], stderr=subprocess.STDOUT)
# # have found is that ifdown/ifup don't seem to be used anymore.
# #/home/ubuntu/.local/share/virtualenvs/rede-7j8-Szxl/lib/python3.7/site-packages/wifi/scheme.py", line 133,
import wifi


def Search(dev):
    wifilist = []

    cells = wifi.Cell.all(dev)
    for cell in cells:
        wifilist.append(cell)
        
    return wifilist


def FindFromSearchList(dev,ssid):
    wifilist = Search(dev)
    print(wifilist)
    for cell in wifilist:
        if cell.ssid == ssid:
            return cell

    return False


def FindFromSavedList(ssid):
    cell = wifi.Scheme.find('wlan0', ssid)

    if cell:
        return cell

    return False

def Connect(device,ssid, password=None):
    cell = FindFromSearchList(device,ssid)

    if cell:
        savedcell = FindFromSavedList(cell)

        # Already Saved from Setting
        if savedcell:
            savedcell.activate()
            return cell

        # First time to conenct
        else:
            if cell.encrypted:
                if password:
                    scheme = Add(cell, password)

                    try:
                        scheme.activate()
                    # Wrong Password
                    except wifi.exceptions.ConnectionError:
                        Delete(ssid)
                        return False

                    return cell
                else:
                    return False
            else:
                scheme = Add(cell)

                try:
                    scheme.activate()
                except wifi.exceptions.ConnectionError:
                    Delete(ssid)
                    return False

                return cell
    
    return False

def Add(cell, password=None):
    if not cell:
        return False

    scheme = wifi.Scheme.for_cell('wlan0', cell.ssid, cell, password)
    scheme.save()
    return scheme

def Delete(ssid):
    if not ssid:
        return False

    cell = FindFromSavedList(ssid)

    if cell:
        cell.delete()
        return True

    return False


if __name__ == '__main__':
    # Search WiFi and return WiFi list

    # 연결 가능 한 wifi 탐색
            # wifi 연결해제
    Search()
    Connect('__telelian','qwer1234')

        # wifi 연결해제
    # Delete('__telelian')

# from wpa_supplicant.core import WpaSupplicantDriver
# from twisted.internet.selectreactor import SelectReactor
# import threading
# import time
# import errno
# import sys
# import types
# import netifaces
# import dbus

# class PythonWifiScanner:

#     wifiAccessPoints = []

#     def __init__(self,reactor):
#         self._reactor = reactor
#         threading.Thread(target=self._reactor.run, kwargs={'installSignalHandlers': 0}).start()
#         time.sleep(0.2)  # let reactor start
#         self.driver = WpaSupplicantDriver(reactor)
#         self.supplicant = self.driver.connect()

#         # get network interfaces

#         self.net_iface = netifaces.interfaces()

#     def get_configured_networks(self,interfaceNumber):
#         return self.supplicant.get_interface(self.net_iface[interfaceNumber].decode()).get_networks()

#     def get_single_wpa_interface(self,interfaceNumber):
#         return self.supplicant.get_interface(self.net_iface[interfaceNumber].decode())

#     def get_interfaces(self):
#         return self.net_iface

#     def select_network(self,network_path,interfaceNumber):
#         return self.supplicant.get_interface(self.net_iface[interfaceNumber].decode()).select_network(network_path)

#     def add_network(self,network_cfg,interfaceNumber):
#         return self.supplicant.get_interface(self.net_iface[interfaceNumber].decode()).add_network(network_cfg)

#     def scan_interface_for_networks(self,interfaceNumber):
#         # Get interface and scan the network
#         interface = self.supplicant.get_interface(self.net_iface[interfaceNumber].decode())
#         wifiNetworks = interface.scan(block=True)
#         self.wifiAccessPoints = [] 
#         for singleWifi in wifiNetworks:
#             self.wifiAccessPoints.append(singleWifi.get_ssid())
#         return wifiNetworks

# # Start a simple Twisted SelectReactor

# sample_network_cfg  = {}
# sample_network_cfg['psk'] = "EnterYourKeyHere"
# sample_network_cfg['ssid'] = "EnterYourWifiHere"
# sample_network_cfg['key_mgmt'] = "WPA-PSK"
# reactor = SelectReactor()
# dave=PythonWifiScanner(reactor)
# value = None
# bus = dbus.SystemBus()


# print ("Interface:" + dave.get_interfaces()[3])

# # scan for available networks

# for singleWifi in dave.scan_interface_for_networks(3):
#     print( "Wifi SSID:" + singleWifi.get_ssid())
#     print ("Wifi Network Type:" + singleWifi.get_network_type())

# # Add network configuration to wpa_supplicant 

# configpath = dave.add_network(sample_network_cfg,3)

# # Attach and Select your network (will need to setip address)
# dave.select_network(configpath.get_path(),3)
# reactor.stop()