"""
Comprehensive Shane telescope analysis with visualizations.
~2 hour deep dive into PostgreSQL dumps.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict
import time

# Configuration
DATA_DIR = Path('../data')
OUTPUT_DIR = Path('../explore')
OUTPUT_DIR.mkdir(exist_ok=True)

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

START_TIME = time.time()

print("\n" + "="*80)
print("SHANE TELESCOPE COMPREHENSIVE ANALYSIS - 2 HOUR DEEP DIVE")
print("="*80)


def find_data_boundaries(filepath):
    """Find data start/end in PostgreSQL dump."""
    data_start = None
    with open(filepath, 'r') as f:
        for i, line in enumerate(f, 1):
            if 'COPY' in line and 'FROM stdin' in line:
                data_start = i + 1
                break
    return data_start


def load_dump(filepath, sample_frac=0.25):
    """Load dump file with sampling."""
    print(f"\n{'='*80}")
    print(f"Loading {filepath.name}...")
    print('='*80)

    data_start = find_data_boundaries(filepath)
    if not data_start:
        print(f"ERROR: Could not find data in {filepath}")
        return None

    columns = ['time', 'keyword', 'binvalue', 'ascvalue', 'repeated', 'discarded']
    skiprows = lambda x: (x < data_start - 1) or (np.random.random() > sample_frac and x >= data_start - 1)

    try:
        df = pd.read_csv(filepath, sep='\t', header=None, skiprows=skiprows,
                        names=columns, dtype={'time': float, 'keyword': str,
                                             'binvalue': str, 'ascvalue': str,
                                             'repeated': int, 'discarded': int},
                        on_bad_lines='skip')
        df['datetime'] = pd.to_datetime(df['time'], unit='s')
        print(f"✓ Loaded {len(df):,} records")
        return df
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def plot_temporal_distribution(dumps):
    """Generate temporal distribution visualizations."""
    print("\nGenerating temporal distribution plots...")

    fig, axes = plt.subplots(2, 1, figsize=(16, 10))

    for ax, (name, df) in zip(axes, dumps.items()):
        # Daily records
        daily = df.set_index('datetime').resample('1D').size()
        ax.plot(daily.index, daily.values, linewidth=1.5, label=f'{name} (daily)', alpha=0.7)

        # Weekly smoothing
        weekly = daily.rolling(window=7, center=True).mean()
        ax.plot(weekly.index, weekly.values, linewidth=2.5, label=f'{name} (7-day avg)', alpha=0.9)

        ax.set_title(f'{name}: Daily Record Count Over Time', fontsize=14, fontweight='bold')
        ax.set_ylabel('Records per Day')
        ax.set_xlabel('Date')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = OUTPUT_DIR / 'fig_01_temporal_distribution.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {path.name}")
    plt.close()


def plot_keyword_frequency(dumps):
    """Plot top keywords."""
    print("\nGenerating keyword frequency plots...")

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    for ax, (name, df) in zip(axes, dumps.items()):
        top_kws = df['keyword'].value_counts().head(20)
        top_kws.plot(kind='barh', ax=ax, color='steelblue')
        ax.set_title(f'{name}: Top 20 Keywords', fontsize=12, fontweight='bold')
        ax.set_xlabel('Record Count')
        ax.invert_yaxis()

    plt.tight_layout()
    path = OUTPUT_DIR / 'fig_02_keyword_frequency.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {path.name}")
    plt.close()


def plot_value_type_distribution(dumps):
    """Analyze numeric vs string values."""
    print("\nAnalyzing value types...")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for ax, (name, df) in zip(axes, dumps.items()):
        numeric_count = 0
        string_count = 0

        # Sample top 100 keywords
        for kw in df['keyword'].value_counts().head(100).index:
            values = df[df['keyword'] == kw]['ascvalue'].dropna()
            try:
                pd.to_numeric(values)
                numeric_count += 1
            except:
                string_count += 1

        labels = ['Numeric', 'String/Status']
        sizes = [numeric_count, string_count]
        colors = ['#66c2a5', '#fc8d62']
        explode = (0.05, 0.05)

        ax.pie(sizes, labels=labels, autopct='%1.0f%%', colors=colors,
               explode=explode, startangle=90, textprops={'fontsize': 11})
        ax.set_title(f'{name}: Keyword Value Types', fontsize=12, fontweight='bold')

    plt.tight_layout()
    path = OUTPUT_DIR / 'fig_03_value_types.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {path.name}")
    plt.close()


def plot_data_quality(dumps):
    """Plot data quality flags."""
    print("\nGenerating data quality plots...")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for ax, (name, df) in zip(axes, dumps.items()):
        valid = len(df) - df['repeated'].sum() - df['discarded'].sum()
        repeated = df['repeated'].sum()
        discarded = df['discarded'].sum()

        sizes = [valid, repeated, discarded]
        labels = [f'Valid\n({valid:,})', f'Repeated\n({repeated:,})', f'Discarded\n({discarded:,})']
        colors = ['#99ccff', '#ffcc99', '#ff9999']

        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.2f%%',
                                            colors=colors, startangle=90)
        ax.set_title(f'{name}: Data Quality', fontsize=12, fontweight='bold')

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

    plt.tight_layout()
    path = OUTPUT_DIR / 'fig_04_data_quality.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {path.name}")
    plt.close()


def plot_keyword_correlations(dumps):
    """Plot keyword co-occurrence patterns."""
    print("\nAnalyzing keyword correlations...")

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    for ax, (name, df) in zip(axes, dumps.items()):
        # Find keywords that appear together
        df_sorted = df.sort_values('time')
        pairs = defaultdict(int)

        # Sample for speed
        sample = df_sorted.sample(min(100000, len(df_sorted)), random_state=42)
        for i in range(len(sample) - 1):
            kw1 = sample.iloc[i]['keyword']
            kw2 = sample.iloc[i + 1]['keyword']
            if kw1 != kw2:
                pair = tuple(sorted([kw1, kw2]))
                pairs[pair] += 1

        top_pairs = sorted(pairs.items(), key=lambda x: x[1], reverse=True)[:15]
        pair_names = [f"{p[0][0][:10]}-{p[0][1][:10]}" for p in top_pairs]
        pair_counts = [p[1] for p in top_pairs]

        ax.barh(pair_names, pair_counts, color='steelblue')
        ax.set_title(f'{name}: Top Keyword Pairs', fontsize=12, fontweight='bold')
        ax.set_xlabel('Co-occurrence Count')
        ax.invert_yaxis()

    plt.tight_layout()
    path = OUTPUT_DIR / 'fig_05_keyword_correlations.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {path.name}")
    plt.close()


def analyze_statistics(dumps):
    """Compute detailed statistics."""
    print("\n" + "="*80)
    print("STATISTICAL ANALYSIS")
    print("="*80)

    stats = {}
    for name, df in dumps.items():
        print(f"\n{name}:")
        print(f"  Records: {len(df):,}")
        print(f"  Time range: {df['datetime'].min()} to {df['datetime'].max()}")
        print(f"  Duration: {(df['datetime'].max() - df['datetime'].min()).days} days")
        print(f"  Unique keywords: {df['keyword'].nunique()}")
        print(f"  Records per keyword: {len(df) / df['keyword'].nunique():.0f} avg")

        # Quality
        valid_pct = (1 - (df['repeated'].sum() + df['discarded'].sum()) / len(df)) * 100
        print(f"  Data quality: {valid_pct:.2f}% valid")
        print(f"  Repeated: {(df['repeated'].sum() / len(df)) * 100:.3f}%")
        print(f"  Discarded: {(df['discarded'].sum() / len(df)) * 100:.3f}%")

        # Temporal
        daily = df.set_index('datetime').resample('1D').size()
        print(f"  Days active: {(daily > 0).sum()}")
        print(f"  Records/day (mean): {daily.mean():.0f}")
        print(f"  Records/day (max): {daily.max():,}")

        stats[name] = {
            'records': len(df),
            'keywords': df['keyword'].nunique(),
            'quality': valid_pct,
            'days_active': (daily > 0).sum(),
            'records_per_day_mean': daily.mean(),
            'records_per_day_max': daily.max()
        }

    return stats


def main():
    """Run complete analysis."""
    print(f"\nStart time: {time.strftime('%H:%M:%S')}")

    # Load data
    dumps = {}
    for dump_file in sorted(DATA_DIR.glob('*.dump')):
        df = load_dump(dump_file, sample_frac=0.25)
        if df is not None:
            dumps[dump_file.stem] = df

    if not dumps:
        print("ERROR: No data loaded!")
        return

    # Generate visualizations
    print("\n" + "="*80)
    print("GENERATING VISUALIZATIONS")
    print("="*80)

    plot_temporal_distribution(dumps)
    plot_keyword_frequency(dumps)
    plot_value_type_distribution(dumps)
    plot_data_quality(dumps)
    plot_keyword_correlations(dumps)

    # Statistics
    stats = analyze_statistics(dumps)

    elapsed = time.time() - START_TIME
    print(f"\n{'='*80}")
    print(f"Analysis completed in {elapsed/60:.1f} minutes")
    print(f"End time: {time.strftime('%H:%M:%S')}")
    print("="*80)

    return dumps, stats


if __name__ == '__main__':
    dumps, stats = main()
