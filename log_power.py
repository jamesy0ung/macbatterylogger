import subprocess
import csv
import re
import datetime
import time
import argparse

def get_battery_info():
    """Executes pmset -g batt and returns parsed battery info."""
    try:
        process = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True, check=True)
        output = process.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing pmset: {e}")
        return None

    lines = output.strip().split('\n')
    battery_line = None
    for line in lines:
        if "InternalBattery" in line:
            battery_line = line
            break
    if not battery_line:
        return None

    match = re.search(r'(\d+)%; (charging|charged|discharging|AC attached);', battery_line)
    if not match:
        return None

    percentage = int(match.group(1))
    status_text = match.group(2)

    if status_text == "charging":
        status_code = 3
    elif status_text == "AC attached":
        status_code = 2
    elif status_text == "discharging":
        status_code = 1
    elif status_text == "charged":
        status_code = 4
    else:
        status_code = 0 # Unknown

    return percentage, status_code


def log_to_csv(csv_file, percentage, status):
    """Appends battery info to the CSV file."""
    timestamp = datetime.datetime.now().isoformat()
    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, percentage, status])

def main():
    parser = argparse.ArgumentParser(
        description='Log macOS battery status to CSV file'
    )
    parser.add_argument(
        '-f', '--file',
        metavar='FILE',
        default=None,
        help='Path to output CSV file (default: battery_log_TIMESTAMP.csv)'
    )
    parser.add_argument(
        '-i', '--interval',
        type=int,
        default=60,
        metavar='SECONDS',
        help='Logging interval in seconds (default: 60)'
    )

    args = parser.parse_args()
    
    # Generate default filename with timestamp if none provided
    if args.file is None:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = f"battery_log_{timestamp}.csv"
    else:
        csv_file = args.file

    # Create header if the file doesn't exist
    try:
        with open(csv_file, 'x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Percentage", "Status"])
    except FileExistsError:
        pass

    print(f"Logging to: {csv_file}")
    print(f"Interval: {args.interval} seconds")
    print("Press Ctrl+C to stop logging")

    try:
        while True:
            battery_info = get_battery_info()
            if battery_info:
                percentage, status = battery_info
                log_to_csv(csv_file, percentage, status)
                print(f"Logged: {datetime.datetime.now().isoformat()}, Percentage: {percentage}%, Status: {status}")
            else:
                print("Could not get battery information")

            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nLogging stopped")

if __name__ == "__main__":
    main()