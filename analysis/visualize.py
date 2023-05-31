import argparse
import glob
import os
import re
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import yaml

# plt.rcParams["figure.figsize"] = (13, 7)
# plt.rcParams["legend.fontsize"] = 14
# plt.rcParams["axes.titlesize"] = 14
sns.set_style("whitegrid")


def read_file(file):
    with open(file) as f:
        text = f.read()
    text = text.replace("\u202f", "")
    return text


def read_logs_perf(directory):
    results = []
    for file in glob.glob(os.path.join(directory, "*.log")):
        text = read_file(file)

        freq = float(file.split("/")[-1].split("_")[0])

        score = float(re.search(r"Final result: ([\d.]+)", text).group(1))
        joules = float(re.search(r"([\d,]+) Joules power", text).group(1).replace(",", "."))
        elapsed = float(re.search(r"([\d,]+) seconds time elapsed", text).group(1).replace(",", "."))

        battery = re.findall(r"energy: +([\d,]+) Wh", text) or None

        if battery:
            before, after = battery
            before = float(before.replace(",", "."))
            after = float(after.replace(",", "."))
            battery = (before - after) * 3600

        record = {
            "CPU frequency, GHz": freq,
            "Power Consumption, Joules": joules,
            "Benchmark Score": score,
            "Time Elapsed, s": elapsed,
            "Battery Consumption, Joules": battery,
        }
        print(file, record)

        results.append(record)
    return results


def read_logs_powertop(directory):
    results = []
    benchmark_files = glob.glob(os.path.join(directory, "*.log"))
    benchmark_files = sorted(benchmark_files, key=lambda x: int(os.path.basename(x).split("_")[0]))
    powertop_files = glob.glob(os.path.join(directory, "*.txt"))
    powertop_files = sorted(powertop_files, key=lambda x: int(os.path.basename(x).split("_")[0]))
    for file_bmk, file_power in zip(benchmark_files, powertop_files):
        text_bmk = read_file(file_bmk)
        text_powertop = read_file(file_power)

        score = float(re.search(r"Final result: ([\d.]+)", text_bmk).group(1))

        time_string = re.search(r"real\t([\d\.ms]+)\n", text_bmk).group(1)
        duration = datetime.strptime(time_string, "%Mm%S.%fs")
        elapsed = duration.minute * 60 + duration.second + duration.microsecond / 1000000

        try:
            joules = float(
                re.search(
                    r"The system baseline power is estimated at: +([\d\.]+) +W",
                    text_powertop,
                ).group(1)
            )
        except AttributeError:
            joules = (
                float(
                    re.search(
                        r"The system baseline power is estimated at: +([\d\.]+) +m W",
                        text_powertop,
                    ).group(1)
                )
                / 1000
            )

        record = {
            # "freq": freq,
            "Power Consumption, Joules": joules * elapsed,
            "Benchmark Score": score,
            "Time Elapsed, s": elapsed,
        }
        print(file_bmk, record)

        results.append(record)
    return results


LOGPARSERS = {"perf_freq": read_logs_perf, "powertop": read_logs_powertop}


def load_data(config):
    results = []
    for i, experiment in enumerate(config):
        parser = LOGPARSERS[experiment["logparser"]]
        records = parser(experiment["path"])
        exp_res = pd.DataFrame(records)
        for k, v in experiment["meta"].items():
            exp_res[k] = v
        exp_res["experiment_id"] = i
        results.append(exp_res)
    return pd.concat(results)


def draw_relplot(data, x, y, hue):
    sns.set_theme(style="whitegrid")
    sns.relplot(
        x=x,
        y=y,
        hue=hue,
        kind="line",
        markers=True,
        dashes=True,
        style=hue,
        aspect=1.5,
        data=data,
    )
    sns.scatterplot(data=data, x=x, y=y, hue=hue, legend=False, ax=plt.gca())


def draw_barplot(data, x, y, hue, logscale=False):
    plt.figure()
    sns.barplot(
        data=data,
        x=x,
        y=y,
        hue=hue,
        errorbar="sd",
    )
    if logscale:
        plt.yscale("log")


def plot_everything(df, show=True, out_dir="test"):
    if out_dir:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        # Create subdirectories if they don't exist
        figures_dir = os.path.join(out_dir, "figures")
        tables_dir = os.path.join(out_dir, "tables")

        for subdir in [figures_dir, tables_dir]:
            if not os.path.exists(subdir):
                os.makedirs(subdir)

    df["Score per Joule"] = df["Benchmark Score"] / df["Power Consumption, Joules"]
    df["experiment"] = (df["machine"] + "-" + df["CPU frequency, GHz"].fillna("").astype("str")).str.strip("-")

    # Save tables
    if out_dir:
        df.to_csv(os.path.join(tables_dir, "records.csv"), index=False)

        agg_cols = ["machine", "workload", "CPU frequency, GHz", "experiment"]
        gb = df.groupby(agg_cols, dropna=False)
        agg_df = gb.agg({k: ["median", "max", "min"] for k in df.columns if k not in agg_cols})
        agg_df["Runs"] = gb.size()
        agg_df = agg_df.reset_index()
        agg_df.columns = [f"{col[1].title()} {col[0]}" for col in agg_df.columns.values]
        agg_df.to_csv(os.path.join(tables_dir, "aggregated.csv"), index=False)

    # Draw plots
    plots_args = [
        (
            draw_relplot,
            (df[df["machine"] == "local"], "CPU frequency, GHz", "Benchmark Score", "workload"),
            "freq-score",
        ),
        (
            draw_relplot,
            (df[df["machine"] == "local"], "CPU frequency, GHz", "Power Consumption, Joules", "workload"),
            "freq-joul",
        ),
        (
            draw_relplot,
            (df[df["machine"] == "local"], "CPU frequency, GHz", "Time Elapsed, s", "workload"),
            "freq-time",
        ),
        (
            draw_relplot,
            (df[df["machine"] == "local"], "CPU frequency, GHz", "Score per Joule", "workload"),
            "freq-score-per-joul",
        ),
        (
            draw_relplot,
            (df[~df["Battery Consumption, Joules"].isna()], "CPU frequency, GHz", "Battery Consumption, Joules", "workload"),
            "freq-battery",
        ),
        (
            draw_barplot,
            (df, "workload", "Power Consumption, Joules", "experiment"),
            "experiment-joul",
        ),
        (
            draw_barplot,
            (df, "workload", "Benchmark Score", "experiment"),
            "experiment-score",
        ),
        (
            draw_barplot,
            (df, "workload", "Score per Joule", "experiment", True),
            "experiment-score-per-joule",
        ),
    ]

    for plot_func, args, name in plots_args:
        plot_func(*args)
        if show:
            plt.show(block=False)
        if out_dir:
            plt.savefig(os.path.join(figures_dir, f"{name}.svg"), pad_inches=0.2)
    if show:
        plt.show(block=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process directories")
    parser.add_argument("config", help="Path to the input directory")
    parser.add_argument("--show", action="store_true", help="Show plots")
    parser.add_argument("--out_dir", default=None, help="Show plots")

    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    data = load_data(config)
    print(data)
    plot_everything(data, show=args.show, out_dir=args.out_dir)
