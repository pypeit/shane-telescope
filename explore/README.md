# Shane Telescope Data Analysis Results

This directory contains the comprehensive exploratory data analysis of the Shane telescope PostgreSQL database dumps.

## Generated Files

### Reports
- `detailed_analysis_report.md` - Main comprehensive analysis report with findings and visualizations
- `readme_io.md` - Guide to understanding and reading the database dump files
- `keyword_metadata.json` - Parsed keyword metadata and categorization
- `anomaly_analysis.json` - Temporal clustering and anomaly detection results

### Visualizations
- `fig_01_temporal_distribution.png` - Monthly record count over time for both datasets
- `fig_02_keyword_distribution.png` - Top 15 keywords by frequency
- `fig_03_quality_flags.png` - Data quality breakdown (valid/repeated/discarded)
- `fig_04_keyword_correlations.png` - Top co-occurring keyword pairs
- `fig_05_value_types.png` - Distribution of numeric vs string keywords
- `fig_06_temporal_patterns.png` - Weekly record distribution patterns

## Data Sources

### Check120.dump (12 GB)
- ~50.5 million records
- Time span: October 2012 - 2024
- Purpose: Checkpoint/pointing system monitoring
- Unique keywords: Multiple hundreds

### Met3apf.dump (7.2 GB)
- ~138.8 million records
- Time span: 2016 - 2025
- Purpose: Detector server telemetry
- Unique keywords: Multiple hundreds

### Keyword Definition Files
- `gshowpocolonghelp` - 313 POCO (pointing) keywords with metadata
- `gshowmet3apflonghelp` - 293 detector server keywords with metadata
- `poco_kwd2db.body` - WCS keyword mapping documentation

## Analysis Approach

1. **Initial Exploration** - Quick examination of data structure and volume
2. **Basic Statistics** - Record counts, time ranges, keyword distributions
3. **Quality Assessment** - Data quality flags, anomaly patterns
4. **Temporal Analysis** - Observation patterns, clustering, gaps
5. **Correlation Analysis** - Keyword relationships and co-occurrence
6. **Pattern Detection** - Noteworthy behaviors and anomalies

## Key Findings

- **High Data Quality**: >99% valid measurement records
- **Long-term Operations**: 12+ years of continuous monitoring
- **System Integration**: Clear temporal correlation between pointing and detector systems
- **Comprehensive Monitoring**: 606 unique keywords across both systems
- **Reliable Data Collection**: Consistent observation patterns with appropriate anomaly flagging

## Python Analysis Tools

Created modular Python utilities in `../src/shane_telescope/`:
- `smart_loader.py` - Robust PostgreSQL dump file parsing
- `io/` - General I/O utilities
- `analysis/` - Analysis modules
- `run_full_analysis.py` - Comprehensive EDA
- `fast_analysis.py` - Quick analysis using sampling
- `detailed_keyword_analysis.py` - Keyword metadata analysis
- `temporal_anomaly_analysis.py` - Temporal pattern detection
- `final_report_generator.py` - Report generation

## Usage

To reproduce or extend this analysis:

```python
from src.shane_telescope.smart_loader import load_dump_data

# Load data
df = load_dump_data(Path('data/check120.dump'), sample_fraction=0.1)

# Analyze
print(f"Records: {len(df)}")
print(f"Keywords: {df['keyword'].nunique()}")
print(f"Time range: {df['datetime'].min()} to {df['datetime'].max()}")
```

## Next Steps

Potential extensions of this analysis:
1. Deep-dive into specific keywords or time periods
2. Advanced statistical modeling of temporal trends
3. Correlation network analysis between keywords
4. Long-term drift analysis for critical parameters
5. Event detection and flagging algorithms

---

*Analysis generated: 2026-07-09*
*Data span: 2012-2025 (12+ years)*
*Total records: 189+ million*
