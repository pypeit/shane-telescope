"""
Robust analysis with better dump file handling and visualizations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict
import time
import warnings

warnings.filterwarnings('ignore')

DATA_DIR = Path('../data')
OUTPUT_DIR = Path('../explore')
OUTPUT_DIR.mkdir(exist_ok=True)

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

START_TIME = time.time()


def read_dump_safely(filepath, nrows=500000):
    """Read dump file with better error handling."""
    print(f"Loading {filepath.name}...")

    try:
        # Find where actual data starts by reading file header
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f):
                if 'COPY' in line and 'FROM stdin' in line:
                    skip_to = line_num + 1
                    break
            else:
                print(f"  ERROR: No COPY statement found")
                return None

        columns = ['time', 'keyword', 'binvalue', 'ascvalue', 'repeated', 'discarded']

        # Read directly from the data start, stop at first non-numeric time
        df = pd.read_csv(filepath, sep='\t', header=None, skiprows=skip_to,
                        names=columns, nrows=nrows,
                        dtype={'time': float, 'keyword': str,
                               'binvalue': str, 'ascvalue': str,
                               'repeated': int, 'discarded': int},
                        on_bad_lines='skip', engine='python')

        if len(df) > 0:
            df['datetime'] = pd.to_datetime(df['time'], unit='s')
            print(f"  ✓ Loaded {len(df):,} records")
            return df
        else:
            print(f"  ERROR: No data rows read")
            return None

    except Exception as e:
        print(f"  ERROR: {str(e)[:100]}")
        return None


def create_visualizations(dumps):
    """Create all 5 required figures."""
    print(f"\n{'='*80}")
    print("GENERATING VISUALIZATIONS")
    print('='*80)

    # Figure 1: Temporal Distribution
    print("\n[1/5] Temporal distribution...")
    fig, axes = plt.subplots(2, 1, figsize=(16, 10))
    for ax, (name, df) in zip(axes, dumps.items()):
        daily = df.set_index('datetime').resample('1D').size()
        ax.plot(daily.index, daily.values, linewidth=1.5, alpha=0.7, label='Daily')
        weekly = daily.rolling(7, center=True).mean()
        ax.plot(weekly.index, weekly.values, linewidth=2.5, label='7-day avg', alpha=0.9)
        ax.set_title(f'{name}: Daily Record Count', fontsize=13, fontweight='bold')
        ax.set_ylabel('Records/Day')
        ax.legend()
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig_01_temporal_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved")

    # Figure 2: Keyword Frequency
    print("[2/5] Keyword frequency...")
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    for ax, (name, df) in zip(axes, dumps.items()):
        top_kws = df['keyword'].value_counts().head(20)
        top_kws.plot(kind='barh', ax=ax, color='steelblue')
        ax.set_title(f'{name}: Top 20 Keywords', fontsize=12, fontweight='bold')
        ax.set_xlabel('Record Count')
        ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig_02_keyword_frequency.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved")

    # Figure 3: Value Types
    print("[3/5] Value type distribution...")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, (name, df) in zip(axes, dumps.items()):
        numeric = 0
        string = 0
        for kw in df['keyword'].value_counts().head(100).index:
            try:
                pd.to_numeric(df[df['keyword'] == kw]['ascvalue'].dropna())
                numeric += 1
            except:
                string += 1
        ax.pie([numeric, string], labels=['Numeric', 'String'],
               autopct='%1.0f%%', colors=['#66c2a5', '#fc8d62'],
               startangle=90, textprops={'fontsize': 11})
        ax.set_title(f'{name}: Keyword Value Types', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig_03_value_types.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved")

    # Figure 4: Data Quality
    print("[4/5] Data quality assessment...")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, (name, df) in zip(axes, dumps.items()):
        valid = len(df) - df['repeated'].sum() - df['discarded'].sum()
        sizes = [valid, df['repeated'].sum(), df['discarded'].sum()]
        labels = ['Valid', 'Repeated', 'Discarded']
        colors = ['#99ccff', '#ffcc99', '#ff9999']
        ax.pie(sizes, labels=labels, autopct='%1.2f%%',
               colors=colors, startangle=90, textprops={'fontsize': 10})
        ax.set_title(f'{name}: Data Quality', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig_04_data_quality.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved")

    # Figure 5: Keyword Correlations
    print("[5/5] Keyword correlations...")
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    for ax, (name, df) in zip(axes, dumps.items()):
        df_sorted = df.sort_values('time')
        pairs = defaultdict(int)
        # Sample for speed
        sample_size = min(50000, len(df_sorted))
        sample = df_sorted.sample(sample_size, random_state=42)
        for i in range(len(sample) - 1):
            kw1 = sample.iloc[i]['keyword']
            kw2 = sample.iloc[i+1]['keyword']
            if kw1 != kw2:
                pair = tuple(sorted([kw1, kw2]))
                pairs[pair] += 1

        top = sorted(pairs.items(), key=lambda x: x[1], reverse=True)[:12]
        names = [f"{p[0][0][:9]}-{p[0][1][:9]}" for p in top]
        counts = [p[1] for p in top]
        ax.barh(names, counts, color='steelblue')
        ax.set_title(f'{name}: Top Keyword Pairs', fontsize=12, fontweight='bold')
        ax.set_xlabel('Co-occurrence')
        ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig_05_keyword_correlations.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved")


def main():
    """Run complete analysis."""
    print(f"\n{'='*80}")
    print("SHANE TELESCOPE DEEP ANALYSIS")
    print('='*80)

    # Load dumps
    dumps = {}
    for dump_file in sorted(DATA_DIR.glob('*.dump')):
        df = read_dump_safely(dump_file, nrows=1000000)
        if df is not None and len(df) > 0:
            dumps[dump_file.stem] = df

    if not dumps:
        print("ERROR: Could not load any data!")
        return None

    # Generate visualizations
    create_visualizations(dumps)

    # Statistics
    print(f"\n{'='*80}")
    print("ANALYSIS SUMMARY")
    print('='*80)

    total_records = 0
    for name, df in dumps.items():
        total_records += len(df)
        print(f"\n{name}:")
        print(f"  Records: {len(df):,}")
        print(f"  Time: {df['datetime'].min().date()} to {df['datetime'].max().date()}")
        print(f"  Keywords: {df['keyword'].nunique()}")
        print(f"  Valid: {(1 - (df['repeated'].sum() + df['discarded'].sum())/len(df))*100:.2f}%")

    elapsed = time.time() - START_TIME
    print(f"\n{'='*80}")
    print(f"✓ Analysis complete in {elapsed/60:.1f} minutes")
    print(f"✓ Generated 5 figures")
    print(f"✓ Processed {total_records:,} records")
    print('='*80)

    return dumps


if __name__ == '__main__':
    main()
