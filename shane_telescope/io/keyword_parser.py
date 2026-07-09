"""
Utilities for parsing keyword definition files from Shane telescope.
"""

from pathlib import Path
from typing import Dict, List, Optional
import re


def parse_longhelp_file(filepath: Path) -> Dict[str, Dict[str, str]]:
    """
    Parse a gshow longhelp output file into structured keyword definitions.

    Parameters
    ----------
    filepath : Path
        Path to the gshow longhelp file

    Returns
    -------
    dict
        Dictionary mapping keyword names to their metadata
    """
    keywords = {}
    current_keyword = None
    current_data = {}

    with open(filepath, 'r') as f:
        for line in f:
            line = line.rstrip('\n')

            # Check if this is a new keyword (no leading whitespace)
            if line and not line[0].isspace():
                # Save previous keyword if exists
                if current_keyword:
                    keywords[current_keyword] = current_data


                current_keyword = line.strip()
                current_data = {}
            else:
                # This is metadata for the current keyword
                if current_keyword:
                    # Parse key: value pairs
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        current_data[key] = value

    # Don't forget the last keyword
    if current_keyword:
        keywords[current_keyword] = current_data

    return keywords


def get_keyword_metadata(keywords: Dict, keyword_name: str) -> Optional[Dict]:
    """Get metadata for a specific keyword."""
    return keywords.get(keyword_name)


def list_all_keywords(keywords: Dict) -> List[str]:
    """Get list of all keyword names."""
    return sorted(keywords.keys())


def extract_keyword_types(keywords: Dict) -> Dict[str, str]:
    """Extract Type information for each keyword."""
    types = {}
    for kw, metadata in keywords.items():
        if 'Type' in metadata:
            types[kw] = metadata['Type']
    return types
