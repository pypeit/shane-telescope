"""
Load and preprocess Shane telescope dump data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
import warnings

warnings.filterwarnings('ignore')


def load_dump_file(filepath: Path) -> pd.DataFrame:
    """Load a PostgreSQL dump file into memory."""
    print(f"Loading {filepath.name}...")

    # Find where data starts
    with open(filepath, 'r') as f:
        for i, line in enumerate(f, 1):
            if line.startswith('COPY'):
                skip_rows = i
                break

    columns = ['time', 'keyword', 'binvalue', 'ascvalue', 'repeated', 'discarded']
    df = pd.read_csv(filepath, sep='\t', header=None, skiprows=skip_rows,
                     names=columns, dtype={'time': float, 'keyword': str,
                                          'binvalue': str, 'ascvalue': str,
                                          'repeated': int, 'discarded': int})

    # Convert time to datetime
    df['datetime'] = pd.to_datetime(df['time'], unit='s')

    print(f"  Loaded: {len(df):,} records, {df['datetime'].min()} to {df['datetime'].max()}")
    print(f"  Memory: {df.memory_usage(deep=True).sum() / 1e9:.2f} GB")

    return df


def load_all_dumps(data_dir: Path) -> Dict[str, pd.DataFrame]:
    """Load all dump files."""
    dumps = {}
    for dump_file in sorted(data_dir.glob('*.dump')):
        name = dump_file.stem
        dumps[name] = load_dump_file(dump_file)
    return dumps


def classify_values(df: pd.DataFrame) -> Dict[str, list]:
    """Classify keywords as numeric or string based on ascvalue."""
    numeric_kws = set()
    string_kws = set()

    for kw in df['keyword'].unique():
        values = df[df['keyword'] == 'ascvalue'].sample(min(100, len(df[df['keyword'] == kw])))
        try:
            pd.to_numeric(values)
            numeric_kws.add(kw)
        except:
            string_kws.add(kw)

    return {'numeric': list(numeric_kws), 'string': list(string_kws)}
