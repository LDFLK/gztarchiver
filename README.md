# 🥽 gztarchiver 
A library for extracting and downloading gazettes from resource website

## 🛠️ Installation

```bash
pip install gztarchiver
```

> ⚠️ If installed with `--user`, make sure your Python user scripts directory is in your PATH:
>
> For example:
> ```bash
> export PATH="$HOME/Library/Python/3.9/bin:$PATH"
> ```

---

## 🚀 How It Works

### 📋 Step-by-Step Workflow

**Step 1: Create & Configure YAML File** ⚙️
- Download the example `config.yaml` file from the repository and edit it according to your preferences [download](config_example.yaml)
- Edit this configuration file to specify your download preferences, archive storage locations, and other settings
- This file acts as the control center for your archiving operations

**Step 2: Run the Program** 🏃‍♂️
- Finally, execute the program using the command-line interface with your desired parameters
- The program will use your configuration to start downloading, organizing, and classifying gazette files
- Sit back and watch as your gazettes are systematically archived!

---

## 🚀 Usage

After installation, you can run the program using the command-line tool:

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

## 🎛️ Options

| Option | Description | Example | Default |
|--------|-------------|---------|---------|
| `--year` | Filter by year or download all | `--year 2023` | None |
| `--month` | Filter by specific month (01-12) | `--month 06` | None |
| `--day` | Filter by specific day (01-31) | `--day 15` | None |
| `--lang` | Specify language | `--lang en` | None |

## 🌍 Language Codes

| Code | Language |
|------|----------|
| `en` | English |
| `si` | Sinhala |
| `ta` | Tamil |


## ✨ Features

- **Resume capability**: If interrupted, run the same command again to resume downloads
- **Graceful shutdown**: Press `Ctrl+C` to stop after current downloads complete
- **Progress tracking**: Real-time download progress with statistics
- **Smart filtering**: Filter by year, month, day, and language
- **File validation**: Automatic validation of downloaded PDF files
- **Get new updates**: Can get new updates years and other data
- **Organized storage**: Files saved in structured folders: `year/month/day/gazette_id/`
- **Comprehensive logging**: Detailed logs for successful and failed downloads
- **Error handling**: Automatic retry for failed downloads with intelligent error reporting

## 📁 Output Structure

Downloads are organized as:
```
~/Desktop/doc-archive/
├── 2023/
│   ├── 01/
│   │   ├── 15/
│   │   │   └── gazette_id/
│   │   │       ├── gazette_id_english.pdf   
│   │   └── ...
│   └── ...
└── ...
```

## 📊 Log Files

For each year, the following log files are created:
- `archive_logs.csv` - Successfully downloaded files
- `failed_logs.csv` - Failed downloads with retry information
- `unavailable_logs.csv` - Unavailable logs
- `classified_metadata.csv` - Document Classified metadata

## 🚨 Error Messages

- **No gazettes found**: `❌ No gazettes found for year 2023 with month 06`
- **Invalid year**: `❌ Year '2025' not found in years.json`
- **Invalid month**: `❌ Invalid month '13'. Must be between 01-12`
- **Invalid day**: `❌ Invalid day '32'. Must be between 01-31`

## 📟 Status

🚧 Under Development

---

**Thank you for using gztarchiver!**