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
- Run unit tests to check the calculations and data validation.
- Generate a text report at `output/stats_report.txt`.



## Requirements

- Python 3
- NumPy



## Statistical Method

Quartiles are calculated using the **median-of-halves** method. Outliers are identified using the IQR fences:

- Lower fence = Q1 − 1.5 × IQR
- Upper fence = Q3 + 1.5 × IQR

NumPy is used to verify selected calculations. The implementation of the toolkit's statistical calculations uses plain Python.

## Current Test Results

The current test run passes all 9 unit tests. The NumPy verification checks report `MATCH` for the tested statistics.

## Output

The generated report includes:

- Number of rows read, valid values, and rejected values
- Descriptive statistics for all valid data
- Statistics after removing detected outliers
- Outlier fences and the identified outlier records
- NumPy verification results
- Unit test summary
