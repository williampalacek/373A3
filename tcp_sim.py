#!/usr/bin/env python3
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.log import setLogLevel, info
import argparse
import time

class AssignmentTopo(Topo):
    def build(self, link_delay, link_loss):
        # Initialize the two switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Initialize the hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        # Add high-speed access links
        self.addLink(h1, s1, bw=100)
        self.addLink(s2, h2, bw=100)

        # Add bottleneck link between s1 and s2
        self.addLink(s1, s2, bw=10, delay=link_delay, loss=link_loss)

def run_experiment(algo, delay, loss, record_cwnd):
    topo = AssignmentTopo(link_delay=delay, link_loss=loss)
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    h1, h2 = net.get('h1', 'h2')

    # Set TCP congestion control algorithm
    h1.cmd(f'sysctl -w net.ipv4.tcp_congestion_control={algo}')
    h2.cmd(f'sysctl -w net.ipv4.tcp_congestion_control={algo}')

    info(f"\n--- Running: {algo.upper()}, {delay}, {loss}% loss ---\n")

    # Start iperf server on h2
    h2.cmd('iperf -s &')
    time.sleep(1) # Give server a second to spin up

    # If this is our chosen run for cwnd, start recording in the background
    cwnd_file = f"cwnd_{algo}_{delay}_{loss}.txt"
    if record_cwnd:
        info("*** Recording cwnd data in background...\n")
        # Use 'ss' to poll TCP info every 0.1 seconds
        h1.cmd(f'while true; do ss -ti | grep -A 1 "10.0.0.2:5001" >> {cwnd_file}; sleep 0.1; done &')
        monitor_pid = h1.cmd('echo $!')

    # Run iperf client on h1 for 30 seconds
    result = h1.cmd('iperf -c 10.0.0.2 -t 30')
    print(result)

    # Clean up background processes
    if record_cwnd:
        h1.cmd(f'kill {monitor_pid}')
    h2.cmd('kill %iperf')
    
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    parser = argparse.ArgumentParser(description='ELEC 373 Assignment 4 TCP Simulation')
    parser.add_argument('--algo', type=str, required=True, choices=['reno', 'cubic'], help='TCP variant')
    parser.add_argument('--delay', type=str, required=True, help='Link delay (e.g., 10ms)')
    parser.add_argument('--loss', type=int, required=True, help='Packet loss percentage (e.g., 0 or 1)')
    parser.add_argument('--cwnd', action='store_true', help='Flag to record cwnd')
    
    args = parser.parse_args()
    run_experiment(args.algo, args.delay, args.loss, args.cwnd)