import pandas as pd
import matplotlib.pyplot as plt
import re

# Path to your log file
log_server = 'network/node-0/logs/geth.log'
log_client = 'network/node-1/logs/geth.log'

geth_logs = ['network/node-0/logs/geth.log',
             'network/node-1/logs/geth.log',
             'network/node-2/logs/geth.log',
             'network/node-3/logs/geth.log']

# Initialize lists to store the parsed data
ids = []
timestamps = []
block_ids = []

# Regular expression pattern to match the lines with "INFO Test time"
pattern = re.compile(r'INFO.*Test time\s+ID=(\d+).*timestamp=(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{9})')

# Read the log file and extract the relevant lines
for log_file in geth_logs:
    with open(log_file, 'r') as file:
        for line in file:
            match = pattern.search(line)
            if match:
                ids.append(int(match.group(1)))
                timestamps.append(match.group(2))
                # Extract Block ID if available; else set to None
                block_id_match = re.search(r'"Block id"=(<nil>|0x[0-9a-fA-F]+)', line)
                block_ids.append(block_id_match.group(1) if block_id_match else None)

# Create a DataFrame from the extracted data
df = pd.DataFrame({
    'ID': ids,
    'Timestamp': pd.to_datetime(timestamps),
    'Block ID': block_ids
})
# Sort the DataFrame by the Timestamp column
df_sorted = df.sort_values(by='Timestamp')
print(df_sorted)

# Identify the indices where ID is 1 and the next row has ID 6
drop_indices = df_sorted[(df_sorted['ID'] == 1) & (df_sorted['ID'].shift(-1) == 6)].index
drop_indices_next = drop_indices + 1  # Include the next row as well
# Combine the indices and drop the rows
df_sorted = df_sorted.drop(drop_indices.union(drop_indices_next))
# Display the resulting DataFrame
print(df_sorted)
# Filter rows with ID 1 and 6
id_1 = df_sorted[df_sorted['ID'] == 1].reset_index(drop=True)
id_6 = df_sorted[df_sorted['ID'] == 6].reset_index(drop=True)
# Ensure both DataFrames have the same length by trimming excess elements if necessary
min_length = min(len(id_1), len(id_6))
id_1 = id_1.iloc[:min_length]
id_6 = id_6.iloc[:min_length]
# Compute the time differences
time_diffs = id_6['Timestamp'] - id_1['Timestamp']
# Convert time differences to milliseconds for easier interpretation
time_diffs_milliseconds = time_diffs.dt.total_seconds() * 1000
plt.figure(figsize=(8, 6))
plt.boxplot(time_diffs_milliseconds, patch_artist=True, showfliers=False)
plt.title('Distribution of Time to build a block with generateWork()')
plt.ylabel('Time Difference (milliseconds)')
# Save the plot as a PNG file
plt.savefig('time_differences_boxplot.png')
# Optional: Close the plot to free up memory if running multiple plots
plt.close()