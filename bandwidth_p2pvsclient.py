import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


log_file = 'bandwidth_logs/node_1_metrics.txt'

data = []
with open(log_file, 'r') as f:
    for line in f:
        parts = line.strip().split(', ')
        timestamp = datetime.strptime(parts[0], "%Y-%m-%dT%H:%M:%S.%f")
        
        # Extract the p2p_egress_count and miner_egress_count
        p2p_egress_count = int(parts[1].split('=')[1])
        miner_egress_count = int(parts[7].split('=')[1])
        
        data.append({
            'timestamp': timestamp, 
            'p2p_egress_count': p2p_egress_count,
            'miner_egress_count': miner_egress_count
        })

df = pd.DataFrame(data)

# Calculate the elapsed time in seconds from the start
df['seconds'] = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()

# Calculate the bandwidth bytes/second
df['p2p_bandwidth'] = df['p2p_egress_count'].diff()
df['miner_bandwidth'] = df['miner_egress_count'].diff()

# Remove the first row
df = df.dropna()


plt.figure(figsize=(10, 6))
plt.plot(df['seconds'], df['p2p_bandwidth'], linestyle='-', color='r', label='p2p')
plt.plot(df['seconds'], df['miner_bandwidth'], linestyle='-', color='orange', label='client node')
plt.xlabel('Time (seconds)')
plt.ylabel('Bandwidth (bytes/second)')
plt.title('Bandwidth Over Time: peer to peer vs client node outbound')
plt.legend()
plt.grid(True)
plt.savefig('bandwidth_plot_node_0.pdf')
plt.close()

