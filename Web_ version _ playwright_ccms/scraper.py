# scraper.py
import os
from playwright.async_api import async_playwright
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

class AsyncPITCSession:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.accounts = None

    async def start(self, contact_no: str):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/143.0.0.0 Safari/537.36"
        )
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => false});
            window.chrome = { runtime: {}, app: {}, webstore: {} };
        """)
        self.page = await context.new_page()
        await self.page.goto("https://ccms.pitc.com.pk/complaint", wait_until="networkidle", timeout=60000)

        await self.page.wait_for_selector("input#identity", timeout=30000)
        await self.page.fill("input#identity", contact_no)
        await self.page.select_option("#search_type", label="Contact No")
        await self.page.click("#search")
        await self.page.wait_for_selector("#accounts", timeout=40000)
        await self.page.wait_for_timeout(8000)

        options = await self.page.query_selector_all("#accounts option")
        self.accounts = []
        for opt in options[1:]:
            text = await opt.text_content()
            text = text.strip()
            value = await opt.get_attribute("value")
            if text and value and "Select" not in text:
                ref = text.split()[0]
                self.accounts.append({"value": value, "text": text, "ref_no": ref})

    async def select_account(self, account_value: str):
        await self.page.select_option("#accounts", value=account_value)
        await self.page.wait_for_timeout(10000)

        ref_no = await self.page.locator(".refno").inner_text()
        ref_no = ref_no.strip()

        consumer_data = {}
        rows = await self.page.locator("#ConsumerInfo tr").all()
        for row in rows:
            cols = await row.locator("td").all()
            if len(cols) >= 2:
                key = await cols[0].inner_text()
                val = await cols[1].inner_text()
                key = key.strip().rstrip(":")
                val = val.strip()
                if key:
                    consumer_data[key] = val

        await self.page.click("#billing-details")
        await self.page.wait_for_timeout(10000)

        billing_data = []
        try:
            rows = await self.page.locator("#BillingDetails table tr").all()
            for row in rows:
                cells = await row.locator("td").all()
                row_text = [await c.inner_text() for c in cells]
                row_text = [t.strip() for t in row_text if t.strip()]
                if len(row_text) > 1:
                    billing_data.append(row_text)
        except:
            billing_data = [["No billing data"]]

        button_visible = await self.page.locator("button:has-text('Duplicate Bill')").is_visible()
        bill_status = "Available" if button_visible else "Already Generated"

        return {
            "reference_no": ref_no,
            "consumer_info": consumer_data,
            "billing_data": billing_data[:25],
            "recent_bill_status": bill_status
        }

    async def generate_bill(self, ref_no: str):
        try:
            await self.page.click("button:has-text('Duplicate Bill')")
            new_page = await self.page.context.wait_for_event("page", timeout=20000)

            await new_page.wait_for_selector("#searchTextBox", timeout=20000)
            await new_page.fill("#searchTextBox", ref_no)
            await new_page.click("input[name='btnSearch']")
            await new_page.wait_for_load_state("networkidle")
            await new_page.wait_for_timeout(8000)

            pdf_bytes = await new_page.pdf(scale=0.75, print_background=True, width="8.27in", height="11.69in")

            filename = f"bill_{ref_no}_{int(__import__('time').time())}.pdf"
            path = os.path.join("bills", filename)
            os.makedirs("bills", exist_ok=True)
            with open(path, "wb") as f:
                f.write(pdf_bytes)

            return {"success": True, "filename": filename}
        finally:
            await self.browser.close()
            await self.playwright.stop()


def generate_billing_graph(billing_data):
    """Parse billing_data and generate a nice consumption graph"""
    months = []
    amounts = []

    # Common month mapping
    month_map = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
    }

    # Parse rows like: ['Nov-24', '5,609.00'] or ['Bill Month', 'Nov 2025']
    for row in billing_data:
        if len(row) >= 2:
            key = row[0].strip()
            val = row[1].strip().replace(",", "")

            # Skip headers and non-month entries
            if "-" in key and len(key) == 7 and key[:3] in month_map:
                try:
                    amount = float(val)
                    # Convert "Nov-24" → "2024-11"
                    month_abbr, year_short = key.split("-")
                    year = "20" + year_short
                    month_num = month_map[month_abbr[:3]]
                    date_str = f"{year}-{month_num}"
                    months.append(date_str)
                    amounts.append(amount)
                except:
                    continue

    if not months:
        return None

    # Sort by date
    combined = sorted(zip(months, amounts))
    sorted_months, sorted_amounts = zip(*combined)

    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(sorted_months, sorted_amounts, marker='o', linewidth=3, markersize=8, color='#e63946')
    plt.fill_between(sorted_months, sorted_amounts, alpha=0.2, color='#e63946')
    plt.title("Monthly Bill Amount (PKR)", fontsize=18, fontweight='bold', color='#1d3557')
    plt.xlabel("Month", fontsize=12)
    plt.ylabel("Amount (PKR)", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return f"data:image/png;base64,{img_base64}"




