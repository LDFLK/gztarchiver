# Getting Started

## Installation
```bash
pip install git+https://github.com/LDFLK/gztarchiver.git
```

## How It Works

**Step 1: Create & Configure YAML File** 
- Download the example [``config example``](config_example.yaml) file from the repository.
- Edit the configurations to specify your download preferences, storage locations, and other settings
- This file acts as the control center for your archiving operations

**Step 2: Run the Program** 
- Finally, execute the program using the command-line interface with your desired parameters. (Check the usage section)
- Sit back and watch as your documents are systematically archived and categorized!


## Usage

After installation, you can run the program using the command-line tool/terminal

**Show help:**
```bash
gztarchiver --help
```

**Extract data for specific year:**
```bash
gztarchiver --year 2023 --lang en --config path-to-the-config-file
```

**Extract data for specific month in a year:**
```bash
gztarchiver --year 2023 --month 06 --lang en --config path-to-the-config-file
```

**Extract data for specific date:**
```bash
gztarchiver --year 2023 --month 06 --day 15 --lang en --config path-to-the-config-file
```

## Options

| Option | Description | Example | Default |
|--------|-------------|---------|---------|
| `--year` | Filter by year or download all | `--year 2023` | None |
| `--month` | Filter by specific month (01-12) | `--month 06` | None |
| `--day` | Filter by specific day (01-31) | `--day 15` | None |
| `--lang` | Specify language | `--lang en` | None |

## Language Codes

| Code | Language |
|------|----------|
| `en` | English |
| `si` | Sinhala |
| `ta` | Tamil |


## Output Structure

Downloaded documents are organized as:
```
~/doc-archive/
├── 2023/
│   ├── 01/
│   │   ├── 15/
│   │   │   └── gazette_id/
│   │   │       ├── gazette_id_english.pdf   
│   │   └── ...
│   | 
|   ├── records/
|   |    ├── successfully_archived.csv
|   |    ├── failed_to_archive.csv
|   |    ├── document_unavailable.csv
|   |    ├── document_classification.csv
|   └── ...
└── ...
```

## Log Files

For each year, the following log files are created:
- `{year}/records/successfully_archived.csv` - Successfully downloaded files
- `{year}/records/failed_to_archive.csv` - Failed downloads with retry information
- `{year}/records/document_unavailable.csv` - Unavailable logs
- `{year}/records/document_classification.csv` - Document Classified metadata

## Error Messages

- **No gazettes found**: `❌ No gazettes found for year 2023 with month 06`
- **Invalid year**: `❌ Year '2025' not found in years.json`
- **Invalid month**: `❌ Invalid month '13'. Must be between 01-12`
- **Invalid day**: `❌ Invalid day '32'. Must be between 01-31`
