# ER IPT HACK 2023. Track 2: Calculations

Solution of the YAV-SSV team. Were the only team that reached the final.

The research is centered around measuring power consumption at different CPU frequencies and in different environments (local laptop, Cloud VM)

See [`TASK.md`](./TASK.md) for task details, and [`report/presentation.pdf`](report/presentation.pdf) for a detailed overview of the given problem.

Details of the results and their analysis can be found in the [`report`](./report) folder.

## [Installation](./installation)
Various auxiliary shell scripts are used to set up the work environment.
Notice that it is not complete, you may need to additionally install at least `python3` and `docker` if your system does not have them.

Should be run from the root of the project, as further scripts expect to have some files (at least python env) to be present here.

## [Templates](./templates/) & [Experiments](./experiments/)
Source code for the experiments run and their raw results.

Experiments can be grouped into two categories: local runs with different CPU frequencies and run on Azure.

Used tools: perf, powertop, hepscore benchmark with different workloads, docker

See subfolders for more details

### Usage:
```
sudo experiments/experiment1/run_benchmarking_fort.sh
```
with no additional agruments

## [Analysis](./analysis)
Script to process experiment logs and build plots

### Usage
```
python analysis/visualize.py analysis/config.yaml --show
```
To interactively display plots

Or

```
python analysis/visualize.py analysis/config.yaml --out_dir report
```
To save plots and tables for the report

### Adding data
Paths to experiments and their metadata should be written in [`analysis/config.yaml`](./analysis/config.yaml)

## [Report](./report)
Resulting tables, graphs, and their analysis.
