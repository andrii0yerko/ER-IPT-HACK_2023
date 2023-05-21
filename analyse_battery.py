import glob
import re

import pandas as pd


def load_logs():
    results = []
    for file in glob.glob("test_results_battery/*.log"):
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

        results.append(
            {
                "freq": freq,
                "Joules": joules,
                "result": score,
                "time": elapsed,
                "battery": battery,
            }
        )
    return pd.DataFrame(results)


if __name__ == "__main__":
    df = load_logs()
    df["ratio"] = df["Joules"] / df["battery"]
    df.groupby("freq").agg({"ratio": ["mean", "max", "min"]}).to_excel(
        "tables/battery.xlsx"
    )
