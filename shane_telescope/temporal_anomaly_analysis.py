"""
Temporal clustering and anomaly detection analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
import json

DATA_DIR = Path('/mnt/tank/Astronomy/PypeIt/shane-telescope/data')


def analyze_temporal_clustering(df, name):
    """Find temporal clusters and anomalies."""
    print(f"\nTemporal clustering for {name}...")

    # Group by week
    weekly = df.set_index('datetime').resample('7D').size()

    mean_weekly = weekly.mean()
    std_weekly = weekly.std()

    # Find busy weeks (>2 std above mean)
    busy_threshold = mean_weekly + 2 * std_weekly
    busy_weeks = weekly[weekly > busy_threshold]

    # Find quiet weeks (<2 std below mean)
    quiet_threshold = mean_weekly - 2 * std_weekly
    quiet_weeks = weekly[weekly < quiet_threshold]

    print(f"  Weekly average: {mean_weekly:.0f} records/week")
    print(f"  Busy weeks (>{busy_threshold:.0f}): {len(busy_weeks)}")
    print(f"  Quiet weeks (<{quiet_threshold:.0f}): {len(quiet_weeks)}")

    if len(busy_weeks) > 0:
        print(f"    Most busy week: {busy_weeks.index[0].date()} ({busy_weeks.iloc[0]:.0f} records)")

    # Detect gaps (>7 days with no records)
    daily_counts = df.set_index('datetime').resample('1D').size()
    gaps = daily_counts[daily_counts == 0]
    if len(gaps) > 0:
        print(f"  Gaps detected: {len(gaps)} days with no records")

    return {
        'mean_weekly': float(mean_weekly),
        'std_weekly': float(std_weekly),
        'busy_weeks': len(busy_weeks),
        'quiet_weeks': len(quiet_weeks),
        'gaps': len(gaps)
    }


def analyze_keyword_volatility(df, name):
    """Analyze which keywords change most frequently."""
    print(f"\nKeyword volatility for {name}...")

    # Count records per keyword
    keyword_counts = df['keyword'].value_counts()

    # For each keyword, calculate how often it changes value
    volatility = {}
    for kw in keyword_counts.head(50).index:
        kw_data = df[df['keyword'] == kw].sort_values('time')
        if len(kw_data) > 1:
            value_changes = (kw_data['ascvalue'] != kw_data['ascvalue'].shift()).sum()
            volatility[kw] = {
                'records': len(kw_data),
                'changes': int(value_changes),
                'change_rate': float(value_changes / len(kw_data))
            }

    # Find most volatile keywords
    most_volatile = sorted(volatility.items(), key=lambda x: x[1]['change_rate'], reverse=True)[:10]

    print(f"  Most volatile keywords (highest change rate):")
    for kw, stats in most_volatile[:5]:
        print(f"    {kw}: {stats['change_rate']:.1%} changes")

    return volatility


def analyze_quality_patterns(df, name):
    """Analyze repeated and discarded flags."""
    print(f"\nQuality patterns for {name}...")

    # Check if repeated/discarded correlate with specific keywords
    repeated_by_kw = df[df['repeated'] == 1]['keyword'].value_counts().head(10)
    discarded_by_kw = df[df['discarded'] == 1]['keyword'].value_counts().head(10)

    print(f"  Top keywords with repeated flag:")
    for kw, count in repeated_by_kw.head(5).items():
        pct = (count / len(df[df['keyword'] == kw])) * 100
        print(f"    {kw}: {count} ({pct:.1f}% of records)")

    print(f"  Top keywords with discarded flag:")
    for kw, count in discarded_by_kw.head(5).items():
        pct = (count / len(df[df['keyword'] == kw])) * 100
        print(f"    {kw}: {count} ({pct:.1f}% of records)")

    # Time-based analysis
    daily_quality = df.set_index('datetime').resample('1D').agg({
        'repeated': 'mean',
        'discarded': 'mean'
    })

    bad_quality_days = daily_quality[(daily_quality['repeated'] > 0.05) | (daily_quality['discarded'] > 0.05)]
    print(f"  Days with high anomaly rates (>5%): {len(bad_quality_days)}")


def main():
    """Run temporal and anomaly analysis."""
    print("\n" + "="*70)
    print("TEMPORAL CLUSTERING & ANOMALY ANALYSIS")
    print("="*70)

    results = {}

    for dump_file in sorted(DATA_DIR.glob('*.dump')):
        print(f"\n{'='*70}")
        print(f"Processing {dump_file.name}...")
        print('='*70)

        # Load data (just first 100k records for speed)
        with open(dump_file, 'r') as f:
            for i, line in enumerate(f, 1):
                if line.startswith('COPY'):
                    skip_rows = i
                    break

        columns = ['time', 'keyword', 'binvalue', 'ascvalue', 'repeated', 'discarded']
        df = pd.read_csv(dump_file, sep='\t', header=None, skiprows=skip_rows,
                        names=columns, dtype={'time': float, 'keyword': str,
                                             'binvalue': str, 'ascvalue': str,
                                             'repeated': int, 'discarded': int},
                        nrows=100000)  # First 100k for speed

        df['datetime'] = pd.to_datetime(df['time'], unit='s')
        name = dump_file.stem

        # Run analyses
        temporal = analyze_temporal_clustering(df, name)
        volatility = analyze_keyword_volatility(df, name)
        analyze_quality_patterns(df, name)

        results[name] = {
            'temporal': temporal,
            'volatility_sample': {kw: v for kw, v in list(volatility.items())[:10]}
        }

    # Save results
    output_file = Path('/mnt/tank/Astronomy/PypeIt/shane-telescope/explore/anomaly_analysis.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✓ Anomaly analysis saved to {output_file.name}")


if __name__ == '__main__':
    main()
