#!/usr/bin/env python3

'''
OPS445 Assignment 2
Program: assignment2.py 
Author: "Arnie Lloyd Sarmiento"
Semester: "Fall 2024"

Description: This script monitors memory usage of processes running on a Linux system. It retrieves and displays the memory usage statistics, including total memory, available memory, and process-specific memory usage. The script allows users to visualize memory consumption in a graphical format, either in kilobytes or human-readable units.

'''

import os
import argparse

def parse_command_args():
    parser = argparse.ArgumentParser(description="Memory Visualizer")
    parser.add_argument('-H', '--human-readable', action='store_true', help='Display sizes in human-readable format.')
    parser.add_argument('-l', '--length', type=int, default=20, help='Specify the graph length (default is 20).')
    parser.add_argument('program', nargs='?', type=str, help='Program name to display memory usage for its processes.')
    return parser.parse_args()
    # Parses the command line arguments. If a program name is provided, the script will display memory usage for its processes.
    # If no program is provided, the script will display system-wide memory usage.

def pids_of_prog(program):
    try:
        return os.popen(f'pidof {program}').read().strip().split()
    except Exception:
        return []
    # Retrieves the list of PIDs for a given program using the 'pidof' command.

def rss_mem_of_pid(pid):
    """Calculates RSS memory usage of a given PID from /proc/[pid]/smaps."""
    rss = 0
    try:
        with open(f'/proc/{pid}/smaps', 'r') as smaps_file:
            for line in smaps_file:
                if line.startswith('Rss:'):
                    rss += int(line.split()[1])  # Add the RSS value (in KB)
    except FileNotFoundError:
        print(f"ERROR: PID {pid} does not exist or /proc/{pid}/smaps is inaccessible.")
    except Exception as e:
        print(f"Unexpected error while reading /proc/{pid}/smaps: {e}")
    return rss
    # Reads the memory usage of a given PID from its /proc/[pid]/smaps file and returns the RSS value in kilobytes (KB).

def human_readable_format(size_kb):
    units = ['KiB', 'MiB', 'GiB', 'TiB']
    size = float(size_kb)
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TiB"
    # Converts memory size in kilobytes (KB) to a human-readable format (e.g., MiB, GiB).

def percent_to_graph(percent, length):
    filled = int(round(percent * length))
    return '#' * filled + ' ' * (length - filled)
    # Converts a percentage value to a text-based bar graph with the specified length.

def get_sys_mem():
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemTotal:'):
                    return int(line.split()[1])
    except Exception:
        return 0
    # Retrieves the total system memory (MemTotal) from /proc/meminfo.

def get_avail_mem():
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemAvailable:'):
                    return int(line.split()[1])
    except Exception:
        return 0
    # Retrieves the available memory (MemAvailable) from /proc/meminfo.

def display_process_memory(program, pids, human_readable, graph_length):
    print(f"Memory usage for program '{program}':")
    total_mem = get_sys_mem()
    total_rss = 0

    for pid in pids:
        rss = rss_mem_of_pid(pid)
        total_rss += rss
        graph = percent_to_graph(rss / total_mem, graph_length)
        print(f"PID {pid}: {rss} KB {human_readable_format(rss) if human_readable else ''} | {graph}")

    print(f"Total: {total_rss} KB {human_readable_format(total_rss) if human_readable else ''}")
    # Displays memory usage for all processes of the specified program, with graphical representation.

def display_system_memory(human_readable, graph_length):
    total_mem = get_sys_mem()
    avail_mem = get_avail_mem()
    used_mem = total_mem - avail_mem

    print(f"Total Memory: {total_mem} KB")
    print(f"Available Memory: {avail_mem} KB")
    if human_readable:
        print(f"Total Memory: {human_readable_format(total_mem)}")
        print(f"Available Memory: {human_readable_format(avail_mem)}")

    graph = percent_to_graph(used_mem / total_mem, graph_length)
    print(f"Used Memory: {used_mem} KB | {graph}")
    # Displays the total, available, and used system memory with graphical representation.

def main():
    args = parse_command_args()
    if args.program:
        pids = pids_of_prog(args.program)
        if not pids:
            print(f"No running processes found for program: {args.program}")
        else:
            display_process_memory(args.program, pids, args.human_readable, args.length)
    else:
        display_system_memory(args.human_readable, args.length)
    # Main function to handle command-line arguments and display either program-specific or system-wide memory usage.

if __name__ == '__main__':
    main()
    # Run the main function if the script is executed directly.

