#!/usr/bin/env python3
import re
import matplotlib.pyplot as plt

# 1. Parse Throughput Data
algos = ['reno', 'cubic']
delays = ['10ms', '100ms']
losses = [0, 1]

results = {}

print("Parsing iperf output...")
for algo in algos:
    for delay in delays:
        for loss in losses:
            filename = f"results_{algo}_{delay}_{loss}.txt"
            throughput = 0.0
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                    # iperf outputs a summary at the end, we grab the Mbits/sec value
                    matches = re.findall(r'(\d+\.?\d*)\s*Mbits/sec', content)
                    if matches:
                        throughput = float(matches[-1]) # Last match is the total run
                    else:
                        # Fallback just in case it dropped to Kbits/sec
                        matches_k = re.findall(r'(\d+\.?\d*)\s*Kbits/sec', content)
                        if matches_k:
                            throughput = float(matches_k[-1]) / 1000.0
            except FileNotFoundError:
                print(f"Error: Missing file {filename}")
            
            results[(algo, delay, loss)] = throughput

# Print the required summary table
print("\n=== Throughput Summary Table (Mbits/sec) ===")
print(f"{'Algorithm':<10} | {'Delay':<8} | {'Loss':<6} | {'Throughput'}")
print("-" * 45)
for key, val in results.items():
    print(f"{key[0].upper():<10} | {key[1]:<8} | {key[2]}%    | {val:.2f} Mbps")
print("-" * 45)

# Generate Throughput Bar Chart
labels = [f"{d}, {l}%" for d in delays for l in losses]
reno_tb = [results[('reno', d, l)] for d in delays for l in losses]
cubic_tb = [results[('cubic', d, l)] for d in delays for l in losses]

x = range(len(labels))
width = 0.35

fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.bar([i - width/2 for i in x], reno_tb, width, label='Reno')
ax1.bar([i + width/2 for i in x], cubic_tb, width, label='Cubic')

ax1.set_ylabel('Throughput (Mbits/sec)')
ax1.set_title('TCP Throughput vs Network Conditions')
ax1.set_xticks(x)
ax1.set_xticklabels(labels)
ax1.legend()
plt.tight_layout()
plt.savefig('throughput_plot.png')
print("-> Saved throughput plot to throughput_plot.png")

# 2. Parse CWND Data
cwnd_file = "cwnd_reno_10ms_0.txt"
cwnds = []
print("\nParsing ss socket data...")
try:
    with open(cwnd_file, 'r') as f:
        for line in f:
            # Look for the cwnd parameter in the ss output
            match = re.search(r'cwnd:(\d+)', line)
            if match:
                cwnds.append(int(match.group(1)))
except FileNotFoundError:
    print(f"Error: Missing file {cwnd_file}")

# Generate CWND Line Chart
if cwnds:
    # We sampled the network every 0.1 seconds in the bash script
    times = [i * 0.1 for i in range(len(cwnds))]
    
    fig, ax2 = plt.subplots(figsize=(10, 6))
    ax2.plot(times, cwnds, color='blue', linewidth=1.5)
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylabel('Congestion Window (cwnd) in MSS')
    ax2.set_title('TCP Reno Congestion Window over Time (10ms delay, 0% loss)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('cwnd_plot.png')
    print("-> Saved cwnd plot to cwnd_plot.png")