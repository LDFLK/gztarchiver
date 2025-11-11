---
title: "🥽 gztarchiver — Automated Gazette Archiving Tool"
layout: default
description: "An intelligent Python-based tool for extracting, downloading, and archiving Sri Lankan government gazettes."
---

# 🥽 **gztarchiver — Automated Gazette Archiving Tool**

## 🧩 What is *gztarchiver*?

**gztarchiver** is an automated **Python-based library and command-line tool** designed to **extract, download, and archive official gazettes** from the Sri Lankan government’s **[documents.gov.lk](https://documents.gov.lk/)** website.  

It simplifies the process of maintaining a well-organized, up-to-date archive of gazettes by handling downloading, validation, and cloud backup operations — all through a single configurable tool.

---

## 💡 Why Use gztarchiver?

Manually collecting gazettes from official resources can be time-consuming, error-prone, and repetitive. **gztarchiver** automates this entire process, providing:

- 🧠 **Intelligent automation** — runs daily without manual intervention  
- 🧩 **Flexible configuration** — manage everything via a simple YAML file  
- 📊 **Reliable logging** — track successful and failed downloads  
- 📟 **Flag documents** — flag documents using LLM 
- 🛠️ **Resume support** — continue downloads from where you left off  
- 🧾 **Organized structure** — files stored by year, month, and date for easy access  

Whether you’re a researcher, data archivist, or government organization, gztarchiver ensures **no gazette is ever missed**.

---

## ⚙️ Technologies Used

| Technology | Purpose |
|-------------|----------|
| **Python** | Core programming language for the entire tool |
| **Scrapy** | Web scraping framework used to extract gazette metadata and links from the resource website |
| **DeepSeek** | Used for intelligent classification and data processing of extracted gazettes |
| **YAML Configuration** | Provides customizable options for runtime behavior and file paths |

---

## 🌐 Resource Website

All gazette data is scraped and archived from the **official Sri Lankan Government Gazette Portal**:

> 🔗 **[https://documents.gov.lk/](https://documents.gov.lk/)**  
> This is the official source of all public gazette publications in English, Sinhala, and Tamil.

---

## 🕗 Daily Execution Schedule

The **gztarchiver** tool is configured to **run automatically every day at 20:00 (8:00 PM)** local time.  
During this scheduled run, it:

1. Checks for new gazettes published that day  
2. Downloads all available files in all supported languages  
3. Validates the downloaded PDFs  
4. Flag documents using deepseek LLM
5. Updates the metadata and log files  
6. Syncs results to the configured archive  

This ensures the archive remains **fresh and synchronized daily**.

---

## 🧾 Summary

| Category | Description |
|-----------|--------------|
| **Tool Name** | gztarchiver |
| **Purpose** | Automate gazette extraction and archiving |
| **Language** | Python |
| **Frameworks** | [Scrapy](https://www.scrapy.org/), [DeepSeek](https://deepseek.ai/), [WSO2 Bijira](https://wso2.com/bijira/) |
| **Data Source** | [documents.gov.lk](https://documents.gov.lk/) |
| **Execution Time** | Daily at 20:00 |
| **Status** | Under active development 🚧 |

---
> Automating the way Sri Lanka archives its history.


