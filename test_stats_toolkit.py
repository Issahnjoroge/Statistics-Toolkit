"""Unit tests for the toolkit. Run with:  python -m unittest -v   (or pytest)."""
import unittest

from stats_toolkit import (
      mean, 
      median, 
      mode, 
      variance, 
      std_dev, 
      quartiles, 
      iqr_outliers, 
      load_column,
      StatisticsAnalyzer,
)


class TestCentralTendency(unittest.TestCase):
    def test_mean_of_known_values(self):
        self.assertEqual(mean([10, 20, 30]), 20)


    def test_median_even_and_odd_lengths(self):
        self.assertEqual(median([10,20,30]), 20)
        self.assertEqual(median([10, 20, 30, 40]), 25)

    def test_mode_with_ties(self):
        self.assertEqual(mode([10, 20, 20, 30, 30]), [20, 30])

    def test_empty_input_raises(self):
        with self.assertRaises(ValueError):
            mean([])


class TestSpread(unittest.TestCase):
    def test_sample_vs_population_variance(self):
        values = [10, 20, 30]
        self.assertAlmostEqual(variance(values), 100)
        self.assertAlmostEqual(variance(values, sample=False), 200 / 3)

    def test_std_dev_single_value(self):
        with self.assertRaises(ValueError):
            std_dev([10])



class TestOutliers(unittest.TestCase):
    def test_no_outliers_in_uniform_data(self):
        result = iqr_outliers([10, 10, 10, 10, 10])
        self.assertEqual(result["outliers"], [])

    def test_detects_obvious_outlier(self):
        result = iqr_outliers([10, 11, 12, 13, 14, 100])
        self.assertIn(100, result["outliers"])


class TestLoading(unittest.TestCase):
    def test_invalid_and_missing_values_are_rejected(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "test_data.csv"

            with open(csv_path, "w", encoding="utf-8") as file:
                file.write("amount,notes\n100,valid\n,missing\nunknown,invalid\n200,valid\n")

            values, rejected = load_column(csv_path, "amount")

            self.assertEqual(values, [100.0, 200.0])
            self.assertEqual(len(rejected), 2)


if __name__ == "__main__":
    unittest.main()
