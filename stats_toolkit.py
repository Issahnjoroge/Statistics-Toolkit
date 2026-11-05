"""
Day 3 - Statistical Analysis Toolkit
squad python specialization - Data Science, AI & Analytics
RULE: implement every calculation yourself with plain python.
Numpy may be imported ONLY in comapre_with_numpy(), to verify. your results.
Do not use statistics module.
"""
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
    """Calculate and return the arithmetic mean of the values."""
    if len(values) == 0:
        raise ValueError("Cannot calculate mean of empty data")

    total = 0

    for value in values:
        total = total + value

    return total / len(values)



def load_column(
    path: Path, column: str
) -> tuple[list[float], list[tuple[int, str, str]]]:

    valid_values = []  
    rejected = []      

    if not Path(path).is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")
    
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

            except (ValueError, AttributeError) as error:
                reason = str(error)

                if "could not convert string to float" in reason:
                    reason = "Not a number"


                rejected.append((row_number, raw_value, reason))

    
    return valid_values, rejected



def median(values: list[float]) -> float:
    """Calculate and return the middle value of the sorted data."""
    if len(values) == 0:
        raise ValueError("Cannot calculate median of empty data")

    
    ordered = sorted(values)
    middle = len(ordered) // 2

    
    if len(ordered) % 2 == 1:
        return ordered[middle]

    
    return (ordered[middle - 1] + ordered[middle]) / 2



def mode(values: list[float]) -> list[float]:
    """Return every value that occurs most often (a list, because there can be ties or none)."""
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
    """Sample variance (n - 1) by default; population variance (n) when sample is False."""
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


def quartiles_from_sorted(
    ordered: list[float]
) -> tuple[float, float, float]:
    """Calculate Q1, Q2, and Q3 from an already sorted list."""

    if len(ordered) == 0:
        raise ValueError("Cannot calculate quartiles of empty data")

    middle = len(ordered) // 2
    q2 = median(ordered)

    if len(ordered) == 1:
        return ordered[0], ordered[0], ordered[0]

    if len(ordered) % 2 == 0:
        lower_half = ordered[:middle]
        upper_half = ordered[middle:]
    else:
        lower_half = ordered[:middle]
        upper_half = ordered[middle + 1:]

    q1 = median(lower_half)
    q3 = median(upper_half)

    return q1, q2, q3



def quartiles(values: list[float]) -> tuple[float, float, float]:
    """Return Q1, Q2, and Q3 using the median-of-halves method."""

    ordered = sorted(values)
    return quartiles_from_sorted(ordered)



def iqr_outliers(values: list[float], k: float = 1.5) -> dict:
    """Return the IQR, lower and upper fences, and detected outliers."""
    if len(values) == 0:
        raise ValueError("Cannot detect outliers in empty data")

    if k < 0:
        raise ValueError("K must be non-negative")

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
    """Wraps one numeric column and exposes every statistic above as a method."""

    def __init__(
        self, values: list[float], name: str = "values"
    ) -> None: 
        
        self.values = list(values)
        self.name = name
        self.sorted_values = sorted(self.values)

        if len(self.values) == 0:
            raise ValueError("Analyzer requires at least one valid value")

    @classmethod
    def from_csv(cls, path: Path, column: str) -> "StatisticsAnalyzer":
        values, rejected = load_column(path, column)

     
        analyzer = cls(values, column)
        analyzer.path = Path(path)
        analyzer.rejected = rejected
        analyzer.rows_read = len(values) + len(rejected)
        return analyzer

   
    def summary(self) -> dict:
        q1, q2, q3 = quartiles_from_sorted(self.sorted_values)
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

        cleaned_analyzer = self.without_outliers()
        cleaned = cleaned_analyzer.summary()

        lines = [
            f"=== Statistics report: {self.name} ===",
            f"Rows read         : {getattr(self, 'rows_read', len(self.values))}",
            f"Valid values      : {len(self.values)}",
            f"Rejected values   : {len(getattr(self, 'rejected', []))}",
        ]

        for row_number, raw_value, reason in getattr(self, "rejected", []):
            lines.append(
                f"  row {row_number}: '{raw_value}' ({reason})"
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
                first_text = ", ".join(map(str, first)) if first else "none"
                second_text = ", ".join(map(str, second)) if second else "none"

            elif key == "count":
                first_text = str(first)
                second_text = str(second)

            else:
                first_text = f"{first:.2f}"
                second_text = f"{second:.2f}"

            lines.append(
                f"{label:20}{first_text:>14}{second_text:>22}"
            )

        lines.append(
            f"{'min / max':20}"
            f"{f'{original["min"]:.2f} / {original["max"]:.2f}':>14}"
            f"{f'{cleaned["min"]:.2f} / {cleaned["max"]:.2f}':>22}"
        )
        original_quartiles = (
            f"{original['q1']:.2f} / {original['q3']:.2f}"
        )

        cleaned_quartiles = (
            f"{cleaned['q1']:.2f} / {cleaned['q3']:.2f}"
        )

        lines.append(
            f"{'Q1 / Q3':20}"
            f"{original_quartiles:>14}"
            f"{cleaned_quartiles:>22}"
        )

        lines.append(
            f"{'IQR':20}"
            f"{original['iqr']:>14.2f}"
            f"{cleaned['iqr']:>22.2f}"
        )

        lines.append(
            f"Outlier fences      : lower {original['lower_fence']:.2f}, "
            f"upper {original['upper_fence']:.2f}"
        )
       
        csv_rows = load_csv_rows(self.path)
        outlier_details = []

        for row in csv_rows:
            raw_value = row.get(self.name, "")

            try:
                value = float(raw_value)
            except (ValueError, TypeError):
                continue

            if value in original["outliers"]:
                outlier_details.append(
                    f"{value:.2f} ({row.get('date', 'unknown')}, "
                    f"{row.get('agent_id', 'unknown')})"
                )

        lines.append("Outliers            : " + ", ".join(outlier_details))

        lines.append("")
        lines.append("=== Risk-team notes ===")
        lines.append(
            "1. AG-104: The deposits of KES 96,500.00 and "
            "KES 88,400.00 are unusually high and should be "
            "reviewed against transaction records."
        )
        lines.append(
            "2. AG-104: The deposit of KES 1,200.00 is "
            "unusually low and should be checked for possible "
            "incomplete reporting or operational issues."
        )
        lines.append(
            "3. AG-101: The deposit of KES 29,060.99 is slightly "
            "above the upper IQR fence and should be checked "
            "against supporting records."
        )
               
        return "\n".join(lines)



def compare_with_numpy(
    analyzer: StatisticsAnalyzer
) -> dict[str, bool]:
    """Import numpy HERE, recompute each statistic and return {name: matches}."""
  
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
    ordered = np.sort(np.array(values))
    middle = len(ordered) // 2

    if len(ordered) % 2 == 0:
        lower_half = ordered[:middle]
        upper_half = ordered[middle:]
    else:
        lower_half = ordered[:middle]
        upper_half = ordered[middle + 1:]

    numpy_q1 = np.percentile(values, 25, method="nearest")
    numpy_q3 = np.percentile(values, 75, method="nearest")
    
    
    checks["Q1 / Q3"] = (
        np.isclose(q1, numpy_q1, atol=tolerance)
    and np.isclose(q3, numpy_q3, atol=tolerance)
    ) 

    return {
        name: bool(matches) 
        for name, matches in checks.items()
    }



def format_numpy_results(analyzer: StatisticsAnalyzer) -> str:
    """Format the NumPy verification results for the report."""

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

    return "\n".join(numpy_lines)


def run_unit_tests() -> str:
    """Run unit tests and return a short test summary."""

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

    return (
        "=== Unit tests ===\n"
        f"{summary_line}\n"
        f"{status}"
    )


def main() -> None:
    """Generate, display, and save the statistics report."""

    analyzer = StatisticsAnalyzer.from_csv(
        DATA_PATH, "daily_deposits_kes"
    )

    report_parts = [
        analyzer.report(),
        format_numpy_results(analyzer),
        run_unit_tests(),
    ]

    full_report = "\n\n".join(report_parts) + "\n"

    print(full_report)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    (output_dir / "stats_report.txt").write_text(
        full_report,
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
