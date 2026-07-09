"""
Detailed keyword correlation and pattern analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
import json

DATA_DIR = Path('/mnt/tank/Astronomy/PypeIt/shane-telescope/data')


def analyze_keyword_metadata():
    """Parse and analyze keyword metadata files."""
    print("Analyzing keyword metadata...")

    keywords = {}

    # Parse POCO keywords
    poco_file = DATA_DIR / 'gshowpocolonghelp'
    if poco_file.exists():
        with open(poco_file, 'r') as f:
            content = f.read()

        # Parse keyword blocks
        current_kw = None
        for line in content.split('\n'):
            if line and not line[0].isspace():
                current_kw = line.strip()
                keywords[current_kw] = {'source': 'poco', 'metadata': {}}
            elif current_kw and ':' in line:
                key, val = line.split(':', 1)
                keywords[current_kw]['metadata'][key.strip()] = val.strip()

    # Parse met3apf keywords
    met_file = DATA_DIR / 'gshowmet3apflonghelp'
    if met_file.exists():
        with open(met_file, 'r') as f:
            content = f.read()

        current_kw = None
        for line in content.split('\n'):
            if line and not line[0].isspace():
                current_kw = line.strip()
                if current_kw not in keywords:
                    keywords[current_kw] = {'source': 'met3apf', 'metadata': {}}
                else:
                    keywords[current_kw]['source'] = 'both'
            elif current_kw and ':' in line:
                key, val = line.split(':', 1)
                keywords[current_kw]['metadata'][key.strip()] = val.strip()

    print(f"  Total unique keywords: {len(keywords)}")

    # Categorize by type
    types = defaultdict(list)
    for kw, data in keywords.items():
        ktype = data['metadata'].get('Type', 'unknown')
        types[ktype].append(kw)

    print(f"  Keyword types found:")
    for ktype, kws in sorted(types.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"    {ktype}: {len(kws)} keywords")

    return keywords


def analyze_wcs_mapping():
    """Analyze WCS keyword mapping documentation."""
    print("\nAnalyzing WCS mapping...")

    mapping_file = DATA_DIR / 'poco_kwd2db.body'
    if mapping_file.exists():
        with open(mapping_file, 'r') as f:
            content = f.read()

        lines = content.split('\n')
        reference_systems = set()

        for line in content.lower():
            if 'fk4' in line:
                reference_systems.add('FK4')
            if 'fk5' in line:
                reference_systems.add('FK5')
            if 'icrs' in line:
                reference_systems.add('ICRS')
            if 'equinox' in line:
                reference_systems.add('EQUINOX')

        print(f"  Reference systems mentioned: {', '.join(sorted(reference_systems))}")
        print(f"  Documentation lines: {len(lines)}")


def main():
    """Run detailed keyword analysis."""
    print("\n" + "="*70)
    print("DETAILED KEYWORD ANALYSIS")
    print("="*70)

    keywords = analyze_keyword_metadata()
    analyze_wcs_mapping()

    # Save metadata to file
    output_file = Path('/mnt/tank/Astronomy/PypeIt/shane-telescope/explore/keyword_metadata.json')
    with open(output_file, 'w') as f:
        # Convert to serializable format
        serializable = {}
        for kw, data in keywords.items():
            serializable[kw] = {
                'source': data['source'],
                'metadata_keys': list(data['metadata'].keys())
            }
        json.dump(serializable, f, indent=2)

    print(f"\n✓ Keyword metadata saved to {output_file.name}")


if __name__ == '__main__':
    main()
