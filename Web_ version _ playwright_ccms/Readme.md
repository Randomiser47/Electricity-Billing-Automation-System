# PITC Web Application Documentation (Async Version)

## Overview
This is an asynchronous web application built with **Quart** (async version of Flask) and **Playwright** for automating the PITC complaint portal. It allows users to:
- Search for accounts using a contact number
- View consumer information and billing history
- Visualize billing trends with a graph
- Generate and download duplicate bills as PDFs

The application runs as a web server and provides a RESTful API for frontend interaction.

## Project Structure
- `app.py`: Main Quart application with API routes
- `scraper.py`: Contains the `AsyncPITCSession` class using Playwright for browser automation and graph generation

## Requirements
- Python 3.8+
- Quart
- Hypercorn (ASGI server)
- Playwright
- Matplotlib
- Base64 (standard library)

Install dependencies:
```bash
pip install quart hypercorn playwright matplotlib
playwright install chromium
```
## Core Components

### app.py - Web Server & API

#### Key Features
- Asynchronous API endpoints
- Session management using in-memory dictionary (`active_sessions`)
- Serves static HTML frontend (`index.html`)
- Handles file downloads from the `bills/` directory
- Uses Hypercorn for async serving

#### API Endpoints

1. **GET /**  
   Serves the main frontend page (`index.html`)

2. **POST /search**  
   - Input: JSON `{ "contact_no": "03xxxxxxxxx" }`  
   - Starts a new Playwright session  
   - Searches accounts by contact number  
   - Returns session ID and list of available accounts

3. **POST /select_account**  
   - Input: JSON `{ "session_id": "...", "account_value": "..." }`  
   - Selects the specified account  
   - Extracts consumer info and billing history  
   - Generates a billing trend graph (base64 PNG)  
   - Returns detailed account data

4. **POST /generate_bill**  
   - Input: JSON `{ "session_id": "...", "reference_no": "..." }`  
   - Generates duplicate bill PDF using Playwright's PDF export  
   - Saves PDF to `bills/` folder  
   - Returns filename for download  
   - Closes browser and cleans up session

5. **GET /download/<filename>**  
   - Downloads the generated PDF bill

#### Server Startup

```python
hypercorn.asyncio.serve(app, config)
```
Binds to 0.0.0.0:5000 by default.

### scraper.py - Automation & Visualization

#### AsyncPITCSession Class
Handles all browser interactions using Playwright in headless mode.

##### Key Methods

1. **`start(contact_no)`**  
   - Launches Chromium with stealth options  
   - Navigates to PITC complaint portal  
   - Searches by contact number  
   - Extracts available account options with reference numbers

2. **`select_account(account_value)`**  
   - Selects account from dropdown  
   - Extracts reference number and consumer information table  
   - Fetches billing history  
   - Checks if duplicate bill is available  
   - Returns structured data

3. **`generate_bill(ref_no)`**  
   - Clicks "Duplicate Bill" button  
   - Handles new popup window  
   - Searches by reference number  
   - Generates A4-sized PDF with background  
   - Saves to `bills/` directory with timestamp  
   - Closes browser gracefully

##### Anti-Detection Features
- Custom user agent
- Viewport and window size emulation
- `navigator.webdriver` override
- Init script to mask automation flags
- Disabled sandbox flags

#### generate_billing_graph() Function
- Parses billing history table
- Extracts month-year and amount
- Converts short months (e.g., "Nov-24") to sortable format
- Creates a clean line + area chart using Matplotlib
- Returns base64-encoded PNG for inline display in browser

##### Graph Styling
- Red line with area fill (`#e63946`)
- Grid, bold title, rotated labels
- High DPI (150) for clarity
- Responsive sizing

#### Directory Management
- Automatically creates `bills/` folder for storing generated PDFs
- PDFs named as: `bill_{ref_no}_{timestamp}.pdf`

#### Security & Best Practices
- In-memory session management (no persistence)
- Sessions automatically cleaned after bill generation
- Headless mode enabled
- Proper resource cleanup in `finally` block
- File existence checks before serving downloads

#### Limitations
- In-memory sessions (lost on server restart)
- Single-user focused (no concurrent session isolation beyond object ID)
- No authentication
- Relies on current PITC website structure (may break on updates)

#### Future Enhancements
- Add user authentication
- Persistent session storage (Redis)
- Queue system for multiple requests
- Email delivery of bills
- Logging and monitoring
- Configurable selectors via config file
- Support for batch processing
- Improved error screenshots on failure

#### Running the Application
```bash
python app.py
```
