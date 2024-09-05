# sillywalks 🎩👞

## About 🦜

A command-line tool to mintor CPU, memory, and I/O of a process.

Here's a YouTube video that shows usage:

[![sillywalks intro](https://img.youtube.com/vi/3a7gU9Y_5f4/0.jpg)](https://www.youtube.com/watch?v=3a7gU9Y_5f4)

## Features 🧀

- Tracks CPU usage, memory consumption, and I/O
- Monitors process and its subprocesses
- Generates time-series plots

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

Or from PyPI (soon):

```bash
pip install sillywalks
```

## Usage 🥥

`sillywalks` is a command-line interface (CLI) tool. A CLI is a
text-based interface where you enter commands in a terminal or command
prompt. Run sillywalks like this:

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
resource usage. It's useful for understanding things like maximum CPU
usage.

2. Watching a video encoding process:

```bash
sillywalks ffmpeg -i input.mp4 -c:v libx264 -crf 23 output.mp4
```

This example monitors the resource usage of FFmpeg, a popular video
and audio processing tool, while it encodes a video. It's helpful for
seeing how resource-intensive this encoding process is.

3. Tracking a machine learning training job:

```bash
sillywalks python3 train_model.py --epochs 100 --batch-size 32
```

This command monitors a machine learning model training process. It
can help you understand the resource requirements of your ML jobs and
optimize them if needed.

## Output 📊🐟

sillywalks provides two types of output:

1. Real-time console updates: These appear in your terminal as the
   monitored process runs.

2. Time-series plot (`process_stats.png`): A graph showing how
   resource usage changes over time.

Here's what the time-series plot might look like:

<a href="https://github.com/dnouri/sillywalks/blob/main/assets/process_stats.png">
  <img src="https://github.com/dnouri/sillywalks/blob/main/assets/process_stats.png" alt="Example plot" style="height: 300px;"/>
</a>

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
install the respective plug-ins for your editor.  To run Black and
Ruff in your source checkout, use:

```bash
make lint
```

## References

- I [blogged about how I used an LLM to write the code for
  sillywalks](https://danielnouri.org/notes/2024/09/02/the-hottest-new-programming-language-is-english/).
  The blog post contains lessons learned and advice on how to best
  learn the skill of [prompt
  engineering](https://huggingface.co/docs/transformers/en/tasks/prompting)
  for beginners and others!

- This software uses [psutil](https://psutil.readthedocs.io/) at its
  core.  psutil is a cross-platform library for retrieving information
  on running processes and system utilization (CPU, memory, disks,
  network, sensors) in Python.

- Monty Python's [Ministry of Silly Walks on
  YouTube](https://youtu.be/iV2ViNJFZC8)

## Contributing 🐮

Contributions are welcome! Feel free to submit issues or pull requests
on our GitHub repository. Whether you're fixing bugs, adding features,
or improving documentation, your help is appreciated.
