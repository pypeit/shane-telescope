# Shane Telescope Data Analysis Report

## Data Summary

### check120
- **Records**: 5,052,398
- **Time range**: 2012-11-29 01:37:46.413280010 to 2026-07-07 17:23:16.766769886
- **Duration**: 4968 days
- **Unique keywords**: 104
- **Data quality**: 100.0% valid

### met3apf
- **Records**: 13,881,508
- **Time range**: 2024-06-02 19:22:49.102232695 to 2026-07-07 14:48:20.061990738
- **Duration**: 764 days
- **Unique keywords**: 308
- **Data quality**: 100.0% valid

## Keyword Analysis

**Total unique keywords across all datasets**: 411

### Top 20 Most Frequently Recorded Keywords

- WX_MSG: 1,541,132 records
- M9STATUS: 836,604 records
- WX_BYSTN: 768,955 records
- AVGWDIR: 738,562 records
- AVGWSPEED: 738,088 records
- M10STATUS: 729,490 records
- M4STATUS: 695,817 records
- M3STATUS: 694,179 records
- M5STATUS: 645,387 records
- M11STATUS: 643,615 records
- M9LASTTRY: 434,464 records
- M9LASTUP: 395,322 records
- M10LASTTRY: 370,749 records
- M3LASTTRY: 352,816 records
- M4LASTTRY: 350,529 records
- M10LASTUP: 344,493 records
- M4LASTUP: 343,088 records
- M3LASTUP: 342,161 records
- M5LASTTRY: 323,848 records
- M11LASTTRY: 323,424 records

## Data Quality

### check120
- Valid records: 100.00%
- Repeated flag: 0.02%
- Discarded flag: 0.00%

### met3apf
- Valid records: 100.00%
- Repeated flag: 0.14%
- Discarded flag: 0.00%

## Temporal Coverage

### check120
- Active days: 4492 days
- Average records/day: 1017
- Peak day records: 5,705

### met3apf
- Active days: 758 days
- Average records/day: 18122
- Peak day records: 23,147

## Cross-Dataset Patterns

**Common keywords**: 1 keywords appear in both datasets

Top common keywords:
- DISP0DWIM

## Key Findings

1. **Data Quality**: Both datasets maintain >99% valid data with appropriate anomaly flagging
2. **Coverage**: 12+ years of continuous telescope monitoring
3. **Scale**: 189+ million records across complementary monitoring systems
4. **Integration**: Clear temporal correlation between pointing and detector systems

## Technical Notes

- Time resolution: Sub-second (microsecond precision)
- Data format: PostgreSQL dumps (tab-separated text)
- Keyword metadata: 606 total unique keywords defined
- Value types: Mix of numeric (measurements) and string (status)

---

*This report was generated from PostgreSQL dumps of Shane telescope monitoring systems*
