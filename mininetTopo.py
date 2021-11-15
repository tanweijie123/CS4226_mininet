'''
Tan Wei Jie
A0202017B
'''

import os
import sys
import atexit
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.link import TCLink, Link
from mininet.node import RemoteController

net = None

class TreeTopo(Topo):

    def __init__(self):
        # Initialize topology
        Topo.__init__(self)
        
        hosts = []
        switches = []
        file = open("topology.in","r")
        
        numHosts, numSwitches, numLinks = file.readline().split(' ')
        print('There are {} hosts, {} switches, {} links'.format(numHosts, numSwitches, numLinks))
        
        for h in range(int(numHosts)):
            host = self.addHost('h%s' % (h+1))
            hosts.append(host)
        
        for s in range(int(numSwitches)):
            switch = self.addSwitch('s%s' % (s+1))
            switches.append(switch)
        
        for l in range(int(numLinks)):
            src, dest, speed = file.readline().split(',')
            
            # get from correct array
            if (src[0] == 'h'):
                src = hosts[int(src[1]) - 1]
            else:
                src = switches[int(src[1]) - 1]
            
            if (dest[0] == 'h'):
                dest = hosts[int(dest[1]) - 1]
            else:
                dest = switches[int(dest[1]) - 1]
            
            self.addLink(src, dest, cls=TCLink, bw=int(speed))
            

def startNetwork():
    info('** Creating the tree network\n')
    topo = TreeTopo()

    global net
    net = Mininet(topo=topo, link=Link,
                  controller=lambda name: RemoteController(name, ip='45.32.104.61'),
                  listenPort=6633, autoSetMacs=True)

    info('** Starting the network\n')
    net.start()

    # Create QoS Queues
    # > os.system('sudo ovs-vsctl -- set Port [INTERFACE] qos=@newqos \
    #            -- --id=@newqos create QoS type=linux-htb other-config:max-rate=[LINK SPEED] queues=0=@q0,1=@q1,2=@q2 \
    #            -- --id=@q0 create queue other-config:max-rate=[LINK SPEED] other-config:min-rate=[LINK SPEED] \
    #            -- --id=@q1 create queue other-config:min-rate=[X] \
    #            -- --id=@q2 create queue other-config:max-rate=[Y]')

    info('** Running CLI\n')
    CLI(net)


def stopNetwork():
    if net is not None:
        net.stop()
        # Remove QoS and Queues
        os.system('sudo ovs-vsctl --all destroy Qos')
        os.system('sudo ovs-vsctl --all destroy Queue')


if __name__ == '__main__':
    # Force cleanup on exit by registering a cleanup function
    atexit.register(stopNetwork)

    # Tell mininet to print useful information
    setLogLevel('info')
    startNetwork()
