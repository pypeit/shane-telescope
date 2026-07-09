"""
Quick exploration of Shane telescope PostgreSQL dump data.
"""

from pathlib import Path
import sys
from . import io


def explore_dumps():
    """Quick examination of dump files."""
    # Get path relative to project root
    data_dir = Path('/mnt/tank/Astronomy/PypeIt/shane-telescope/data')

    print("=" * 70)
    print("SHANE TELESCOPE DATA EXPLORATION")
    print("=" * 70)

    # Examine dump files
    dump_files = list(data_dir.glob('*.dump'))
    print(f"\nFound {len(dump_files)} dump files:")

    for dump_file in dump_files:
        print(f"\n{dump_file.name}:")
        try:
            start_line = io.find_data_start(dump_file)
            print(f"  - Data starts at line: {start_line}")

            # Read a small sample
            print(f"  - Sample records:")
            for i, chunk in enumerate(io.read_dump_chunk(dump_file, chunksize=5)):
                if i == 0:
                    print(f"    Columns: {list(chunk.columns)}")
                    print(f"    First 3 rows:")
                    for _, row in chunk.head(3).iterrows():
                        print(f"      {row.to_dict()}")
                    break
        except Exception as e:
            print(f"  ERROR: {e}")


def explore_keywords():
    """Quick examination of keyword definition files."""
    data_dir = Path('/mnt/tank/Astronomy/PypeIt/shane-telescope/data')

    print("\n" + "=" * 70)
    print("KEYWORD DEFINITIONS")
    print("=" * 70)

    # Examine keyword files
    keyword_files = {
        'poco': data_dir / 'gshowpocolonghelp',
        'met3apf': data_dir / 'gshowmet3apflonghelp'
    }

    for name, filepath in keyword_files.items():
        if filepath.exists():
            print(f"\n{name}:")
            try:
                keywords = io.parse_longhelp_file(filepath)
                print(f"  - Total keywords: {len(keywords)}")
                print(f"  - First 5 keywords:")
                for kw in list(keywords.keys())[:5]:
                    metadata = keywords[kw]
                    print(f"    - {kw}: {metadata.get('Type', 'Unknown type')}")
            except Exception as e:
                print(f"  ERROR parsing: {e}")


def explore_mapping():
    """Quick examination of keyword mapping file."""
    data_dir = Path('/mnt/tank/Astronomy/PypeIt/shane-telescope/data')
    mapping_file = data_dir / 'poco_kwd2db.body'

    print("\n" + "=" * 70)
    print("KEYWORD MAPPING DOCUMENTATION")
    print("=" * 70)

    if mapping_file.exists():
        with open(mapping_file, 'r') as f:
            content = f.read()
        print(f"\nFile size: {len(content)} bytes")
        print(f"Number of lines: {len(content.splitlines())}")
        print("\nFirst 500 characters:")
        print(content[:500])


if __name__ == '__main__':
    try:
        explore_dumps()
        explore_keywords()
        explore_mapping()
        print("\n" + "=" * 70)
        print("Exploration complete!")
        print("=" * 70)
    except Exception as e:
        print(f"Error during exploration: {e}")
        sys.exit(1)
