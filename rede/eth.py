import asyncio
import functools
import ipaddress
import os
import re
import socket
from pyroute2 import IPDB
from loguru import logger
from pyroute2 import IPRoute
import time
import socket, fcntl, struct
import rede.dhclient as dhclient
import netifaces
def release(self):
    IPDB().release()

def get_interfaces():
    return IPDB().interfaces
def get_ipv4(iface):
    if not IPDB().interfaces[iface].ipaddr:
        None

    return IPDB().interfaces[iface]

def get_ifname(iface):
    exp = os.getenv('TRIANGLE_IFNAME_REGEX', '(eth|wlan)[0-4]')
    if not re.match(exp, str(iface)):
        return None

    # operstate = IPDB().interfaces[iface].operstate
    # if operstate in ('DOWN', 'DORMANT') :
    #     return None
    return IPDB().interfaces[iface].ifname

# def delete_ip(ifname,ipaddr,sm):
#     IPDB().interfaces[ifname].del_ip(ipaddr,24).commit()

def get_detail(iface):
    adr = IPRoute().get_addr(label=iface)
    rt= IPRoute().get_routes()
    gatewaybox=""
    net_clear_for_Gateway = list(netifaces.gateways()[2])
    print(netifaces.gateways())
    for i in range(0,len(rt)):
        if rt[i]['attrs'][2][1] == adr[0]['attrs'][0][1]:
            rt[i]['attrs'][2]
    for i in range(0,len(net_clear_for_Gateway)):
        if net_clear_for_Gateway[i][1] == iface :
            gatewaybox=net_clear_for_Gateway[i][0]
    if gatewaybox == "":
        gatewaybox="null"
    res = {
        'address': adr[0]['attrs'][0][1],
        'mask' : IPDB().interfaces[iface]['ipaddr'][0]['prefixlen'],
        'broadcast' : adr[0]['attrs'][2][1],
        'gateway'   : gatewaybox,
     }
    logger.debug({
            'title': 'ipr',
            'result': res,
    })

    return res


def get_dhcp(ifname):
    info = dhclient.action(ifname)
    res = {
            'address'   : info['yiaddr'],
            'mask'      : info['options']['subnet_mask'],
            'broadcast' : info['yiaddr'].rsplit('.', 1)[0] + '.255',
            'gateway'   : info['options']['router'][0],
     }

    logger.debug({
            'title': 'dhcp',
            'result': res,
    })

    return res    

def print_dhcp(res):
    print(res)

class get_Eth:
    def __init__(self):
        self._ipdb = IPDB()

    def dev_show(iface): 
        ifname =  get_ifname(iface)
        if not ifname:
            return
        return ifname

    def get_device(self):
        eth_name =[]
        res = [] 
        for iface in get_interfaces():
            try:
                eth_name.append(get_Eth.dev_show(iface))
            except Exception as e:
                logger.exception(e)
        #쓰레기값
        for val in eth_name: 
            if val != None : 
                res.append(val)
        return res

        ifname =  get_ifname(iface)
        if not ifname:
            return
        return ifname

    #print addr mask gateway braodcast use pyroute2 and netifaces  
    def show_detail(self,ifname):
        addr =  get_ipv4(ifname)
        res ={}
        res[ifname] = get_detail(ifname)
        return res

    #print DHCP addr mask gateway braodcast
    def show_detail2(self,ifname):
        addr =  get_ipv4(ifname)
        res ={}
        res[ifname] = get_dhcp(ifname)
        return res

    #for json
    def dev_dict(self):
        devices=get_Eth.get_device(self)
        res = {}
        for i in devices:
            try:
                res[i]={}
                res[i]=self.show_detail(i)
            except Exception as e:
                logger.exception(e)
        return res

    #for json dhcp
    def dev_dict2(self):
        devices=get_Eth.get_device(self)
        res = {}
        for i in devices:
            try:
                res[i]={}
                res[i]=self.show_detail2(i)
            except Exception as e:
                logger.exception(e)
        return res

    #set address do not change gateway
    def set_address(self, ifname, addr, mask, broadcast):
        with self._ipdb.interfaces[ifname] as eth:
            a=str(eth.ipaddr.ipv4[0]['address'])
            sm_network = eth['ipaddr'][0]['prefixlen']
            eth.del_ip(a,sm_network).commit()
            return eth.add_ip(
                addr, mask=mask, broadcast=broadcast)
    #set address and gateway
    def set_route_rule(self, ifname, addr, mask,broadcast, gateway):
        oif = self._ipdb.interfaces[ifname].index
        rt_idx = self._get_rt_idx(ifname)
        sm_network = self._ipdb.interfaces[ifname]['ipaddr'][0]['prefixlen']

        logger.debug({
            'ifname': ifname,
            'addr': addr,
            'gateway': gateway,
            'oif': oif,
            'rt_table_index': rt_idx,
            'subnet_mask': sm_network,
        })
        self._remove_rule(rt_idx)
        self._add_rule(rt_idx, sm_network)
        self._remove_route(rt_idx)
        self._add_route(rt_idx,addr, gateway, oif)
        self.set_address(ifname, addr, mask, broadcast)
        with self._ipdb.interfaces[ifname] as eth:
            a=str(eth.ipaddr.ipv4[0]['address'])
            eth.del_ip(a,sm_network).commit()
            return eth.add_ip(
                addr, mask=mask, broadcast=broadcast)
        
    def _get_rt_idx(self, ifname):
        # set rules and routes
        rt_tables = {
            'eth0': 10,
            'eth1': 11,
            'eth2': 12,
            'eth3': 13,
            'eth4': 14,
            'wlan0': 20,
            'wlan1': 21,
            'wlan2': 22,
            'wlan3': 23,
            'wlan4': 24,
        }

        return rt_tables[ifname]

    # 192.168.0.100/24
    def _get_subnet_mask_network(self, addr, sm):
        return str(ipaddress.ip_interface(addr + '/' + sm).network)

    def _remove_rule(self, rt_idx):
        spec = {
            'table': rt_idx,
        }
        logger.debug({
            'spec': spec,
        })
        print(self._ipdb.rules)
        try:
            self._ipdb.rules[spec].remove().commit()
        except Exception as e :
            logger.warning({
                'msg' :e,
                
            })

    def _add_rule(self, rt_idx, mask):
        spec = {
            'src': mask,
            'table': rt_idx,
        }
        logger.debug({
            'spec': spec,
        })
        
        self._ipdb.rules.add(spec)

    def _remove_route(self, rt_idx):
        spec = {
            'table': rt_idx,
        }
        logger.debug({
            'spec': spec,
        })
        try:
            self._ipdb.routes.tables[rt_idx][
                {'table': rt_idx}].remove()
        except Exception as e :
            logger.warning({
                'msg' :e,
                
            })
        # .remove().commit
    def _add_route(self, rt_idx, new_ip,gateway, oif):
        spec = {
            'dst': 'default',
            'gateway': gateway,
            'oif': oif,
            'table': rt_idx,
        }
        logger.debug({
            'spec': spec,
        })
        print(spec)
        self._ipdb.routes.add(spec).commit()


# # specify table and priority