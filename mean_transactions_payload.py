import re
import pandas as pd

log_files_ego = [
    'network-ego/node-1/logs/geth.log',
    'network-ego/node-2/logs/geth.log',
    'network-ego/node-3/logs/geth.log',
    'network-ego/node-4/logs/geth.log'
]

log_files_network2 = [
    'network 2/network/node-1/logs/geth.log',
    'network 2/network/node-2/logs/geth.log',
    'network 2/network/node-3/logs/geth.log',
    'network 2/network/node-4/logs/geth.log',
    'network 2/network/node-5/logs/geth.log'
]

# Regular expression pattern to match lines with "Updated payload" and "txs="
pattern = re.compile(r'Updated payload\s+.*txs=(\d+)')

node_stats = {}

def process_logs(log_files, network_name):
    for i, log_file in enumerate(log_files):
        node_key = f'{network_name}_node-{i+1}'
        node_stats[node_key] = {'total_txs': 0, 'count': 0}
        
        with open(log_file, 'r') as file:
            for line in file:
                match = pattern.search(line)
                if match:
                    txs = int(match.group(1))
                    if txs > 0:
                        node_stats[node_key]['total_txs'] += txs
                        node_stats[node_key]['count'] += 1


process_logs(log_files_ego, 'network_ego')
process_logs(log_files_network2, 'network_2')

# Calculate the mean number of transactionS
mean_txs = {node: stats['total_txs'] / stats['count'] if stats['count'] > 0 else 0 
            for node, stats in node_stats.items()}

# Display the results
for node, mean in mean_txs.items():
    print(f'{node}: Mean transactions = {mean:.2f}')

df = pd.DataFrame(list(mean_txs.items()), columns=['Node', 'Mean Transactions'])
print(df)