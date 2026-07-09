"""
Smart data loader that properly handles PostgreSQL dumps.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Tuple

DATA_DIR = Path('/mnt/tank/Astronomy/PypeIt/shane-telescope/data')


def find_data_boundaries(filepath: Path) -> Tuple[int, int]:
    """Find where actual data starts and ends in a PostgreSQL dump."""
    data_start = None
    data_end = None

    with open(filepath, 'r') as f:
        for i, line in enumerate(f, 1):
            if 'COPY' in line and 'FROM stdin' in line:
                data_start = i + 1  # Data starts on next line
            if line.strip() == r'\.':
                data_end = i - 1  # End line is the \. marker
                break

    return data_start, data_end


def load_dump_data(filepath: Path, sample_fraction: float = 1.0) -> pd.DataFrame:
    """Load dump file, optionally sampling data."""
    print(f"Loading {filepath.name}...")

    data_start, data_end = find_data_boundaries(filepath)

    if data_start is None:
        raise ValueError(f"Could not find data start in {filepath.name}")

    # Skip rows before data
    skiprows_before = data_start - 1

    # Calculate how many rows of actual data
    nrows = data_end - data_start + 1 if data_end else None

    if sample_fraction < 1.0:
        # Randomly sample
        import random
        nrows = int(nrows * sample_fraction) if nrows else None
        skiprows = lambda x: x < skiprows_before or (x > skiprows_before and random.random() > sample_fraction)
    else:
        skiprows = range(skiprows_before)

    columns = ['time', 'keyword', 'binvalue', 'ascvalue', 'repeated', 'discarded']

    try:
        df = pd.read_csv(filepath, sep='\t', header=None, skiprows=skiprows,
                        names=columns, dtype={'time': float, 'keyword': str,
                                             'binvalue': str, 'ascvalue': str,
                                             'repeated': int, 'discarded': int},
                        nrows=nrows, error_bad_lines=False)
    except TypeError:
        # Older pandas version
        df = pd.read_csv(filepath, sep='\t', header=None, skiprows=skiprows,
                        names=columns, dtype={'time': float, 'keyword': str,
                                             'binvalue': str, 'ascvalue': str,
                                             'repeated': int, 'discarded': int},
                        nrows=nrows, on_bad_lines='skip')

    df['datetime'] = pd.to_datetime(df['time'], unit='s')

    print(f"  Loaded: {len(df):,} records")
    if df.empty:
        print(f"  WARNING: No data loaded! data_start={data_start}, data_end={data_end}")

    return df


def main():
    """Test the loader."""
    for dump_file in sorted(DATA_DIR.glob('*.dump')):
        df = load_dump_data(dump_file)
        if not df.empty:
            print(f"  Time range: {df['datetime'].min()} to {df['datetime'].max()}")
            print(f"  Unique keywords: {df['keyword'].nunique()}")


if __name__ == '__main__':
    main()
