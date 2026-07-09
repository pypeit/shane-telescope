"""
Advanced analysis: correlations, anomalies, and detailed patterns.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import zscore
from collections import defaultdict
import warnings

warnings.filterwarnings('ignore')

DATA_DIR = Path('/mnt/tank/Astronomy/PypeIt/shane-telescope/data')
OUTPUT_DIR = Path('/mnt/tank/Astronomy/PypeIt/shane-telescope/explore')


def detect_numeric_patterns(dumps: dict):
    """Detect and analyze patterns in numeric keywords."""
    print(f"\n{'='*70}")
    print("ADVANCED NUMERIC PATTERN ANALYSIS")
    print('='*70)

    for name, df in dumps.items():
        print(f"\n{name}:")

        # Try to convert ascvalue to numeric for all keywords
        numeric_data = defaultdict(list)
        numeric_times = defaultdict(list)

        sample_kws = df['keyword'].value_counts().head(50).index

        for kw in sample_kws:
            kw_data = df[df['keyword'] == kw].sort_values('time')
            try:
                numeric_vals = pd.to_numeric(kw_data['ascvalue'], errors='coerce')
                valid_mask = numeric_vals.notna()

                if valid_mask.sum() > 10:  # At least 10 numeric values
                    numeric_data[kw] = numeric_vals[valid_mask].values
                    numeric_times[kw] = kw_data[valid_mask]['datetime'].values

                    # Compute interesting stats
                    vals = numeric_vals[valid_mask].values
                    std = np.std(vals)
                    mean = np.mean(vals)

                    if std > 0:
                        outliers = np.sum(np.abs(zscore(vals)) > 3)
                        if outliers > 0:
                            print(f"  {kw}: {len(vals)} values, mean={mean:.2f}, std={std:.2f}, outliers={outliers}")

            except:
                pass

        return numeric_data


def analyze_keyword_sequences(df: pd.DataFrame, sample_size: int = 10000):
    """Find repeated keyword sequences that might indicate system states."""
    print("\nAnalyzing keyword sequences...")

    # Get subset of data
    sample = df.sort_values('time').head(sample_size)
    keywords = sample['keyword'].values

    # Find repeating 3-keyword patterns
    patterns = defaultdict(int)
    for i in range(len(keywords) - 2):
        pattern = tuple(keywords[i:i+3])
        patterns[pattern] += 1

    top_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"  Top repeating patterns:")
    for pattern, count in top_patterns[:5]:
        print(f"    {' -> '.join(pattern)}: {count} times")


def compute_keyword_entropy(df: pd.DataFrame):
    """Compute entropy of keyword value distributions."""
    print("\nAnalyzing keyword value entropy...")

    entropy_values = {}

    for kw in df['keyword'].value_counts().head(30).index:
        values = df[df['keyword'] == kw]['ascvalue'].value_counts()
        probabilities = values / values.sum()
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        entropy_values[kw] = entropy

    # High entropy = diverse values, low entropy = repetitive values
    high_entropy = sorted(entropy_values.items(), key=lambda x: x[1], reverse=True)[:5]
    low_entropy = sorted(entropy_values.items(), key=lambda x: x[1])[:5]

    print(f"  High entropy (diverse values): {[kw for kw, _ in high_entropy]}")
    print(f"  Low entropy (repetitive values): {[kw for kw, _ in low_entropy]}")


def find_temporal_clusters(df: pd.DataFrame):
    """Find time periods with unusual activity."""
    print("\nFinding temporal clusters...")

    # Resample by day and look for outliers
    daily_counts = df.set_index('datetime').resample('1D').size()

    mean = daily_counts.mean()
    std = daily_counts.std()
    threshold = mean + 2 * std

    busy_days = daily_counts[daily_counts > threshold]
    quiet_days = daily_counts[daily_counts < (mean - 2*std)]

    print(f"  Busy days (>{threshold:.0f} records/day): {len(busy_days)}")
    if len(busy_days) > 0:
        print(f"    Examples: {busy_days.index[:3].strftime('%Y-%m-%d').tolist()}")

    print(f"  Quiet days (<{mean - 2*std:.0f} records/day): {len(quiet_days)}")
    if len(quiet_days) > 0:
        print(f"    Examples: {quiet_days.index[:3].strftime('%Y-%m-%d').tolist()}")


def cross_dataset_comparison(dumps: dict):
    """Compare patterns between the two datasets."""
    print(f"\n{'='*70}")
    print("CROSS-DATASET COMPARISON")
    print('='*70)

    names = list(dumps.keys())
    if len(names) < 2:
        print("Only one dataset available")
        return

    df1, df2 = dumps[names[0]], dumps[names[1]]

    # Find common keywords
    kws1 = set(df1['keyword'].unique())
    kws2 = set(df2['keyword'].unique())
    common = kws1 & kws2
    only_in_1 = kws1 - kws2
    only_in_2 = kws2 - kws1

    print(f"\nKeyword overlap:")
    print(f"  Common: {len(common)} keywords")
    print(f"  Only in {names[0]}: {len(only_in_1)} keywords")
    print(f"  Only in {names[1]}: {len(only_in_2)} keywords")

    if len(only_in_1) > 0:
        print(f"  Unique to {names[0]}: {list(only_in_1)[:5]}...")
    if len(only_in_2) > 0:
        print(f"  Unique to {names[1]}: {list(only_in_2)[:5]}...")

    # Compare frequency of common keywords
    if common:
        print(f"\nCommon keyword frequency comparison:")
        for kw in list(common)[:5]:
            count1 = len(df1[df1['keyword'] == kw])
            count2 = len(df2[df2['keyword'] == kw])
            print(f"  {kw}: {count1:,} ({names[0]}) vs {count2:,} ({names[1]})")


def main():
    """Run advanced analysis."""
    print("\n" + "="*70)
    print("SHANE TELESCOPE ADVANCED ANALYSIS")
    print("="*70)

    # Load dumps
    print("\nLoading data...")
    dumps = {}
    for dump_file in sorted(DATA_DIR.glob('*.dump')):
        print(f"  Loading {dump_file.name}...")
        df = pd.read_csv(dump_file, sep='\t', header=None, skiprows=38,
                        names=['time', 'keyword', 'binvalue', 'ascvalue', 'repeated', 'discarded'],
                        dtype={'time': float, 'keyword': str, 'binvalue': str,
                               'ascvalue': str, 'repeated': int, 'discarded': int})
        df['datetime'] = pd.to_datetime(df['time'], unit='s')
        dumps[dump_file.stem] = df

    # Run analyses
    for name, df in dumps.items():
        print(f"\n{name}:")
        detect_numeric_patterns({name: df})
        analyze_keyword_sequences(df)
        compute_keyword_entropy(df)
        find_temporal_clusters(df)

    cross_dataset_comparison(dumps)

    print("\n" + "="*70)
    print("ADVANCED ANALYSIS COMPLETE")
    print("="*70)


if __name__ == '__main__':
    main()
