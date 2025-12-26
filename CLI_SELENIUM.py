from selenium.webdriver.common.by import By 
import undetected_chromedriver as uc 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import time
import matplotlib.pyplot as plt
import base64
import whisper


chrome_options = uc.ChromeOptions()
driver = uc.Chrome(options=chrome_options)

driver.get('https://ccms.pitc.com.pk/complaint')

# Load the model (small is a good balance for CPU)
model = whisper.load_model("small")
# Path to your audio file
audio_path = "numbers.ogg"  # can be .wav, .mp3, .ogg, etc.
# Transcribe the audio
result = model.transcribe(audio_path, task="transcribe")  # use task="translate" to get English
# Print the detected language
print("Detected language:", result["language"])
# Print the transcription
client_no = result['text'].replace(",","").replace(" ","")
print(client_no)

input_number = driver.find_element(By.ID,value="identity")
input_number.clear()
input_number.send_keys(client_no)

drop_down_contact_no = driver.find_element(By.ID,value="search_type")
select = Select(drop_down_contact_no)
select.select_by_visible_text("Contact No")

search_button = driver.find_element(By.ID,value="search")
search_button.click()
time.sleep(10)

account_select = driver.find_element(By.ID,value='accounts')
select = Select(account_select)    
all_options = select.options
print("\nAvailable Accounts:")
for index, option in enumerate(all_options):
    print(f"{index}. {option.text}")


choice = int(input("\nSelect account number: "))

selected_option = all_options[choice]
select.select_by_visible_text(selected_option.text)
time.sleep(10)
ref_no = driver.find_element(By.CLASS_NAME,value="refno")
reference_no = ref_no.text

container = driver.find_element(By.ID, "ConsumerInfo")
table = container.find_element(By.TAG_NAME, "table")
rows = table.find_elements(By.TAG_NAME, "tr")

data = {}

for row in rows:
    cols = row.find_elements(By.TAG_NAME, "td")
    
    # only process rows with 2 cells
    if len(cols) == 2:
        key = cols[0].text.strip()
        value = cols[1].text.strip()
        data[key] = value
for k, v in data.items():
    print(f"{k}: {v}")

billing_button = driver.find_element(By.ID,value="billing-details")
billing_button.click()
time.sleep(10)

billing_details = driver.find_element(By.ID,value="BillingDetails")
billing_table = billing_details.find_element(By.TAG_NAME,"table")
b_rows = billing_table.find_elements(By.TAG_NAME,"tr")
billing_data = []

for row in b_rows:
    cols = row.find_elements(By.TAG_NAME, "td")
    row_values = [col.text.strip() for col in cols]
    if row_values:  # skip empty rows
        billing_data.append(row_values)
for r in billing_data:
    print(r)

duplicate_bill = driver.find_element(By.XPATH, "//button[contains(text(),'Duplicate Bill')]")
original_window = driver.current_window_handle
old_windows = set(driver.window_handles)

print("Before:", driver.window_handles)
duplicate_bill.click()

# Wait for a new window to appear
WebDriverWait(driver, 10).until(
    EC.number_of_windows_to_be(len(old_windows)+ 1)
)

# Get the new window handle
new_windows = set(driver.window_handles) - old_windows
new_window = new_windows.pop()
print("New window:", new_window)

# Switch to the new window
driver.switch_to.window(new_window)

# Now you're in the new window
print("Current window after switch:", driver.current_window_handle)

time.sleep(5)
search_bill = driver.find_element(By.ID,value="searchTextBox")
search_bill.clear()
search_bill.send_keys(reference_no)

search_button = driver.find_element(By.NAME,value="btnSearch")
search_button.click()
time.sleep(10)

pdf = driver.execute_cdp_cmd("Page.printToPDF", {
    "printBackground": True,
    "paperWidth": 8.27,    # A4 width in inches (8.27in) or adjust as needed
    "paperHeight": 11.69,  # A4 height in inches (11.69in) or adjust
    "marginTop": 0,
    "marginBottom": 0,
    "marginLeft": 0,
    "marginRight": 0,
    "scale": 0.6           # Scale down content to fit on one page (0.1 to 2.0)
})

with open("duplicate_bill.pdf", "wb") as f:
    f.write(base64.b64decode(pdf['data']))

