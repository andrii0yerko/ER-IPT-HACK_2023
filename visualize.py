import argparse
import glob
import os
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["figure.figsize"] = (13, 7)
plt.rcParams["legend.fontsize"] = 14
plt.rcParams["axes.titlesize"] = 14


def read_logs(directory):
    results = []
    for file in glob.glob(os.path.join(directory, "*.log")):
        with open(file) as f:
            text = f.read()
        text = text.replace("\u202f", "")

        freq = float(file.split("/")[-1].split("_")[0])

        score = float(re.search(r"Final result: ([\d.]+)", text).group(1))
        joules = float(
            re.search(r"([\d,]+) Joules power", text).group(1).replace(",", ".")
        )
        elapsed = float(
            re.search(r"([\d,]+) seconds time elapsed", text).group(1).replace(",", ".")
        )

        battery = re.findall(r"energy: +([\d,]+) Wh", text) or None

        if battery:
            before, after = battery
            before = float(before.replace(",", "."))
            after = float(after.replace(",", "."))
            battery = (before - after) * 3600

        record = {
            "freq": freq,
            "Joules": joules,
            "result": score,
            "time": elapsed,
            "battery": battery,
        }
        print(file, record)

        results.append(record)
    return results


def load_data(read_dir):
    results = read_logs(read_dir)
    exp_res = pd.DataFrame(results)
    exp_res["score_per_joule"] = exp_res["result"] / exp_res["Joules"]
    exp_res["perf_to_battery_ratio"] = exp_res["Joules"] / exp_res["battery"]

    exp_res_agg = exp_res.groupby("freq").agg(
        {k: ["median", "max", "min", list] for k in exp_res.columns if k != "freq"}
    )
    exp_res_agg = exp_res_agg.reset_index()

    exp_res_agg.columns = [
        "_".join(col).strip("_ ") for col in exp_res_agg.columns.values
    ]
    return exp_res, exp_res_agg


def vs_freq_plot(exp_res, exp_res_agg, yax):
    plt.errorbar(
        exp_res_agg["freq"],
        exp_res_agg[f"{yax}_median"],
        yerr=np.abs(
            (
                exp_res_agg[[f"{yax}_min", f"{yax}_max"]].values
                - exp_res_agg[[f"{yax}_median"]].values
            ).T
        ),
        fmt="",
        linestyle="",
        color="tab:red",
        alpha=0.8,
        capsize=10,
        capthick=1,
        linewidth=1,
    )

    plt.scatter(exp_res["freq"], exp_res[yax], alpha=0.5, color="gray")
    plt.fill_between(
        exp_res_agg["freq"],
        exp_res_agg[f"{yax}_min"],
        exp_res_agg[f"{yax}_max"],
        color="tab:red",
        alpha=0.1,
        label="Confidence Intervals",
    )

    plt.plot(
        exp_res_agg["freq"],
        exp_res_agg[f"{yax}_median"],
        linestyle="--",
        color="tab:red",
    )


def plot_everything(exp_res, exp_res_agg, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Create subdirectories if they don't exist
    figures_dir = os.path.join(out_dir, "figures")
    tables_dir = os.path.join(out_dir, "tables")

    for subdir in [figures_dir, tables_dir]:
        if not os.path.exists(subdir):
            os.makedirs(subdir)

    exp_res_agg.drop(columns=exp_res_agg.filter(like="list").columns).set_index(
        "freq"
    ).T.to_csv(os.path.join(out_dir, "tables", "results.csv"))

    yax = "result"
    vs_freq_plot(exp_res, exp_res_agg, yax)

    plt.title("Frequency vs Score")
    plt.xlabel("Frequency, GHz")
    plt.ylabel("Score")
    plt.grid()
    plt.savefig(os.path.join(out_dir, "figures", "freq-res.pdf"), pad_inches=0.2)
    # plt.show()
    plt.clf()
    plt.cla()

    vs_freq_plot(exp_res, exp_res_agg, "Joules")

    plt.title("Frequency vs Power consumption")
    plt.xlabel("Frequency, GHz")
    plt.ylabel("Power consumption, joules")
    plt.grid()
    plt.savefig(os.path.join(out_dir, "figures", "freq-joul.pdf"), pad_inches=0.2)
    # plt.show()
    plt.clf()
    plt.cla()

    plt.scatter(
        exp_res["Joules"], exp_res["result"], marker="o", alpha=0.5, c=exp_res["freq"]
    )
    plt.scatter(
        exp_res_agg["Joules_median"],
        exp_res_agg["result_median"],
        marker="o",
        alpha=1,
        color="tab:red",
    )

    plt.title("Power consumption vs Score")
    plt.xlabel("Power consumption, joules")
    plt.ylabel("Score")
    plt.grid()
    plt.savefig(os.path.join(out_dir, "figures", "joul-score.pdf"), pad_inches=0.2)
    plt.clf()
    plt.cla()

    vs_freq_plot(exp_res, exp_res_agg, "score_per_joule")

    plt.title("Frequency vs Score per Joule")
    plt.xlabel("Frequency, GHz")
    plt.ylabel("Score per Joule, 1/joules")
    plt.grid()
    plt.savefig(
        os.path.join(out_dir, "figures", "freq-score-per-joul.pdf"), pad_inches=0.2
    )
    plt.clf()
    plt.cla()

    vs_freq_plot(exp_res, exp_res_agg, "time")

    plt.title("Frequency vs time")
    plt.xlabel("Frequency, GHz")
    plt.ylabel("Time, s")
    plt.grid()
    plt.savefig(os.path.join(out_dir, "figures", "freq-time.pdf"), pad_inches=0.2)
    plt.clf()
    plt.cla()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process directories")
    parser.add_argument("read_dir", help="Path to the input directory")
    parser.add_argument("out_dir", help="Path to the output directory")

    args = parser.parse_args()

    data = load_data(args.read_dir)
    plot_everything(*data, out_dir=args.out_dir)
