#stats_toolkit.py
import csv
import math
from pathlib import Path
import subprocess
import sys

DATA_PATH = Path("data") / "agent_deposits.csv"

def load_csv_rows(path: Path) -> list[dict]:
    with open(path, "r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))

def mean(values: list[float]) -> float:
    if len(values) == 0:
        raise ValueError("Cannot calculate mean of empty data")

    total = 0

    for value in values:
        total = total + value

    return total / len(values)



def load_column(
    path: Path, column: str
) -> tuple[list[float], list[tuple[int, str]]]:

    valid_values = []  
    rejected = []      

    with open(path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

       
        if reader.fieldnames is None or column not in reader.fieldnames:
            raise ValueError(f"Column '{column}' not found in CSV")

        
        for row_number, row in enumerate(reader, start=2):
            raw_value = row.get(column)

            try:
                
                if raw_value is None or raw_value.strip() == "":
                    raise ValueError("Missing value")

               
                value = float(raw_value)

                if not math.isfinite(value):
                    raise ValueError("Value is not finite")

                
                valid_values.append(value)

            except (ValueError, AttributeError):
                
                rejected.append((row_number, raw_value))

    
    return valid_values, rejected



def median(values: list[float]) -> float:
    if len(values) == 0:
        raise ValueError("Cannot calculate median of empty data")

    
    ordered = sorted(values)
    middle = len(ordered) // 2

    
    if len(ordered) % 2 == 1:
        return ordered[middle]

    
    return (ordered[middle - 1] + ordered[middle]) / 2



def mode(values: list[float]) -> list[float]:
    if len(values) == 0:
        raise ValueError("Cannot calculate mode of empty data")

    frequencies = {}

   
    for value in values:
        frequencies[value] = frequencies.get(value, 0) + 1

    highest_frequency = max(frequencies.values())

    
    if highest_frequency == 1:
        return []

   
    return [
        value
        for value, frequency in frequencies.items()
        if frequency == highest_frequency
    ]



def variance(values: list[float], sample: bool = True) -> float:
    minimum_count = 2 if sample else 1

    if len(values) < minimum_count:
        raise ValueError("Not enough values to calculate variance")

    average = mean(values)
    squared_differences = []

  
    for value in values:
        squared_differences.append((value - average) ** 2)

    
    divisor = len(values) - 1 if sample else len(values)

    return sum(squared_differences) / divisor



def std_dev(values: list[float], sample: bool = True) -> float:
    return math.sqrt(variance(values, sample))



def quartiles(values: list[float]) -> tuple[float, float, float]:
    if len(values) == 0:
        raise ValueError("Cannot calculate quartiles of empty data")

    ordered = sorted(values)
    middle = len(ordered) // 2
    q2 = median(ordered)

    
    if len(ordered) % 2 == 0:
        lower_half = ordered[:middle]
        upper_half = ordered[middle:]
    else:
      
        lower_half = ordered[:middle]
        upper_half = ordered[middle + 1:]

    if len(ordered) == 1:
        return ordered[0], ordered[0], ordered[0]

    q1 = median(lower_half)
    q3 = median(upper_half)

    return q1, q2, q3



def iqr_outliers(values: list[float], k: float = 1.5) -> dict:
    if len(values) == 0:
        raise ValueError("Cannot detect outliers in empty data")

    q1, _, q3 = quartiles(values)
    iqr = q3 - q1

    
    lower_fence = q1 - k * iqr
    upper_fence = q3 + k * iqr

    
    outliers = [
        value for value in values
        if value < lower_fence or value > upper_fence
    ]

    return {
        "iqr": iqr,
        "lower_fence": lower_fence,
        "upper_fence": upper_fence,
        "outliers": outliers,
    }



class StatisticsAnalyzer:

    def __init__(
        self, values: list[float], name: str = "values"
    ) -> None:
        # Store a copy so the original list is not changed accidentally.
        self.values = list(values)
        self.name = name

        if len(self.values) == 0:
            raise ValueError("Analyzer requires at least one valid value")

    @classmethod
    def from_csv(cls, path: Path, column: str) -> "StatisticsAnalyzer":
        values, rejected = load_column(path, column)

     
        analyzer = cls(values, column)
        analyzer.rejected = rejected
        analyzer.rows_read = len(values) + len(rejected)
        return analyzer

   
    def summary(self) -> dict:
        q1, q2, q3 = quartiles(self.values)
        outlier_info = iqr_outliers(self.values)

        return {
            "count": len(self.values),
            "mean": mean(self.values),
            "median": q2,
            "mode": mode(self.values),
            "variance": variance(self.values),
            "std_dev": std_dev(self.values),
            "min": min(self.values),
            "max": max(self.values),
            "q1": q1,
            "q2": q2,
            "q3": q3,
            "iqr": outlier_info["iqr"],
            "lower_fence": outlier_info["lower_fence"],
            "upper_fence": outlier_info["upper_fence"],
            "outliers": outlier_info["outliers"],
        }

   
    def without_outliers(self) -> "StatisticsAnalyzer":
        info = iqr_outliers(self.values)
        outlier_values = info["outliers"]

        remaining = [
            value for value in self.values
            if value not in outlier_values
        ]

        if len(remaining) == 0:
            raise ValueError("No values remain after removing outliers")

        return StatisticsAnalyzer(remaining, self.name)

   
    def report(self) -> str:
        original = self.summary()
        cleaned = self.without_outliers().summary()

        lines = [
            f"=== Statistics report: {self.name} ===",
            f"Rows read         : {getattr(self, 'rows_read', len(self.values))}",
            f"Valid values      : {len(self.values)}",
            f"Rejected values   : {len(getattr(self, 'rejected', []))}",
        ]

      
        for row_number, raw_value in getattr(self, "rejected", []):
            if raw_value is None or str(raw_value).strip() == "":
                reason = "Missing value"
            else:
                try:
                    number = float(raw_value)
                    reason = (
                        "Value is not finite"
                        if not math.isfinite(number)
                        else "Rejected value"
                    )
                except (ValueError, TypeError):
                    reason = "Not a number"

            lines.append(
                f"  row {row_number}: '{raw_value}' ({reason})"
            )

        lines.append("")
        lines.append(
            f"{'':20}{'all data':>14}{'outliers removed':>22}"
        )

       
        for label, key in [
            ("count", "count"),
            ("mean", "mean"),
            ("median", "median"),
            ("mode", "mode"),
            ("variance (sample)", "variance"),
            ("std dev (sample)", "std_dev"),
        ]:
            first = original[key]
            second = cleaned[key]

           
            if key == "mode":
                first = first if first else "none"
                second = second if second else "none"

            lines.append(f"{label:20}{str(first):>14}{str(second):>22}")

        lines.append(
            f"{'min / max':20}"
            f"{str(original['min']) + ' / ' + str(original['max']):>14}"
            f"{str(cleaned['min']) + ' / ' + str(cleaned['max']):>22}"
        )
        lines.append(
            f"{'Q1 / Q3':20}"
            f"{str(original['q1']) + ' / ' + str(original['q3']):>14}"
            f"{str(cleaned['q1']) + ' / ' + str(cleaned['q3']):>22}"
        )
        lines.append(
            f"{'IQR':20}{str(original['iqr']):>14}{str(cleaned['iqr']):>22}"
        )
        lines.append(
            f"Outlier fences      : lower {original['lower_fence']}, "
            f"upper {original['upper_fence']}"
        )
       
        csv_rows = load_csv_rows(DATA_PATH)
        outlier_details = []

        for row in csv_rows:
            raw_value = row.get(self.name, "")

            try:
                value = float(raw_value)
            except (ValueError, TypeError):
                continue

            if value in original["outliers"]:
                outlier_details.append(
                    f"{value} ({row.get('date', 'unknown')}, "
                    f"{row.get('agent_id', 'unknown')})"
                )

        lines.append("Outliers            : " + ", ".join(outlier_details))
               
        return "\n".join(lines)



def compare_with_numpy(
    analyzer: StatisticsAnalyzer
) -> dict[str, bool]:
  
    import numpy as np

    values = analyzer.values
    q1, _, q3 = quartiles(values)

   
    tolerance = 1e-9

    checks = {
        "mean": np.isclose(mean(values), np.mean(values), atol=tolerance),
        "median": np.isclose(median(values), np.median(values), atol=tolerance),
        "variance": np.isclose(
            variance(values),
            np.var(values, ddof=1),
            atol=tolerance,
        ),
        "std dev": np.isclose(
            std_dev(values),
            np.std(values, ddof=1),
            atol=tolerance,
        ),
    }
    ordered = sorted(values)
    middle = len(ordered) // 2

    if len(ordered) % 2 == 0:
        lower_half = ordered[:middle]
        upper_half = ordered[middle:]
    else:
        lower_half = ordered[:middle]
        upper_half = ordered[middle + 1:]

    numpy_q1 = np.median(lower_half)
    numpy_q3 = np.median(upper_half)
    
    
    checks["Q1 / Q3"] = (
        np.isclose(q1, numpy_q1, atol=tolerance)
    and np.isclose(q3, numpy_q3, atol=tolerance)
    ) 

    return {
        name: bool(matches) 
        for name, matches in checks.items()
    }



    
if __name__ == "__main__":
    analyzer = StatisticsAnalyzer.from_csv(
        DATA_PATH, "daily_deposits_kes"
    )

   
    report_parts = [analyzer.report()]

   
    numpy_lines = ["=== NumPy verification ==="]
    for name, matches in compare_with_numpy(analyzer).items():
        result = "MATCH" if matches else "MISMATCH"

        if name == "variance":
            line = f"{name:12} {result} (ddof=1)"
        elif name == "Q1 / Q3":
            line = f"{name:12} {result} (method=median of halves)"
        else:
            line = f"{name:12} {result}"

        numpy_lines.append(line)

    report_parts.append("\n".join(numpy_lines))

    
    test_result = subprocess.run(
        [sys.executable, "-m", "unittest"],
        capture_output=True,
        text=True,
    )

    test_output = test_result.stderr + test_result.stdout
    test_lines = test_output.splitlines()

    
    summary_line = next(
        (line for line in test_lines if line.startswith("Ran ")),
        "Test summary unavailable",
    )

    status = "OK" if test_result.returncode == 0 else "FAILED"

    test_section = (
        "=== Unit tests ===\n"
        f"{summary_line}\n"
        f"{status}"
    )

    report_parts.append(test_section)

    
    full_report = "\n\n".join(report_parts) + "\n"

    print(full_report)

    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    (output_dir / "stats_report.txt").write_text(
        full_report,
        encoding="utf-8",
    )

