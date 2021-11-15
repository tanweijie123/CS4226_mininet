'''
Tan Wei Jie
A0202017B
'''

import sys
import os
from sets import Set

from pox.core import core

import pox.openflow.libopenflow_01 as of
import pox.openflow.discovery
import pox.openflow.spanning_forest

from pox.lib.revent import *
from pox.lib.util import dpid_to_str
from pox.lib.addresses import IPAddr, EthAddr

log = core.getLogger()

class Controller(EventMixin):
    def __init__(self):
        self.listenTo(core.openflow)
        core.openflow_discovery.addListeners(self)
        
        self.macToPort = {}
        
    def _handle_PacketIn (self, event):
        packet = event.parsed
        dpid = event.dpid
        src = packet.src
        dst = packet.dst
        inport = event.port     
        
        # install entries to the route table
        def install_enqueue(event, packet, outport, q_id):
            #log.info("Sw{} installing new routing: {}:{} -> {}:{}".format(dpid, src, inport, dst, outport))
            
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet, inport)
            msg.data = event.ofp
            msg.actions.append(of.ofp_action_output(port = outport))
            event.connection.send(msg)

        # Check the packet and decide how to route the packet
        def forward(message = None):
            #log.info("Sw{} finding routes for {}".format(dpid, dst))
            
            if dpid not in self.macToPort:
                #log.info("Sw{} no match found for {}".format(dpid, dst))
                flood()
            elif dst not in self.macToPort[dpid]:
                #log.info("Sw{} no match found for {}".format(dpid, dst))
                flood()
            else:
                #log.info("Sw{} found match for {}".format(dpid, dst))
                install_enqueue(event, packet, self.macToPort[dpid][dst], None)              

        # When it knows nothing about the destination, flood but don't install the rule
        def flood (message = None):
            #log.info("Sw{} flooding: {}:{} -> *".format(dpid, src, inport))

            # define your message here

            # ofp_action_output: forwarding packets out of a physical or virtual port
            # OFPP_FLOOD: output all openflow ports expect the input port and those with 
            #    flooding disabled via the OFPPC_NO_FLOOD port config bit
            # msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
        
            msg = of.ofp_packet_out()
            msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
            msg.data = event.ofp
            msg.in_port = inport
            event.connection.send(msg)
        
        # add new src to map then forward 
        if dpid not in self.macToPort:
            self.macToPort[dpid] = {}
        self.macToPort[dpid][src] = inport 
        forward()


    def _handle_ConnectionUp(self, event):
        dpid = dpid_to_str(event.dpid)
        log.debug("Switch %s has come up.", dpid)
        
        # Send the firewall policies to the switch
        def sendFirewallPolicy(connection, policy):
            # define your message here
            
            # OFPP_NONE: outputting to nowhere
            # msg.actions.append(of.ofp_action_output(port = of.OFPP_NONE))
            x = 1

        for i in [FIREWALL_POLICIES]:
            sendFirewallPolicy(event.connection, i)
            

def launch():
    # Run discovery and spanning tree modules
    pox.openflow.discovery.launch()
    pox.openflow.spanning_forest.launch()

    # Starting the controller module
    core.registerNew(Controller)
