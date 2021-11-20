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
from mininet.link import Link
from mininet.node import RemoteController

net = None
linkspeedTuple = {}

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
            
            self.addLink(src, dest)
            linkspeedTuple[(src, dest)] = int(speed);
            

def startNetwork():
    info('** Creating the tree network\n')
    topo = TreeTopo()

    global net
    net = Mininet(topo=topo, link=Link,
                  controller=lambda name: RemoteController(name, ip='45.32.104.61'),
                  listenPort=6633, autoSetMacs=True)

    info('** Starting the network\n')
    net.start()

    info("** Create QoS Queues\n")
    
    # q0 = normal queue
    # q1 = premium queue
    
    def getLinkSpeedInBps(node1, node2):
        linkspeed = 0
        if (src, dst) in linkspeedTuple:
            linkspeed = linkspeedTuple[(src,dst)]
        elif (dst, src) in linkspeedTuple:
            linkspeed = linkspeedTuple[(dst,src)]
        
        return linkspeed * 1000000 # convert Mbps -> bps
    
    for link in net.topo.links(True, False, True):
        src = link[0]
        dst = link[1]
        interface0 = '{}-eth{}'.format(src, link[2]['port1'])
        interface1 = '{}-eth{}'.format(dst, link[2]['port2'])
        info("*** Setting {} QoS\n".format(interface1))
        
        if (src[0] == 's' and dst[0] == 's'): # check if it is switch -- switch
            switch_linkspeed = getLinkSpeedInBps(src, dst)
        
            os.system("sudo ovs-vsctl -- set Port %s qos=@newqos \
                    -- --id=@newqos create QoS type=linux-htb other-config:max-rate=%i queues=0=@q0,1=@q1 \
                    -- --id=@q0 create queue other-config:max-rate=%i other-config:min-rate=%i \
                    -- --id=@q1 create queue other-config:max-rate=%i other-config:min-rate=%i"
                    % (interface0, switch_linkspeed, switch_linkspeed, switch_linkspeed, switch_linkspeed, switch_linkspeed))
            os.system("sudo ovs-vsctl -- set Port %s qos=@newqos \
                    -- --id=@newqos create QoS type=linux-htb other-config:max-rate=%i queues=0=@q0,1=@q1 \
                    -- --id=@q0 create queue other-config:max-rate=%i other-config:min-rate=%i \
                    -- --id=@q1 create queue other-config:max-rate=%i other-config:min-rate=%i"
                    % (interface1, switch_linkspeed, switch_linkspeed, switch_linkspeed, switch_linkspeed, switch_linkspeed))
        
        elif (src[0] == 's' or dst[0] == 's'): # check if it is host -- switch
            host_linkspeed = getLinkSpeedInBps(src, dst)
            premium_link = 0.8 * host_linkspeed
            general_link = 0.5 * host_linkspeed
            
            interface = interface0
            if (dst[0] == 's'): 
                interface = interface1
            
            os.system("sudo ovs-vsctl -- set Port %s qos=@newqos \
                    -- --id=@newqos create QoS type=linux-htb other-config:max-rate=%i queues=0=@q0,1=@q1 \
                    -- --id=@q0 create queue other-config:max-rate=%i other-config:min-rate=%i \
                    -- --id=@q1 create queue other-config:max-rate=%i other-config:min-rate=%i"
                    % (interface, host_linkspeed, general_link, general_link, host_linkspeed, premium_link))
            

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
