import pandas as pd
import matplotlib.pyplot as plt
import re

geth_logs_0_to_4 = [
    'network 2/network/node-0/logs/geth.log',
    'network 2/network/node-1/logs/geth.log',
    'network 2/network/node-2/logs/geth.log',
    'network 2/network/node-3/logs/geth.log',
    'network 2/network/node-4/logs/geth.log'
]

geth_log_5 = 'network 2/network/node-5/logs/geth.log'

geth_logs_ego = [
    'network-ego/node-0/logs/geth.log',
    'network-ego/node-1/logs/geth.log',
    'network-ego/node-2/logs/geth.log',
    'network-ego/node-3/logs/geth.log',
    'network-ego/node-4/logs/geth.log'
]

# Regular expression pattern to match the lines with "INFO Test time"
pattern = re.compile(r'INFO.*Test time\s+ID=(\d+).*timestamp=(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{9})')

def process_logs(log_files):
    ids = []
    timestamps = []
    block_ids = []
    
    for log_file in log_files:
        with open(log_file, 'r') as file:
            for line in file:
                match = pattern.search(line)
                if match:
                    ids.append(int(match.group(1)))
                    timestamps.append(match.group(2))
                    # Extract Block ID if available; else set to None
                    block_id_match = re.search(r'"Block id"=(<nil>|\d+)', line)
                    block_ids.append(block_id_match.group(1) if block_id_match else None)
    
    df = pd.DataFrame({
        'ID': ids,
        'Timestamp': pd.to_datetime(timestamps),
        'Block ID': block_ids
    })
    
    # Sort the DataFrame by the Timestamp
    df_sorted = df.sort_values(by='Timestamp')

    # Identify the indices where ID is 1 and the next row has ID 6
    drop_indices = df_sorted[(df_sorted['ID'] == 1) & (df_sorted['ID'].shift(-1) == 6)].index
    drop_indices_next = drop_indices + 1  # Include the next row as well

    # Combine the indices and drop the rows
    df_sorted = df_sorted.drop(drop_indices.union(drop_indices_next))

    # Calculate the time differences
    id_1 = df_sorted[df_sorted['ID'] == 1].reset_index(drop=True)
    id_6 = df_sorted[df_sorted['ID'] == 6].reset_index(drop=True)
    min_length = min(len(id_1), len(id_6))
    id_1 = id_1.iloc[:min_length]
    id_6 = id_6.iloc[:min_length]

    time_diffs = id_6['Timestamp'] - id_1['Timestamp']
    time_diffs_milliseconds = time_diffs.dt.total_seconds() * 1000
    
    return time_diffs_milliseconds, df_sorted

time_diffs_milliseconds_0_to_4, df_sorted_0_to_4 = process_logs(geth_logs_0_to_4)

# Get the first and last timestamps from nodes 0 to 4
start_time = df_sorted_0_to_4['Timestamp'].min()
end_time = df_sorted_0_to_4['Timestamp'].max()

# Process logs for node 5
ids_5 = []
timestamps_5 = []

with open(geth_log_5, 'r') as file:
    for line in file:
        match = pattern.search(line)
        if match:
            timestamp = pd.to_datetime(match.group(2))
            # Keep only IDs 1 and 6 and within the time range of nodes 0 to 4
            if match.group(1) in ['1', '6'] and start_time <= timestamp <= end_time:
                ids_5.append(int(match.group(1)))
                timestamps_5.append(timestamp)

df_5 = pd.DataFrame({
    'ID': ids_5,
    'Timestamp': pd.to_datetime(timestamps_5)
})

# Ensure both DataFrames have the same length
id_1_5 = df_5[df_5['ID'] == 1].reset_index(drop=True)
id_6_5 = df_5[df_5['ID'] == 6].reset_index(drop=True)
min_length_5 = min(len(id_1_5), len(id_6_5))
id_1_5 = id_1_5.iloc[:min_length_5]
id_6_5 = id_6_5.iloc[:min_length_5]

# Compute the time differences for node 5
time_diffs_5 = id_6_5['Timestamp'] - id_1_5['Timestamp']
time_diffs_milliseconds_5 = time_diffs_5.dt.total_seconds() * 1000

time_diffs_milliseconds_ego, _ = process_logs(geth_logs_ego)

# Combine the time differences from all sets into a list
time_diffs_combined = [
    time_diffs_milliseconds_ego,
    time_diffs_milliseconds_0_to_4,
    time_diffs_milliseconds_5    
]

colors = ['skyblue', 'lightgreen', 'lightcoral']

plt.figure(figsize=(10, 6))
box = plt.boxplot(time_diffs_combined, patch_artist=True, tick_labels=['Modified Nodes inside eGo', 'Modified Nodes outside eGo', 'Regular Nodes'], showfliers=False)
for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)
plt.title('Comparison of Time to Build a Block with generateWork()')
plt.ylabel('Time Difference (milliseconds)')
plt.grid(True)
plt.savefig('time_differences_boxplot_comparison.pdf')
plt.close()
