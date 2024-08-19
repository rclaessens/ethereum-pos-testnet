import requests
import time
import os
from datetime import datetime

base_url = 'http://127.0.0.1:'
ports = range(8300, 8305)

log_directory = 'bandwidth_logs'

if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# delete files before writing
for port in ports:
    log_file = f"{log_directory}/node_{port-8300}_metrics.txt"
    if os.path.exists(log_file):
        os.remove(log_file)

def fetch_metrics(port):
    metrics_url = f"{base_url}{port}/debug/metrics"
    log_file = f"{log_directory}/node_{port-8300}_metrics.txt"
    
    try:
        response = requests.get(metrics_url)
        
        if response.status_code == 200:
            data = response.json()

            # Extract metrics
            p2p_egress_count = data.get('p2p/egress.count', 'N/A')
            p2p_egress_mean = data.get('p2p/egress.mean', 'N/A')
            p2p_egress_one_minute = data.get('p2p/egress.one-minute', 'N/A')
            p2p_ingress_count = data.get('p2p/ingress.count', 'N/A')
            p2p_ingress_mean = data.get('p2p/ingress.mean', 'N/A')
            p2p_ingress_one_minute = data.get('p2p/ingress.one-minute', 'N/A')
            miner_egress_count = data.get('miner/egress.count', 'N/A')
            miner_egress_mean = data.get('miner/egress.mean', 'N/A')
            miner_egress_one_minute = data.get('miner/egress.one-minute', 'N/A')
            miner_ingress_count = data.get('miner/ingress.count', 'N/A')
            miner_ingress_mean = data.get('miner/ingress.mean', 'N/A')
            miner_ingress_one_minute = data.get('miner/ingress.one-minute', 'N/A')

            # Get the current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

            # Create a log entry as a single line
            log_entry = (
                f"{timestamp}, "
                f"p2p_egress_count={p2p_egress_count}, "
                f"p2p_egress_mean={p2p_egress_mean}, "
                f"p2p_egress_one_minute={p2p_egress_one_minute}, "
                f"p2p_ingress_count={p2p_ingress_count}, "
                f"p2p_ingress_mean={p2p_ingress_mean}, "
                f"p2p_ingress_one_minute={p2p_ingress_one_minute}, "
                f"miner_egress_count={miner_egress_count}, "
                f"miner_egress_mean={miner_egress_mean}, "
                f"miner_egress_one_minute={miner_egress_one_minute}, "
                f"miner_ingress_count={miner_ingress_count}, "
                f"miner_ingress_mean={miner_ingress_mean}, "
                f"miner_ingress_one_minute={miner_ingress_one_minute}\n"
            )

            # Append with 'a'
            with open(log_file, 'a') as f:
                f.write(log_entry)
        
        else:
            print(f"Failed to fetch metrics from port {port}. Status code: {response.status_code}")
    
    except Exception as e:
        print(f"Error fetching metrics from port {port}: {e}")

# Run the fetch every second and log the metrics for each node
while True:
    try:
        for port in ports:
            fetch_metrics(port)
        time.sleep(1)
    except Exception as e:
        print(f"Error: {e}")
        break