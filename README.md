# 🥽 gztarchiver 
A library for extracting and downloading gazettes from resource website

## 🛠️ Installation

```bash
pip install git+https://github.com/yasandu0505/gztarchiver.git
```

> ⚠️ If installed with `--user`, make sure your Python user scripts directory is in your PATH:
>
> For example:
> ```bash
> export PATH="$HOME/Library/Python/3.9/bin:$PATH"
> ```

---

## 🚀 How It Works

Let me tell you how my program works! The process is straightforward and involves three main steps:

### 📋 Step-by-Step Workflow

**Step 1: Setup Cloud Archive** 🌐
- First, you need to set up Google Cloud credentials to enable cloud storage functionality
- This involves creating a Google Cloud project, enabling the Drive API, and downloading your `credentials.json` file
- Save the credentials in a dedicated folder for security
- Add the credentials paths in step 2

**Step 2: Create & Configure YAML File** ⚙️
- Download the example `config.yaml` file from the repository and edit it according to your preferences [download](config_example.yaml)
- Edit this configuration file to specify your download preferences, storage locations, and other settings
- This file acts as the control center for your archiving operations

**Step 3: Run the Program** 🏃‍♂️
- Finally, execute the program using the command-line interface with your desired parameters
- The program will use your cloud credentials and configuration to start downloading and organizing gazette files
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

## ☁️ Setup Cloud Archive

**1. Go to Google Cloud Console**
```bash
https://console.cloud.google.com/
```

**2. Create a new project**

**3. Enable the Google Drive API in that project**

**4. Go to APIs & Services > Credentials**

**5. Click "Create Credentials" → "OAuth Client ID"**

**6. Choose Desktop App**

**7. Download the file — it's called `credentials.json`**

**8. Create a folder called `credentials` somewhere in your computer**

**9. Place the `credentials.json` inside the `credentials`**

**10. Copy the path and update the config.yaml file**

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