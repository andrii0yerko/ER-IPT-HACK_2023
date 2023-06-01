# Results


In this and the following experiments, we had not run the full benchmark because of its long execution (10 hours locally) but measured a single one at a time from the selected list of different tasks.

Each measurement consists of several (at least 3, up to 10) runs of benchmarking to validate results. Also, we ware tried to keep the environment homogeneous as possible for different measurement


## Local runs
In the first experiment, we investigated the relationship between max CPU frequency and power consumption & performance scored by benchmark.
The hypothesis was that lower frequency leads to lower energy consumption.

### Setup
- Run locally (AMD Ryzen 5 5500U, 6 cores, 12 threads)
- Used stack: `Linux`, `perf` (`power/energy-pkg`), `cpupower`, `upower`, `docker`
- The experiment workflow was the following:
    - Limit CPU upper frequency
    - run `perf` and benchmark workload (a few times)
    - save results

    Repeat for each available CPU frequency (1.4 GHz, 1.7 GHz, 2.1 GHz)

### Key observations
Here we can see a nonlinear reduction of the score with reducing the frequency. The difference between 2.1 GHz and 1.7 GHz is bigger than between 1.7 GHz and 1.4 GHz
![](https://raw.githubusercontent.com/andrii0yerko/ER-IPT-HACK_2023/main/report/figures/freq-score.svg)

Time reduction is nonlinear too. It seems to be highly correlated with the score but with a bigger variance.
![](https://raw.githubusercontent.com/andrii0yerko/ER-IPT-HACK_2023/main/report/figures/freq-time.svg)

An interesting situation is observed in the change in power consumption: limiting the CPU frequency reduces power consumption, until a certain point.
In our measurements, a 1.7GHz run had a lower power consumption than a 1.4 GHz one. In the case of the CPU that allows more flexible frequency adjusting there will be a parabola-shaped curve with a "sweet spot" - optimal frequency when the power consumption reaches minimum.  
![](https://raw.githubusercontent.com/andrii0yerko/ER-IPT-HACK_2023/main/report/figures/freq-joul.svg)

Measurements of a battery discharge were approximate because of monitoring software limitations - `upower` measures battery level only once every 30 seconds and within a low-precise scale (percents?). Because of that results cannot be very reliable, but there is a strong correlation between energy consumption measured by `perf` and the battery discharge. The ratio between them is something about 0.6-0.8
![](https://raw.githubusercontent.com/andrii0yerko/ER-IPT-HACK_2023/main/report/figures/freq-battery.svg)


Let's investigate the value which can be achieved from the each energy unit.
![](https://raw.githubusercontent.com/andrii0yerko/ER-IPT-HACK_2023/main/report/figures/score-joul.svg)

As we can see, despite the nonmonotonic reduction of energy consumption depending on the frequency, the ratio between the score and energy used to achieve it still decreases monotonically, which means there is more performance loss than energy efficiency gain.
![](https://raw.githubusercontent.com/andrii0yerko/ER-IPT-HACK_2023/main/report/figures/freq-score-per-joul.svg)


Also important to notice that these results are not dependent on specific benchmark workloads, and the tasks of different execution times show similar curves.

> Please see `tables/` subdirectory for the source measurement numbers

In conclusion, maximal frequency shows the best score-to-energy ratio, which may be the optimal solution for a production workload if the benchmark score fully represents its potential performance. In other cases, there is no silver bullet - maximal frequency tends to be the most performant one, while the middle one is more energy-saving, and decisions should be made corresponding to the company goals. Also, it may be possible to tune different computational nodes differently and achieve interesting tradeoffs between performance and its energy-efficiency.


## Comparing with Azure VM measurements

First of all, an **important disclaimer**:

On Azure, we do not have access to a physical CPU, so cannot play with its frequency or measure energy consumption with `perf`

On VMs, measurements can be taken with PowerTOP, but there are doubts about how valid it measures power consumption in this case. In some workloads it gives a difference up to 100 times with the local runs, meanwhile in others - about 3 times, which looks unrealistic. At the same time, the powertop cannot estimate energy consumption locally in our machine, because it somehow depends on the OS kernel settings - that is, there is no way to verify that this method is correct. In addition, to calculate power consumption, it uses estimates of parameters obtained from previous launches (with battery power), and virtual machines already have this configuration, probably provided by Microsoft itself.
Finally, the variance of values in different runs is quite small, these are not some random errors.

### Setup
- Run on Azure (Intel(R) Xeon(R) Platinum 8171M CPU @ 2.60GHz)
- Used stack: `Linux`, `powertop`, `docker`
- The experiment workflow was the following:
    - For each of the previously used workloads
    - run `powertop` and benchmark workload (a few times)
    - save results

### Observations
The benchmark score on VM is lower, as expected - it has a less powerful CPU.
![](https://raw.githubusercontent.com/andrii0yerko/ER-IPT-HACK_2023/main/report/figures/experiment-score.svg)

The results of power measurements are strange. The difference on `atlas-gen-bmk` task is about 3 times, while for other tasks it is about 100 times, that is too big to be true, and probably

![](https://raw.githubusercontent.com/andrii0yerko/ER-IPT-HACK_2023/main/report/figures/experiment-joul.svg)



![](https://raw.githubusercontent.com/andrii0yerko/ER-IPT-HACK_2023/main/report/figures/experiment-score-per-joule.svg)

To summarize, cloud providers can be an interesting option for heavy computational tasks on big scales, because it allows to dynamically allocate and scale computational resources, and, probably, is more energy-efficient because of shared hardware components for big computation nodes, and absence of outward software, graphical environment, etc. But probably not as useful for computing organizations like WLCG, which will have more value from building data centers on their own.
