#!/bin/bash

# Clear old kernel interfaces just in case
sudo mn -c

# Define parameters
algos=("reno" "cubic")
delays=("10ms" "100ms")
losses=(0 1)

# Loop through all 8 combinations
for algo in "${algos[@]}"; do
    for delay in "${delays[@]}"; do
        for loss in "${losses[@]}"; do
            
            # We only need cwnd for ONE scenario. Let's pick Reno, 10ms, 0% loss.
            if [ "$algo" == "reno" ] && [ "$delay" == "10ms" ] && [ "$loss" -eq 0 ]; then
                echo "Running $algo with $delay delay and $loss% loss (RECORDING CWND)..."
                sudo python3 tcp_sim.py --algo $algo --delay $delay --loss $loss --cwnd > results_${algo}_${delay}_${loss}.txt
            else
                echo "Running $algo with $delay delay and $loss% loss..."
                sudo python3 tcp_sim.py --algo $algo --delay $delay --loss $loss > results_${algo}_${delay}_${loss}.txt
            fi
            
            # Give the OS a moment to clean up network namespaces between runs
            sleep 2
        done
    done
done

echo "All 8 experiments completed. Check the results_*.txt files for throughput."