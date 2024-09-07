"""Process Monitor with Resource Usage Plotting

This module provides functionality to monitor a process's resource usage
and generate a plot of the collected data. It supports console output,
Prometheus metrics, and saves a plot of resource usage over time.
"""

import argparse
import threading
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from subprocess import Popen
from typing import List, Tuple, Callable, Optional
import os
from datetime import datetime

import psutil
import matplotlib.pyplot as plt


@dataclass
class ProcessStats:
    memory: float
    cpu_percent: float
    io_read: float
    io_write: float


class OutputStrategy(ABC):
    @abstractmethod
    def output(self, stats: ProcessStats):
        pass

    @abstractmethod
    def cleanup(self):
        pass


class ConsoleOutput(OutputStrategy):
    def output(self, stats: ProcessStats):
        print(
            f"\rMemory: {stats.memory:.2f}MB | CPU: {stats.cpu_percent:.2f}% | "
            f"I/O Read: {stats.io_read:.2f}MB | I/O Write: {stats.io_write:.2f}MB",
            end="",
            flush=True,
        )

    def cleanup(self):
        print("\nMonitoring finished.")


class PrometheusOutput(OutputStrategy):
    """Strategy for Prometheus metrics output.

    Initializes Prometheus metrics and starts a server on the specified port.
    """

    def __init__(self, port: int, prometheus_client):
        self.port = port
        self.prometheus_client = prometheus_client
        self.memory_gauge = self.prometheus_client.Gauge(
            'process_memory_usage_mb', 'Memory usage of the process in MB'
        )
        self.cpu_gauge = self.prometheus_client.Gauge(
            'process_cpu_usage_percent', 'CPU usage of the process in percent'
        )
        self.io_read_gauge = self.prometheus_client.Gauge(
            'process_io_read_mb', 'I/O read of the process in MB'
        )
        self.io_write_gauge = self.prometheus_client.Gauge(
            'process_io_write_mb', 'I/O write of the process in MB'
        )
        self.server_thread = threading.Thread(target=self._start_server)
        self.server_thread.start()
        print(f"Prometheus server running on port {self.port}")

    def _start_server(self):
        self.prometheus_client.start_http_server(self.port)

    def output(self, stats: ProcessStats):
        self.memory_gauge.set(stats.memory)
        self.cpu_gauge.set(stats.cpu_percent)
        self.io_read_gauge.set(stats.io_read)
        self.io_write_gauge.set(stats.io_write)

    def cleanup(self):
        print("\nPrometheus server shutting down...")


def create_prometheus_output(port: int) -> Optional[PrometheusOutput]:
    """Create a PrometheusOutput instance if the prometheus_client is installed."""
    try:
        import prometheus_client

        return PrometheusOutput(port, prometheus_client)
    except ImportError:
        print("prometheus_client not installed. Prometheus support will be disabled.")
        return None


class MultiOutput(OutputStrategy):
    """Strategy for multiple output methods.

    Allows combination of multiple output strategies.
    """

    def __init__(self, strategies: List[OutputStrategy]):
        self.strategies = strategies

    def output(self, stats: ProcessStats):
        for strategy in self.strategies:
            strategy.output(stats)

    def cleanup(self):
        for strategy in self.strategies:
            strategy.cleanup()


@contextmanager
def get_output_strategy(use_console: bool, use_prometheus: bool, prometheus_port: int):
    """Context manager to create and manage output strategies."""
    strategies = []
    if use_console:
        strategies.append(ConsoleOutput())
    if use_prometheus:
        prometheus_output = create_prometheus_output(prometheus_port)
        if prometheus_output:
            strategies.append(prometheus_output)

    strategy = MultiOutput(strategies)
    try:
        yield strategy
    finally:
        strategy.cleanup()


def get_process_stats(
    pid: int,
) -> Optional[Tuple[float, Tuple[float, float], Tuple[int, int]]]:
    """Get process statistics for a given process ID.

    Returns memory usage, CPU times, and I/O counters.
    """
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
                cpu_times = tuple(sum(x) for x in zip(cpu_times, child.cpu_times()))
                io_counters = tuple(
                    sum(x) for x in zip(io_counters, child.io_counters())
                )

        return memory, cpu_times, io_counters
    except psutil.NoSuchProcess:
        return None


def monitor_process(
    command: List[str],
    output_strategy: OutputStrategy,
    popen_func: Callable = Popen,
    time_func: Callable = time.time,
    sleep_func: Callable = time.sleep,
    frequency: float = 10.0,
):
    """Monitor the resource usage of a process.

    Collects and outputs process statistics at specified frequency.
    """
    process = popen_func(command)
    pid = process.pid

    start_time = time_func()
    last_cpu_times = None
    last_time = start_time
    data_points = []

    try:
        while process.poll() is None:
            current_time = time_func()
            process_stats = get_process_stats(pid)

            if process_stats is None:
                break

            memory, cpu_times, io_counters = process_stats

            if last_cpu_times is not None:
                time_diff = max(
                    current_time - last_time, 1e-6
                )  # Avoid division by zero
                cpu_percent = (sum(cpu_times) - sum(last_cpu_times)) / time_diff * 100
            else:
                cpu_percent = 0

            last_cpu_times = cpu_times
            last_time = current_time

            stats = ProcessStats(
                memory=memory,
                cpu_percent=cpu_percent,
                io_read=io_counters[0] / 1024 / 1024,  # MB
                io_write=io_counters[1] / 1024 / 1024,  # MB
            )

            relative_time = current_time - start_time
            data_points.append(
                (
                    relative_time,
                    stats.memory,
                    stats.cpu_percent,
                    stats.io_read,
                    stats.io_write,
                )
            )

            output_strategy.output(stats)

            sleep_func(1.0 / frequency)
    except KeyboardInterrupt:
        pass

    return data_points


def plot_stats(
    data_points: List[Tuple[float, float, float, float, float]], output_file: str
):
    """Plot the collected process statistics and save to a file."""
    if not data_points:
        print("No data to plot.")
        return

    times = [point[0] for point in data_points]
    memories = [point[1] for point in data_points]
    cpus = [point[2] for point in data_points]
    io_reads = [point[3] for point in data_points]
    io_writes = [point[4] for point in data_points]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15), sharex=True)

    ax1.plot(times, memories, label='Memory (MB)')
    ax1.set_ylabel('Memory (MB)')
    ax1.legend()

    ax2.plot(times, cpus, label='CPU (%)')
    ax2.set_ylabel('CPU (%)')
    ax2.legend()

    ax3.plot(times, io_reads, label='I/O Read (MB)')
    ax3.plot(times, io_writes, label='I/O Write (MB)')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('I/O (MB)')
    ax3.legend()

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close(fig)

    print(f"Plot saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Monitor process resource usage")
    parser.add_argument(
        'command', nargs=argparse.REMAINDER, help="The command to run and monitor"
    )
    parser.add_argument(
        '--frequency',
        type=float,
        default=10.0,
        help="Log stats with this frequency (Hz)",
    )
    parser.add_argument(
        '--no-console', action='store_true', help="Disable console output"
    )
    parser.add_argument(
        '--prometheus', action='store_true', help="Enable Prometheus metrics"
    )
    parser.add_argument(
        '--port', type=int, default=8000, help="Port for Prometheus metrics server"
    )
    args = parser.parse_args()

    if not args.command:
        parser.error("No command specified to monitor")

    with get_output_strategy(
        not args.no_console,
        args.prometheus,
        args.port,
    ) as output_strategy:
        data_points = monitor_process(
            command=args.command,
            output_strategy=output_strategy,
            frequency=args.frequency,
        )

    if not data_points:
        print(
            "No data collected. The monitored process may have crashed or finished too quickly."
        )
        return

    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    command_name = os.path.basename(args.command[0])
    output_file = f"{command_name}-{timestamp}.png"

    try:
        plot_stats(data_points, output_file)
    except Exception as e:
        print(f"Error plotting stats: {e}")


if __name__ == "__main__":
    main()
