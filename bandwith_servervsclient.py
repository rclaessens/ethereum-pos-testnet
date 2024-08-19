import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

log_files = [f'bandwidth_logs/node_{i}_metrics.txt' for i in range(5)]


dfs = []

for i, log_file in enumerate(log_files):
    data = []
    with open(log_file, 'r') as f:
        for line in f:

            parts = line.strip().split(', ')
            timestamp = datetime.strptime(parts[0], "%Y-%m-%dT%H:%M:%S.%f")
            
            # Extract miner_egress_count
            miner_egress_count = int(parts[7].split('=')[1])
            
            data.append({'timestamp': timestamp, 
                         'miner_egress_count': miner_egress_count})
            
    df = pd.DataFrame(data)

    # Calculate the elapsed time in seconds from the start
    df['seconds'] = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()

    # Calculate the bandwidth bytes/second
    df['miner_bandwidth'] = df['miner_egress_count'].diff()

    # Remove the first row
    df = df.dropna()

    dfs.append((i, df))


plt.figure(figsize=(10, 6))
for i, df in dfs:
    label = 'Server Node' if i == 0 else f'Client Node {i}'
    plt.plot(df['seconds'], df['miner_bandwidth'], linestyle='-', label=label)

plt.xlabel('Time (seconds)')
plt.ylabel('Bandwidth (bytes/second)')
plt.title('Outbound communication Bandwidth Over Time for All Nodes')
plt.legend()
plt.grid(True)
plt.savefig('bandwidth_plot_all_nodes.pdf')
plt.close()
