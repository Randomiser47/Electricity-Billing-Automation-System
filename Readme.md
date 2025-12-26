# PITC Complaint System Automation

Selenium-based automation script for extracting customer complaint data and generating duplicate bills from PITC's complaint portal.

## Overview

This script automates the process of:
1. Transcribing customer numbers from audio using Whisper
2. Querying the PITC complaint system
3. Extracting customer and billing information
4. Generating duplicate bill PDFs

## Prerequisites

### Python Packages
```bash
pip install undetected-chromedriver selenium whisper matplotlib
```

# PITC Automation Script Documentation

## Additional Requirements
- Chrome/Chromium browser
- Whisper model files (automatically downloaded on first run)

## Core Functionality

### 1. Audio Transcription
- Uses Whisper's small model
- Supports `.wav`, `.mp3`, `.ogg` formats
- Extracts and cleans customer numbers

### 2. Web Automation
- Undetected ChromeDriver bypasses detection
- Multi-window handling for bill generation
- Dynamic element waiting with explicit waits

### 3. Data Extraction
- Customer information from consumer info table
- Billing history from billing details
- Reference number for bill lookup

### 4. PDF Generation
- Uses Chrome DevTools Protocol
- Custom page sizing for A4 format
- Background printing enabled

## Usage Flow

```plaintext
1. Initialize driver and load Whisper model
2. Transcribe customer number from audio
3. Navigate to complaint portal
4. Search by contact number
5. Select account from dropdown
6. Extract customer information
7. Access billing details
8. Generate duplicate bill PDF
```
