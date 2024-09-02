# sillywalks 🎩👞

## About 🦜

A whimsical resource monitor that prances through your processes,
tracking CPU, memory, and I/O with a spring in its step!

## Features 🧀

- Tracks CPU usage, memory consumption, and I/O operations
- Monitors main process and its subprocesses
- Provides real-time console updates
- Generates time-series plots
- Outputs summary statistics

## Installation 🛋️

To install project requirements, it's first recommended to create a
virtualenv:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -U pip wheel
```

Install sillywalks from source:

```bash
pip install -e ".[devel]"
```

Or from PyPI:

```bash
pip install sillywalks
```

Note: `pip` is a package installer for Python. The `-e` flag installs
the package in 'editable' mode, which is useful for developers.

## Usage 🥥

sillywalks is a command-line interface (CLI) tool. A CLI is a
text-based interface where you enter commands in a terminal or command
prompt. Run sillywalks with:

```bash
sillywalks <command> [args...]
```

Replace `<command>` with the program you want to monitor, and
`[args...]` with any arguments for that program.

### Examples

1. Monitoring a Python script:

```bash
sillywalks python3 my_script.py
```

This command will run `my_script.py` using Python 3 and monitor its
resource usage. It's useful for understanding how your Python scripts
perform and use system resources.

2. Watching a video encoding process:

```bash
sillywalks ffmpeg -i input.mp4 -c:v libx264 -crf 23 output.mp4
```

This example monitors the resource usage of FFmpeg, a popular video
and audio processing tool, while it encodes a video. It's helpful for
seeing how resource-intensive video encoding can be.

3. Tracking a machine learning training job:

```bash
sillywalks python3 train_model.py --epochs 100 --batch-size 32
```

This command monitors a machine learning model training process. It
can help you understand the resource requirements of your ML jobs and
optimize them if needed.

Here's what an output plot might look like:

[![process_stats.png](https://github.com/dnouri/sillywalks/blob/add-plot-example-to-readme/assets/process_stats.png?sanitize=true&width=100)](https://github.com/dnouri/sillywalks/blob/main/assets/process_stats.png)

## Output 📊🐟

sillywalks provides three types of output:

1. Real-time console updates: These appear in your terminal as the
   monitored process runs.

2. Time-series plot (`sillywalks_stats.png`): A graph showing how
   resource usage changes over time.

3. Summary statistics table: A final report of the overall resource
   usage.

## Limitations 🦸‍♂️

- Subprocess tracking accuracy may vary depending on the system and
  the processes being monitored.

- Currently offers limited customization options for monitoring and
  reporting.

- May need optimization for very long-running processes to manage data
  collection and storage efficiently.

## Profiling vs. Monitoring 🕵️‍♂️🧠

While sillywalks is great for overall resource monitoring, sometimes
you need more detailed code-level insights. In such cases, consider
using a profiler:

- Use sillywalks for: High-level resource tracking of CPU, memory, and
I/O.

- Use a profiler for: Identifying code bottlenecks, memory leaks, or
creating call graphs.

For Python, [py-spy](https://github.com/benfred/py-spy) is a popular
sampling profiler that can attach to running processes with low
overhead. It provides detailed performance insights without modifying
your code.

Example:

```bash
py-spy record -o profile.svg --pid 12345
```

Choose sillywalks for general resource monitoring, and switch to a
profiler like py-spy when you need to optimize at the code level.

## 🧹 Linting

We use Ruff and Black to lint and prettify the code.  You may want to
install the respective plug-ins for your editor.

To run Black and SQLFluff locally, use:

```bash
make lint
```

## Contributing 🐮

Contributions are welcome! Feel free to submit issues or pull requests
on our GitHub repository. Whether you're fixing bugs, adding features,
or improving documentation, your help is appreciated.

## License ⚖️

This project is under the MIT License. See the LICENSE file for
details. The MIT License is a permissive open-source license that
allows for reuse with few restrictions.
