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
        
        # s1 config
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        s1 = self.addSwitch('s1');
        self.addLink(h1, s1, cls=TCLink, bw=int(10))
        self.addLink(h2, s1, cls=TCLink, bw=int(10))

        # s2 config
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        s2 = self.addSwitch('s2');
        self.addLink(h3, s2, cls=TCLink, bw=int(10))
        self.addLink(h4, s2, cls=TCLink, bw=int(10))

        # s3 config
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')
        s3 = self.addSwitch('s3')
        self.addLink(h5, s3, cls=TCLink, bw=int(10))
        self.addLink(h6, s3, cls=TCLink, bw=int(10))
        self.addLink(h7, s3, cls=TCLink, bw=int(10))

        # s4 config
        s4 = self.addSwitch('s4')

        # switches network
        self.addLink(s1, s2, cls=TCLink, bw=int(1000))
        self.addLink(s2, s3, cls=TCLink, bw=int(1000))
        self.addLink(s3, s4, cls=TCLink, bw=int(1000))
        self.addLink(s1, s4, cls=TCLink, bw=int(1000))
        

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
