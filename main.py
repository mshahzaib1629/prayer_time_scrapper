import time
import os
import psutil

from apps.namaz_timing.app import App
import sys
import argparse

def main(cities: list[str]):
    # Start the timer
    start_time = time.time()

    # Get the process ID (PID) of the current Python process
    pid = os.getpid()
    python_process = psutil.Process(pid)

    # Measure memory before execution
    memory_usage_before = python_process.memory_info().rss / (1024 * 1024)

    for name in cities:
        name = name.strip()
        # execute code
        print("===============================")
        print(name)
        print("===============================")
        app = App(name)
        app.get_namaz_timings()
    
    # Stop the timer
    end_time = time.time()

    # Calculate the time taken
    execution_time = end_time - start_time
    print(f"Time taken: {execution_time:.5f} seconds")

    # Get the memory usage after the code block
    memory_usage_after = python_process.memory_info().rss / (1024 * 1024)

    # print(f"Memory usage before: {memory_usage_before:.2f} MB")
    # print(f"Memory usage after: {memory_usage_after:.2f} MB")
    print(f"Memory used: {memory_usage_after - memory_usage_before:.2f} MB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get Namaz timings for a city.')
    parser.add_argument('--city', type=str, required=True, help='Name of the city to get Namaz timings for')
    args = parser.parse_args()

    CITY_NAMES = args.city
    print("City Names: ", CITY_NAMES)
    cities = CITY_NAMES.split(",")
    main(cities)