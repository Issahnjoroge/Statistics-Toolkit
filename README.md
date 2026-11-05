# Day 3 — Statistics Toolkit

## Overview

This project is a statistics toolkit built with plain Python. It reads deposit data from a CSV file, validates the values, calculates descriptive statistics, identifies outliers, and verifies selected results using NumPy.

## Features

- Load a numeric column from a CSV file.
- Identify missing, invalid, and non-finite values.
- Calculate mean, median, and mode.
- Calculate sample and population variance.
- Calculate standard deviation.
- Calculate quartiles and the interquartile range.
- Detect outliers using IQR fences.
- Compare results with NumPy.
- Run unit tests to check calculations and data validation.
- Generate a text report at `output/stats_report.txt`.

## Requirements

- Python 3
- NumPy

## Installation

Install the required dependency using:

```bash
pip3 install -r requirements.txt
```

## How to Run

From the project directory, generate the statistics report using:

```bash
python3 stats_toolkit.py
```

The report is saved to:

`output/stats_report.txt`

## How to Run Unit Tests

Run the tests using:

```bash
python3 -m unittest -v
```

## Statistical Method

Quartiles are calculated using the **median-of-halves** method.

Outliers are identified using the IQR fences:

- Lower fence = Q1 − 1.5 × IQR
- Upper fence = Q3 + 1.5 × IQR

The toolkit calculates both sample and population variance.

Sample variance uses `n - 1` in the denominator and is used when estimating the variance of a larger population from a sample. Population variance uses `n` and describes the spread of the complete population.

NumPy is used to verify selected calculations. The toolkit's own statistical calculations use plain Python.

## Data Validation Rules and Assumptions

- The CSV file is expected to contain the required deposit column and relevant record details, such as date and agent ID.
- Missing values are rejected.
- Non-numeric values are rejected.
- Non-finite numeric values, such as infinity and NaN, are rejected.
- Each valid deposit value is treated as one observation.
- The IQR method uses a multiplier of 1.5 to identify potential outliers.
- Outliers are flagged for review; they are not automatically assumed to be errors or fraudulent transactions.

## Current Test Results

The current test run passes all 9 unit tests. The NumPy verification checks report `MATCH` for the tested statistics.

## Output

The generated report includes:

- Number of rows read, valid values, and rejected values.
- Descriptive statistics for all valid data.
- Statistics after removing detected outliers.
- Outlier fences and identified outlier records.
- NumPy verification results.
- Unit-test summary.
