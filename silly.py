import sys
import time
import psutil
import matplotlib.pyplot as plt
from subprocess import Popen


def get_process_stats(pid):
    try:
        process = psutil.Process(pid)
        with process.oneshot():
            memory = process.memory_full_info().uss / 1024 / 1024  # MB
            cpu_times = process.cpu_times()
            io_counters = process.io_counters()

        children = process.children(recursive=True)
        for child in children:
            with child.oneshot():
                memory += child.memory_full_info().uss / 1024 / 1024
                cpu_times = [sum(x) for x in zip(cpu_times, child.cpu_times())]
                io_counters = [sum(x) for x in zip(io_counters, child.io_counters())]

        return memory, cpu_times, io_counters
    except psutil.NoSuchProcess:
        return None


def monitor_process(command):
    process = Popen(command)
    pid = process.pid

    start_time = time.time()
    last_cpu_times = None
    stats = {'time': [], 'memory': [], 'cpu': [], 'io_read': [], 'io_write': []}

    try:
        while process.poll() is None:
            current_time = time.time() - start_time
            process_stats = get_process_stats(pid)

            if process_stats is None:
                break

            memory, cpu_times, io_counters = process_stats

            if last_cpu_times is not None:
                cpu_percent = sum(cpu_times) - sum(last_cpu_times)
                cpu_percent /= current_time - stats['time'][-1]
                cpu_percent *= 100
            else:
                cpu_percent = 0

            last_cpu_times = cpu_times

            stats['time'].append(current_time)
            stats['memory'].append(memory)
            stats['cpu'].append(cpu_percent)
            stats['io_read'].append(io_counters[0] / 1024 / 1024)  # MB
            stats['io_write'].append(io_counters[1] / 1024 / 1024)  # MB

            print(
                f"\rTime: {current_time:.2f}s | Memory: {memory:.2f}MB | CPU: {cpu_percent:.2f}% | I/O Read: {stats['io_read'][-1]:.2f}MB | I/O Write: {stats['io_write'][-1]:.2f}MB",
                end='',
            )

            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        print("\nData collection finished. Generating plots...")
        generate_plots(stats)


def generate_plots(stats):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))

    ax1.plot(stats['time'], stats['memory'])
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Memory Usage (MB)')
    ax1.set_title('Memory Usage Over Time')

    ax2.plot(stats['time'], stats['cpu'])
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('CPU Usage (%)')
    ax2.set_title('CPU Usage Over Time')

    ax3.plot(stats['time'], stats['io_read'], label='Read')
    ax3.plot(stats['time'], stats['io_write'], label='Write')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('I/O (MB)')
    ax3.set_title('I/O Over Time')
    ax3.legend()

    plt.tight_layout()
    plt.savefig('process_stats.png')
    print("Plots saved as process_stats.png")


def main(argv=sys.argv):
    if len(argv) < 2:
        print("Usage: sillywalks <command>")
        sys.exit(1)

    monitor_process(argv[1:])
