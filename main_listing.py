import time
import os
import psutil

from apps.namaz_timing.app import App

def main():
    # Start the timer
    start_time = time.time()

    # Get the process ID (PID) of the current Python process
    pid = os.getpid()
    python_process = psutil.Process(pid)

    # Measure memory before execution
    memory_usage_before = python_process.memory_info().rss / (1024 * 1024)

    # execute code
    app = App()
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
    main()