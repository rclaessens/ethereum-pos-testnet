import pandas as pd
import matplotlib.pyplot as plt
import re

geth_logs_ego = [
    'network-ego/node-0/logs/geth.log',
    'network-ego/node-1/logs/geth.log',
    'network-ego/node-2/logs/geth.log',
    'network-ego/node-3/logs/geth.log',
    'network-ego/node-4/logs/geth.log'
]

geth_logs_non_ego = [
    'network 2/network/node-0/logs/geth.log',
    'network 2/network/node-1/logs/geth.log',
    'network 2/network/node-2/logs/geth.log',
    'network 2/network/node-3/logs/geth.log',
    'network 2/network/node-4/logs/geth.log'
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

    # Sort by Timestamp
    df_sorted = df.sort_values(by='Timestamp').reset_index(drop=True)

    # Identify sequence 1, 2, 3, 4, 5, 6
    sequence_indices = df_sorted[(df_sorted['ID'] == 1) &
                                 (df_sorted['ID'].shift(-1) == 2) &
                                 (df_sorted['ID'].shift(-2) == 3) &
                                 (df_sorted['ID'].shift(-3) == 4) &
                                 (df_sorted['ID'].shift(-4) == 5) &
                                 (df_sorted['ID'].shift(-5) == 6)].index

    # Filter, keep only rows with the sequence 1, 2, 3, 4, 5, 6
    df_filtered = pd.concat([df_sorted.loc[seq_idx:seq_idx+5]
                             for seq_idx in sequence_indices
                             if seq_idx + 5 in df_sorted.index])

    time_diffs = {}
    for i in range(1, 6):
        id_start = df_filtered[df_filtered['ID'] == i]['Timestamp'].reset_index(drop=True)
        id_next = df_filtered[df_filtered['ID'] == i+1]['Timestamp'].reset_index(drop=True)
        time_diff = (id_next - id_start).dt.total_seconds() * 1000  # Convert to milliseconds
        time_diffs[f'{i} to {i+1}'] = time_diff.mean()

    return time_diffs

time_diffs_ego = process_logs(geth_logs_ego)
time_diffs_non_ego = process_logs(geth_logs_non_ego)

# Define step names
step_names = {
    '1 to 2': 'Client collecting transactions',
    '2 to 3': 'Sending transactions to the server',
    '3 to 4': 'Executing transactions',
    '4 to 5': 'Sending results to the client',
    '5 to 6': 'Client updating its state'
}

steps = list(time_diffs_ego.keys())
ego_values = [time_diffs_ego[step] for step in steps]
non_ego_values = [time_diffs_non_ego[step] for step in steps]

bar_width = 0.35
index = range(len(steps))

plt.figure(figsize=(10, 6))

plt.bar(index, ego_values, bar_width, color='skyblue', label='Ego Nodes')
plt.bar([i + bar_width for i in index], non_ego_values, bar_width, color='lightgreen', label='Non-Ego Nodes')

plt.xlabel('Step')
plt.ylabel('Mean Time Difference (milliseconds)')
plt.title('Comparison of Mean Time Differences Between Steps')
plt.xticks([i + bar_width / 2 for i in index], [step_names[step] for step in steps], rotation=45, ha='right')
plt.legend()
plt.tight_layout()
plt.savefig('mean_time_differences_comparison.pdf')
plt.close()
