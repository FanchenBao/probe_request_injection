
import signal, sys
import logging
logging.getLogger().setLevel(logging.INFO)

from scapy.all import sendp,Dot11,RadioTap,RandMAC
from time import sleep
from multiprocessing import Process
import os
from datetime import datetime


def custom_mac():
    timestamp = datetime.now().strftime('%H:%M')
#    return f'11:11:11:{timestamp}'
    return timestamp


def pq_flood(device, interval):
    sendp(RadioTap()/
      Dot11(type=0,subtype=4,
      addr1="ff:ff:ff:ff:ff:ff",
#      addr2="11:11:11:11:11:11",
#      addr2=custom_mac(),
      addr2=RandMAC(f'{custom_mac()}:11'),
      addr3="ff:ff:ff:ff:ff:ff"),
      iface=device, loop=1, inter=interval)





device = 'wlan1'
interval = 0.05

print('Press CTRL+C to Abort')
#p = Process(target=pq_flood, args=(device, interval,))
#p.start()
#pid = p.pid
#p.join(60)
#os.kill(pid, signal.SIGINT)
pq_flood(device, interval)
