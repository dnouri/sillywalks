import sys
from io import StringIO
from unittest.mock import Mock, patch, call

import pytest

from silly import (
    ProcessStats,
    ConsoleOutput,
    PrometheusOutput,
    MultiOutput,
    get_process_stats,
    monitor_process,
    get_output_strategy,
)


class MockPrometheusClient:
    def __init__(self):
        self.Gauge = Mock()
        self.start_http_server = Mock()


def test_process_stats():
    stats = ProcessStats(memory=100.0, cpu_percent=50.0, io_read=10.0, io_write=5.0)
    assert stats.memory == 100.0
    assert stats.cpu_percent == 50.0
    assert stats.io_read == 10.0
    assert stats.io_write == 5.0


def test_console_output():
    console_output = ConsoleOutput()
    stats = ProcessStats(memory=100.0, cpu_percent=50.0, io_read=10.0, io_write=5.0)

    captured_output = StringIO()
    sys.stdout = captured_output

    console_output.output(stats)

    sys.stdout = sys.__stdout__  # Reset redirect.

    assert "Memory: 100.00MB | CPU: 50.00%" in captured_output.getvalue()
    assert "I/O Read: 10.00MB | I/O Write: 5.00MB" in captured_output.getvalue()


def test_prometheus_output():
    mock_client = MockPrometheusClient()
    mock_client.Gauge.side_effect = [Mock(), Mock(), Mock(), Mock()]
    prometheus_output = PrometheusOutput(8000, mock_client)
    assert prometheus_output.port == 8000

    # Check that Gauges were created
    assert mock_client.Gauge.call_count == 4

    stats = ProcessStats(memory=100.0, cpu_percent=50.0, io_read=10.0, io_write=5.0)
    prometheus_output.output(stats)

    # Check that set was called on each Gauge
    for gauge in [
        prometheus_output.memory_gauge,
        prometheus_output.cpu_gauge,
        prometheus_output.io_read_gauge,
        prometheus_output.io_write_gauge,
    ]:
        gauge.set.assert_called_once()


def test_multi_output():
    mock_strategy1 = Mock()
    mock_strategy2 = Mock()
    multi_output = MultiOutput([mock_strategy1, mock_strategy2])

    stats = ProcessStats(memory=100.0, cpu_percent=50.0, io_read=10.0, io_write=5.0)
    multi_output.output(stats)

    mock_strategy1.output.assert_called_with(stats)
    mock_strategy2.output.assert_called_with(stats)

    multi_output.cleanup()
    mock_strategy1.cleanup.assert_called_once()
    mock_strategy2.cleanup.assert_called_once()


@patch('silly.psutil.Process')
def test_get_process_stats(mock_process):
    mock_process.return_value.memory_full_info.return_value.uss = 1024 * 1024  # 1 MB
    mock_process.return_value.cpu_times.return_value = (1.0, 0.5)
    mock_process.return_value.io_counters.return_value = (
        1024 * 1024,
        512 * 1024,
    )  # 1 MB read, 0.5 MB write
    mock_process.return_value.children.return_value = []

    stats = get_process_stats(12345)
    assert stats is not None
    assert stats[0] == 1.0  # 1 MB memory
    assert stats[1] == (1.0, 0.5)  # CPU times
    assert stats[2] == (1024 * 1024, 512 * 1024)  # IO counters


@pytest.mark.parametrize(
    "use_console,use_prometheus,expected_strategies",
    [
        (True, False, 1),
        (False, True, 1),
        (True, True, 2),
    ],
)
def test_get_output_strategy(use_console, use_prometheus, expected_strategies):
    with patch(
        'silly.create_prometheus_output',
        return_value=Mock(spec=PrometheusOutput) if use_prometheus else None,
    ):
        with get_output_strategy(use_console, use_prometheus, 8000) as strategy:
            assert isinstance(strategy, MultiOutput)
            assert len(strategy.strategies) == expected_strategies


def test_monitor_process():
    mock_strategy = Mock()
    mock_popen = Mock()
    mock_process = Mock()
    mock_process.poll.side_effect = [None, None, 0]  # Run twice, then exit
    mock_popen.return_value = mock_process

    mock_time = Mock(side_effect=[0, 1, 2])  # Simulate time passing
    mock_sleep = Mock()

    mock_get_stats = Mock(
        side_effect=[
            (100.0, (1.0, 0.5), (1024 * 1024, 512 * 1024)),
            (120.0, (1.5, 0.7), (1536 * 1024, 768 * 1024)),
            None,  # Simulate process ending
        ]
    )

    with patch('silly.get_process_stats', mock_get_stats):
        monitor_process(
            ['test_command'],
            mock_strategy,
            popen_func=mock_popen,
            time_func=mock_time,
            sleep_func=mock_sleep,
        )

    assert mock_strategy.output.call_count == 2  # Called twice before process "exits"
    mock_popen.assert_called_with(['test_command'])

    expected_calls = [
        call(
            ProcessStats(
                memory=pytest.approx(100.0),
                cpu_percent=pytest.approx(0.0),
                io_read=pytest.approx(1.0),
                io_write=pytest.approx(0.5),
            )
        ),
        call(
            ProcessStats(
                memory=pytest.approx(120.0),
                cpu_percent=pytest.approx(70.0),
                io_read=pytest.approx(1.5),
                io_write=pytest.approx(0.75),
            )
        ),
    ]
    mock_strategy.output.assert_has_calls(expected_calls, any_order=False)


if __name__ == '__main__':
    pytest.main()
