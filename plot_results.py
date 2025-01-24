import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import argparse

def convert_time(seconds, unit='hours'):
    conversions = {
        'hours': 3600,
        'minutes': 60,
        'seconds': 1
    }
    return seconds / conversions[unit]

def parse_battery_log(csv_path, use_elapsed_time=False, time_unit='hours'):

    df = pd.read_csv(csv_path, parse_dates=['Timestamp'])
    
    status_map = {
        0: 'Unknown', 1: 'Discharging', 
        2: 'AC Attached', 3: 'Charging', 
        4: 'Charged'
    }
    df['StatusText'] = df['Status'].map(status_map)
    
    if use_elapsed_time:
        seconds_elapsed = (df['Timestamp'] - df['Timestamp'].min()).dt.total_seconds()
        df['TimeElapsed'] = convert_time(seconds_elapsed, time_unit)
        time_column = 'TimeElapsed'
        x_label = f'Time Elapsed ({time_unit.capitalize()})'
    else:
        df['TimeStamp'] = df['Timestamp']
        time_column = 'TimeStamp'
        x_label = 'Timestamp'
    
    plt.figure(figsize=(12, 6))
    
    plt.subplot(2, 1, 1)
    plt.plot(df[time_column], df['Percentage'], marker='o')
    plt.title('Battery Charge Level')
    plt.ylabel('Charge Percentage')
    plt.xlabel(x_label)
    plt.grid(True)
    
    plt.subplot(2, 1, 2)
    plt.plot(df[time_column], df['Status'], marker='o', linestyle='-')
    plt.yticks(list(status_map.keys()), list(status_map.values()), rotation=45)
    plt.title('Battery Status Over Time')
    plt.ylabel('Status')
    plt.xlabel(x_label)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot battery log data')
    parser.add_argument('file', help='Path to the battery log CSV file')
    parser.add_argument('-e', '--elapsed', action='store_true', 
                       help='Use elapsed time instead of timestamps')
    parser.add_argument('-u', '--unit', choices=['hours', 'minutes', 'seconds'], 
                      default='hours', help='Time unit for elapsed time')
    
    args = parser.parse_args()
    parse_battery_log(args.file, use_elapsed_time=args.elapsed, time_unit=args.unit)