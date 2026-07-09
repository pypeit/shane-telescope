# shane-telescope

Testing and development of IOP (inherent optical properties) algorithms using Shane telescope data.

## Overview

This repository is used to test a wide range of IOP (inherent optical properties) algorithms and generate metrics and diagnostics to share with the community.

## Installation

### Requirements

- Python >=3.11
- conda (recommended for environment management)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/PypeIt/shane-telescope.git
cd shane-telescope
```

2. Create a conda environment (optional but recommended):
```bash
conda create -n pypeit14b python=3.11
conda activate pypeit14b
```

3. Install the package:
```bash
pip install -e .
```

Or install dependencies only:
```bash
pip install -r requirements.txt
```

## Development

Install development dependencies:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
pytest tests/
```

## License

This project is licensed under the BSD 3-Clause License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.rst](CONTRIBUTING.rst) for guidelines.
