#!/usr/bin/env python3
"""
Deep expanded analysis of Shane telescope PostgreSQL data.
Performs advanced pattern detection, anomaly analysis, and system health assessment.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

print("="*80)
print("SHANE TELESCOPE DEEP EXPANDED ANALYSIS")
print("="*80)

# Configuration
SAMPLE_SIZE = 100000  # Analyze 100k records per file for speed
OUTPUT_DIR = 'explore'

def load_and_prepare_data(filename, sample_size=100000):
    """Load PostgreSQL dump with smart boundary detection."""
    print(f"\nLoading {filename}...")

    try:
        # Find COPY statement to skip SQL header
        with open(f'data/{filename}', 'r') as f:
            for i, line in enumerate(f):
                if line.startswith('COPY'):
                    skiprows = i + 1
                    break

        # Read data
        df = pd.read_csv(
            f'data/{filename}',
            sep='\t',
            skiprows=skiprows,
            header=None,
            names=['time', 'keyword', 'binvalue', 'ascvalue', 'repeated', 'discarded'],
            dtype={'time': float, 'keyword': str, 'binvalue': str, 'ascvalue': str,
                   'repeated': int, 'discarded': int},
            nrows=sample_size,
            on_bad_lines='skip'
        )

        # Convert timestamps
        df['datetime'] = pd.to_datetime(df['time'], unit='s')
        df['hour'] = df['datetime'].dt.hour
        df['day_of_year'] = df['datetime'].dt.dayofyear
        df['month'] = df['datetime'].dt.month

        # Try to convert ascvalue to numeric where possible
        df['numeric_value'] = pd.to_numeric(df['ascvalue'], errors='coerce')

        print(f"  ✓ Loaded {len(df):,} records")
        return df

    except Exception as e:
        print(f"  ✗ Error loading {filename}: {e}")
        return None

# Load data
check120 = load_and_prepare_data('check120.dump', SAMPLE_SIZE)
met3apf = load_and_prepare_data('met3apf.dump', SAMPLE_SIZE)

if check120 is not None and met3apf is not None:
    print("\n" + "="*80)
    print("GENERATING ADVANCED VISUALIZATIONS")
    print("="*80)

    # =========================================================================
    # Figure 6: Motor Status Evolution (M3-M11)
    # =========================================================================
    print("\n[1/5] Motor status evolution over time...")

    motor_keywords = [f'M{i}STATUS' for i in range(3, 12)]
    motor_data = met3apf[met3apf['keyword'].isin(motor_keywords)].copy()

    if len(motor_data) > 0:
        motor_daily = motor_data.groupby([motor_data['datetime'].dt.date, 'keyword']).size().unstack(fill_value=0)

        fig, ax = plt.subplots(figsize=(14, 8))
        for motor in motor_keywords:
            if motor in motor_daily.columns:
                ax.plot(motor_daily.index, motor_daily[motor], marker='o', label=motor, linewidth=2, markersize=3)

        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Daily Record Count', fontsize=12, fontweight='bold')
        ax.set_title('Motor Status (M3-M11) Activity Over Time', fontsize=14, fontweight='bold')
        ax.legend(loc='best', ncol=3)
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_DIR}/fig_06_motor_evolution.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("   ✓ Saved fig_06_motor_evolution.png")

    # =========================================================================
    # Figure 7: Weather Parameter Correlations
    # =========================================================================
    print("[2/5] Weather parameter correlations...")

    weather_keywords = [k for k in met3apf['keyword'].unique() if 'WX' in k or 'TEMP' in k or 'HUMID' in k]
    weather_data = met3apf[met3apf['keyword'].isin(weather_keywords[:15])].copy()  # Top 15 weather keywords

    if len(weather_data) > 100:
        weather_pivot = weather_data.pivot_table(
            index='datetime',
            columns='keyword',
            values='numeric_value',
            aggfunc='first'
        ).interpolate(method='linear')

        # Calculate correlation only for numeric columns with sufficient data
        valid_cols = weather_pivot.columns[weather_pivot.notna().sum() > 100].tolist()
        if len(valid_cols) > 2:
            corr_matrix = weather_pivot[valid_cols].corr()

            fig, ax = plt.subplots(figsize=(12, 10))
            sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                       square=True, ax=ax, cbar_kws={'label': 'Correlation'})
            ax.set_title('Weather Parameter Correlations', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)
            plt.tight_layout()
            plt.savefig(f'{OUTPUT_DIR}/fig_07_weather_correlations.png', dpi=150, bbox_inches='tight')
            plt.close()
            print("   ✓ Saved fig_07_weather_correlations.png")
        else:
            print("   ⊘ Insufficient numeric weather data for correlation analysis")
    else:
        print("   ⊘ Insufficient weather data available")

    # =========================================================================
    # Figure 8: Hourly Activity Pattern Heatmap
    # =========================================================================
    print("[3/5] Hourly activity patterns...")

    combined = pd.concat([
        check120[['datetime', 'keyword', 'hour']].assign(system='check120'),
        met3apf[['datetime', 'keyword', 'hour']].assign(system='met3apf')
    ])

    hourly_pattern = combined.groupby(['system', 'hour']).size().unstack(fill_value=0)

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    for idx, system in enumerate(['check120', 'met3apf']):
        system_data = combined[combined['system'] == system]
        hourly_by_keyword = system_data.groupby(['hour', 'keyword']).size().unstack(fill_value=0)
        top_keywords = hourly_by_keyword.sum().nlargest(10).index

        hourly_top = hourly_by_keyword[top_keywords]
        hourly_top.plot(kind='bar', ax=axes[idx], width=0.8)
        axes[idx].set_title(f'{system.upper()} - Hourly Activity Pattern (Top 10 Keywords)',
                           fontsize=12, fontweight='bold')
        axes[idx].set_xlabel('Hour of Day', fontsize=11)
        axes[idx].set_ylabel('Record Count', fontsize=11)
        axes[idx].legend(title='Keyword', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        axes[idx].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/fig_08_hourly_patterns.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved fig_08_hourly_patterns.png")

    # =========================================================================
    # Figure 9: Numeric Value Distribution (Top Keywords)
    # =========================================================================
    print("[4/5] Numeric value distributions...")

    numeric_keywords = []
    for kw in met3apf['keyword'].unique():
        kw_data = met3apf[met3apf['keyword'] == kw]['numeric_value'].dropna()
        if len(kw_data) > 100:
            numeric_keywords.append((kw, len(kw_data)))

    numeric_keywords = sorted(numeric_keywords, key=lambda x: x[1], reverse=True)[:6]

    if numeric_keywords:
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        axes = axes.flatten()

        for idx, (kw, _) in enumerate(numeric_keywords):
            values = met3apf[met3apf['keyword'] == kw]['numeric_value'].dropna()

            if len(values) > 0:
                axes[idx].hist(values, bins=50, color='steelblue', edgecolor='black', alpha=0.7)
                axes[idx].set_title(f'{kw}', fontsize=11, fontweight='bold')
                axes[idx].set_xlabel('Value', fontsize=10)
                axes[idx].set_ylabel('Frequency', fontsize=10)
                axes[idx].grid(True, alpha=0.3, axis='y')

                # Add statistics
                stats_text = f'Mean: {values.mean():.2f}\nStd: {values.std():.2f}\nN: {len(values)}'
                axes[idx].text(0.98, 0.97, stats_text, transform=axes[idx].transAxes,
                             fontsize=9, verticalalignment='top', horizontalalignment='right',
                             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.suptitle('Distribution of Top 6 Numeric Keywords (met3apf)',
                    fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_DIR}/fig_09_value_distributions.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("   ✓ Saved fig_09_value_distributions.png")

    # =========================================================================
    # Figure 10: System Reliability Metrics
    # =========================================================================
    print("[5/5] System reliability metrics...")

    metrics_data = {
        'System': ['check120', 'met3apf'],
        'Data Quality (%)': [
            check120[check120['discarded'] == 0].shape[0] / len(check120) * 100,
            met3apf[met3apf['discarded'] == 0].shape[0] / len(met3apf) * 100
        ],
        'No Repeated Values (%)': [
            check120[check120['repeated'] == 0].shape[0] / len(check120) * 100,
            met3apf[met3apf['repeated'] == 0].shape[0] / len(met3apf) * 100
        ],
        'Unique Keywords': [
            check120['keyword'].nunique(),
            met3apf['keyword'].nunique()
        ],
        'Time Span (years)': [
            (check120['datetime'].max() - check120['datetime'].min()).days / 365.25,
            (met3apf['datetime'].max() - met3apf['datetime'].min()).days / 365.25
        ]
    }

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Data Quality
    ax = axes[0, 0]
    ax.bar(metrics_data['System'], metrics_data['Data Quality (%)'], color=['#2ecc71', '#3498db'],
           edgecolor='black', linewidth=2)
    ax.set_ylabel('Percentage (%)', fontsize=11, fontweight='bold')
    ax.set_title('Data Quality (Non-Discarded Records)', fontsize=12, fontweight='bold')
    ax.set_ylim([98, 100])
    for i, v in enumerate(metrics_data['Data Quality (%)']):
        ax.text(i, v + 0.1, f'{v:.2f}%', ha='center', va='bottom', fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # No Repeated Values
    ax = axes[0, 1]
    ax.bar(metrics_data['System'], metrics_data['No Repeated Values (%)'], color=['#e74c3c', '#f39c12'],
           edgecolor='black', linewidth=2)
    ax.set_ylabel('Percentage (%)', fontsize=11, fontweight='bold')
    ax.set_title('Non-Repeated Records', fontsize=12, fontweight='bold')
    ax.set_ylim([70, 100])
    for i, v in enumerate(metrics_data['No Repeated Values (%)']):
        ax.text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # Unique Keywords
    ax = axes[1, 0]
    ax.bar(metrics_data['System'], metrics_data['Unique Keywords'], color=['#9b59b6', '#1abc9c'],
           edgecolor='black', linewidth=2)
    ax.set_ylabel('Count', fontsize=11, fontweight='bold')
    ax.set_title('Unique Keywords Monitored', fontsize=12, fontweight='bold')
    for i, v in enumerate(metrics_data['Unique Keywords']):
        ax.text(i, v + 5, str(v), ha='center', va='bottom', fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # Time Span
    ax = axes[1, 1]
    ax.bar(metrics_data['System'], metrics_data['Time Span (years)'], color=['#34495e', '#16a085'],
           edgecolor='black', linewidth=2)
    ax.set_ylabel('Years', fontsize=11, fontweight='bold')
    ax.set_title('Monitoring Time Span', fontsize=12, fontweight='bold')
    for i, v in enumerate(metrics_data['Time Span (years)']):
        ax.text(i, v + 0.3, f'{v:.1f}y', ha='center', va='bottom', fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    plt.suptitle('System Reliability Metrics Comparison', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/fig_10_reliability_metrics.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved fig_10_reliability_metrics.png")

    # =========================================================================
    # Advanced Statistics
    # =========================================================================
    print("\n" + "="*80)
    print("ADVANCED STATISTICS")
    print("="*80)

    print("\n### Motor Analysis (M3-M11)")
    for motor in motor_keywords:
        motor_records = met3apf[met3apf['keyword'] == motor]
        print(f"  {motor}: {len(motor_records):,} records")

    print(f"\n### Top 5 Keywords by Frequency (check120)")
    print(check120['keyword'].value_counts().head(5))
    print(f"\n### Top 5 Keywords by Frequency (met3apf)")
    print(met3apf['keyword'].value_counts().head(5))

    print(f"\n### Temporal Coverage")
    print(f"  check120: {check120['datetime'].min()} to {check120['datetime'].max()}")
    print(f"  met3apf: {met3apf['datetime'].min()} to {met3apf['datetime'].max()}")

    print("\n" + "="*80)
    print("✓ DEEP ANALYSIS COMPLETE")
    print("✓ Generated 5 additional figures (fig_06 through fig_10)")
    print("="*80)

else:
    print("\n✗ Failed to load data files")
