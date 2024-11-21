# Duplicate Detection

## Introduction
Data deduplication is the process of identifying and removing duplicate records or entries within datasets. This tool provides functionalities to compare two datasets (Z1, Z2) and identify duplicate entries based on various criteria.

## Implementation Details
- **dedup_z1.py**: Implements data deduplication for Z1 dataset.
- **dedup_z2.py**: Implements data deduplication for Z2 dataset.
- **ascii_key.py**: Generates ASCII keys for data comparison.
- **main.py**: Integrates the deduplication process for both datasets.

## Project Structure

```bash
project_directory/
├── dedup_z2_test.py
├── dedup_z1_test.py
├── ascii_key.py
├── main.py
├── tests/
│ ├── test_file1.py
│ ├── test_file2.py
│ └── conftest.py
├── data/ # To Download the data,  follow the instructions in the README
│ ├── Z1.csv
│ ├── Z2.csv
│ ├── ZY1.csv
│ └── ZY2.csv
├── observation_issues  # Issues we encountered
│ ├── README.md
│ └── valid_true_ground_z1.py
└── requirements.txt
```

## Installation

### Prerequisites

- Python 3.x
- `pip` (Python package installer)

### Setting Up the Virtual Environment

1. **Create a virtual environment**:

   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
    - Windows: 
        ```bash 
        venv\Scripts\activate
        ```
    - macOS/Linux:
        ```bash 
        source venv/bin/activate
        ```

3. **Install the dependencies**:
   ```bash 
    pip install -r requirements.txt
   ```
### Running Tests

1. **Ensure the virtual environment is activated**:
    - Windows
   ```bash 
    venv\Scripts\activate
    ```
    - macOS/Linux
    ```bash 
    source venv/bin/activate
   ```

2. Set the PYTHONPATH environment variable:
    - Windows
    ```bash 
    set PYTHONPATH=.
    ```
    - macOS/Linux
    ```bash 
    export PYTHONPATH=.
    ```

3. Run Tests:
    ```bash 
     pytest 
   ```

3. Download the Data:
    First download data.zip from "https://bigdama.github.io/teaching/Programmierpraktikum.html" and extract it in the folder data.

### Usage
1. **Run main.py**: Integrates the deduplication process for both datasets.
    ```bash
    python main.py
    ```

## Authors
Noah Kogge, Berra Akbas, Jan Dangberg

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## DISCLOSURE: 
We took inspiration from: 
https://dbgroup.ing.unimore.it/sigmod22contest/leaders.shtml