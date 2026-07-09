"""
Utilities for reading PostgreSQL dump files from Shane telescope data.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Iterator


def find_data_start(dump_file: Path) -> int:
    """Find the line number where actual data begins in a PostgreSQL dump."""
    with open(dump_file, 'r') as f:
        for i, line in enumerate(f, 1):
            if line.startswith('COPY'):
                # Data starts on the next line after COPY statement
                return i + 1
    raise ValueError(f"No COPY statement found in {dump_file}")


def read_dump_chunk(dump_file: Path, chunksize: int = 10000,
                    skip_rows: Optional[int] = None) -> Iterator[pd.DataFrame]:
    """
    Read dump file in chunks.

    Parameters
    ----------
    dump_file : Path
        Path to the dump file
    chunksize : int
        Number of rows to read per chunk
    skip_rows : int, optional
        Number of rows to skip before data (found automatically if not provided)

    Yields
    ------
    pd.DataFrame
        Chunk of data
    """
    if skip_rows is None:
        skip_rows = find_data_start(dump_file) - 1

    # Column names for dump files
    columns = ['time', 'keyword', 'binvalue', 'ascvalue', 'repeated', 'discarded']

    for chunk in pd.read_csv(dump_file, sep='\t', header=None,
                             skiprows=skip_rows, chunksize=chunksize,
                             dtype={'time': float, 'keyword': str,
                                   'binvalue': str, 'ascvalue': str,
                                   'repeated': int, 'discarded': int},
                             names=columns):
        yield chunk


def count_rows(dump_file: Path) -> int:
    """Count number of data rows in dump file (excluding SQL header)."""
    skip_rows = find_data_start(dump_file) - 1
    with open(dump_file, 'r') as f:
        # Skip to data start
        for _ in range(skip_rows):
            f.readline()
        # Count remaining lines (excluding final '\.' which ends the COPY)
        count = 0
        for line in f:
            if line.strip() != r'\.':
                count += 1
    return count
