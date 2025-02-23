from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import shutil # shutil is a built-in Python module that provides file operations like copying, moving, renaming, and deleting files or directories. It's useful in Robocorp automation when handling file management tasks.
import os  # Added for directory handling


'''
    The @task decorator in Robocorp marks a function as the main entry point for a robotic process automation (RPA) task.
    It tells the Robocorp framework to execute that function when the robot runs. 
    In this case, order_robot_from_RobotSpareBin is the primary task that orchestrates the robot ordering process.
'''
@task
def order_robot_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc with the following steps:
    1. Opens the robot order website.
    2. Downloads the orders CSV file.
    3. Fills and submits orders from the CSV data.
    4. Saves each order receipt as a PDF with an embedded robot screenshot.
    5. Archives all receipts into a ZIP file.
    6. Cleans up temporary directories.
    """
    # Configure browser with a slight delay for visibility
    browser.configure(slowmo=200)
    
    # Step-by-step execution
    open_robot_order_website()
    download_orders_file()
    fill_form_with_csv_data()
    archive_receipts()
    clean_up()

def open_robot_order_website():
    """
    Opens the robot order website and dismisses the initial popup.
    Steps:
    1. Navigate to the robot order page.
    2. Click the 'OK' button to close the modal.
    """
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()
    page.click('text=OK')  # Dismisses the annoying startup modal

def download_orders_file():
    """
    Downloads the orders CSV file from the provided URL.
    Steps:
    1. Initialize HTTP client.
    2. Download the file, overwriting any existing local copy.
    """
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)

def order_another_bot():
    """
    Clicks the 'Order another' button to start a new order.
    """
    page = browser.page()
    page.click("#order-another")

def click_ok_after_order():
    """
    Clicks 'OK' on the popup after ordering another robot.
    """
    page = browser.page()
    page.click('text=OK')

def fill_and_submit_robot_data(order):
    """
    Fills and submits the robot order form based on CSV data.
    Steps:
    1. Map head number to head name and select it.
    2. Select the body part using dynamic XPath.
    3. Fill in legs and address fields.
    4. Submit the order and handle receipt/screenshot.
    Args:
        order (dict): A row from the CSV with keys like 'Head', 'Body', 'Legs', 'Address', 'Order number'.
    """
    page = browser.page()
    
    # Dictionary to map head numbers to names
    head_options = {
        "1": "Roll-a-thor head",
        "2": "Peanut crusher head",
        "3": "D.A.V.E head",
        "4": "Andy Roid head",
        "5": "Spanner mate head",
        "6": "Drillbit 2000 head"
    }
    
    # Fill the form
    head_number = order["Head"]
    page.select_option("#head", head_options.get(head_number, head_options["1"]))  # Default to 1 if invalid
    page.click(f'//*[@id="root"]/div/div[1]/div/div[1]/form/div[2]/div/div[{order["Body"]}]/label')
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", order["Address"])
    
    # Submit and verify success with retry logic
    while True:
        page.click("#order")
        order_another = page.query_selector("#order-another")
        if order_another:  # If button appears, order was successful
            pdf_path = store_receipt_as_pdf(int(order["Order number"]))
            screenshot_path = screenshot_robot(int(order["Order number"]))
            embed_screenshot_to_receipt(screenshot_path, pdf_path)
            order_another_bot()
            click_ok_after_order()
            break
        # Implicitly retries if order fails (no explicit error check, just loops until success)

def store_receipt_as_pdf(order_number):
    """
    Saves the order receipt as a PDF file.
    Steps:
    1. Extract receipt HTML from the page.
    2. Convert HTML to PDF and save it in the output/receipts directory.
    Args:
        order_number (int): Unique order number for naming the file.
    Returns:
        str: Path to the saved PDF file.
    """
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    receipts_dir = "output/receipts"
    os.makedirs(receipts_dir, exist_ok=True)  # Ensure directory exists
    pdf_path = f"{receipts_dir}/{order_number}.pdf"
    pdf.html_to_pdf(receipt_html, pdf_path)
    return pdf_path

def fill_form_with_csv_data():
    """
    Reads the CSV file and processes each order.
    Steps:
    1. Load CSV into a table.
    2. Iterate over each row and fill/submit the form.
    """
    tables = Tables()
    robot_orders = tables.read_table_from_csv("orders.csv")
    for order in robot_orders:
        fill_and_submit_robot_data(order)

def screenshot_robot(order_number):
    """
    Takes a screenshot of the robot preview image.
    Steps:
    1. Locate the robot preview image.
    2. Save the screenshot in the output/screenshots directory.
    Args:
        order_number (int): Unique order number for naming the file.
    Returns:
        str: Path to the saved screenshot.
    """
    page = browser.page()
    screenshots_dir = "output/screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)  # Ensure directory exists
    screenshot_path = f"{screenshots_dir}/{order_number}.png"
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot_path, pdf_path):
    """
    Embeds the robot screenshot into the receipt PDF.
    Steps:
    1. Use the PDF library to add the screenshot as a watermark.
    Args:
        screenshot_path (str): Path to the screenshot file.
        pdf_path (str): Path to the PDF file to modify.
    """
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot_path, 
                                   source_path=pdf_path, 
                                   output_path=pdf_path)

def archive_receipts():
    """
    Creates a ZIP archive of all receipt PDFs.
    Steps:
    1. Use the Archive library to zip the receipts folder.
    """
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")

def clean_up():
    """
    Removes temporary directories after archiving.
    Steps:
    1. Delete receipts and screenshots directories.
    """
    try:
        shutil.rmtree("./output/receipts")
        shutil.rmtree("./output/screenshots")
    except FileNotFoundError:
        pass  # Ignore if directories don't exist

"""
Library and Class Documentation for Robot Order Automation Script
================================================================

1. robocorp.tasks
-----------------
- Purpose: Provides the `@task` decorator to define the main entry point of an RPA task.
- Usage: Marks a function (e.g., `order_robot_from_RobotSpareBin`) as the robot's primary task.
- Parameters: None directly; applied as a decorator above a function.
- Example: `@task def my_task(): ...`
- Additional Useful Method: None (decorator-focused module).

2. robocorp.browser
-------------------
- Purpose: Controls web browsers for automation (e.g., navigating pages, clicking elements).
- Key Class: Implicit browser control (no explicit class instantiation).
- Methods:
  - `configure(slowmo=int)`: Sets a delay (ms) between actions for visibility/debugging.
    - Params: `slowmo` (int, optional) - Delay in milliseconds (e.g., 200).
  - `goto(url)`: Navigates to a specified URL.
    - Params: `url` (str) - Target URL (e.g., "https://example.com").
  - `page()`: Returns the current page object for interaction.
    - Returns: Page object with methods like `click()`, `fill()`, etc.
- Page Object Methods:
  - `click(selector)`: Clicks an element by locator (CSS, XPath, text).
    - Params: `selector` (str) - Locator (e.g., "#id", "text=OK").
  - `fill(selector, value)`: Enters text into an input field.
    - Params: `selector` (str), `value` (str) - e.g., "#address", "123 Main St".
  - `select_option(selector, value)`: Selects an option in a dropdown.
    - Params: `selector` (str), `value` (str) - e.g., "#head", "Roll-a-thor head".
  - `query_selector(selector)`: Checks if an element exists.
    - Params: `selector` (str) - Returns element or None.
  - `locator(selector)`: Creates a locator for advanced interactions (e.g., screenshot).
    - Params: `selector` (str) - Returns Locator object.
- Additional Useful Method:
  - `wait_for_selector(selector, timeout=int)`: Waits for an element to appear.
    - Params: `selector` (str), `timeout` (int, ms) - e.g., "text=OK", 5000.

3. RPA.HTTP
-----------
- Purpose: Handles HTTP requests, primarily for downloading files.
- Key Class: `HTTP()`
- Methods:
  - `download(url, target_file=None, overwrite=False)`: Downloads a file from a URL.
    - Params:
      - `url` (str) - Source URL (e.g., "https://robotsparebinindustries.com/orders.csv").
      - `target_file` (str, optional) - Local file path (defaults to filename from URL).
      - `overwrite` (bool) - Overwrite existing file if True (e.g., True).
    - Returns: Path to downloaded file if `target_file` is specified.
- Additional Useful Method:
  - `get(url)`: Performs a simple GET request for text/data.
    - Params: `url` (str) - Returns response content.

4. RPA.Tables
-------------
- Purpose: Reads and manipulates tabular data (e.g., CSV files).
- Key Class: `Tables()`
- Methods:
  - `read_table_from_csv(file_path, header=True)`: Reads a CSV into a table object.
    - Params:
      - `file_path` (str) - Path to CSV (e.g., "orders.csv").
      - `header` (bool) - Treats first row as headers if True (default).
    - Returns: Table object ( iterable rows as dicts with column names as keys).
- Additional Useful Method:
  - `write_table_to_csv(table, file_path)`: Writes a table back to a CSV.
    - Params: `table` (Table), `file_path` (str).

5. RPA.PDF
----------
- Purpose: Creates and manipulates PDF files (e.g., receipts, embedding images).
- Key Class: `PDF()`
- Methods:
  - `html_to_pdf(html, output_path)`: Converts HTML to a PDF file.
    - Params:
      - `html` (str) - HTML content (e.g., receipt HTML).
      - `output_path` (str) - File path (e.g., "output/receipts/1.pdf").
  - `add_watermark_image_to_pdf(image_path, source_path, output_path)`: Embeds an image into a PDF.
    - Params:
      - `image_path` (str) - Path to image (e.g., "output/screenshots/1.png").
      - `source_path` (str) - Input PDF path.
      - `output_path` (str) - Output PDF path (can overwrite source).
- Additional Useful Method:
  - `add_files_to_pdf(files, output_path)`: Combines multiple PDFs into one.
    - Params: `files` (list of str) - Paths to PDFs, `output_path` (str).

6. RPA.Archive
--------------
- Purpose: Creates and manages ZIP archives.
- Key Class: `Archive()`
- Methods:
  - `archive_folder_with_zip(folder_path, archive_name)`: Zips a folder into a ZIP file.
    - Params:
      - `folder_path` (str) - Folder to archive (e.g., "./output/receipts").
      - `archive_name` (str) - Output ZIP path (e.g., "./output/receipts.zip").
- Additional Useful Method:
  - `extract_archive(archive_name, target_folder)`: Unzips an archive.
    - Params: `archive_name` (str), `target_folder` (str).

7. shutil (Standard Python Library)
-----------------------------------
- Purpose: Provides high-level file operations (e.g., deleting directories).
- Key Methods:
  - `rmtree(path)`: Recursively deletes a directory and its contents.
    - Params: `path` (str) - Directory path (e.g., "./output/receipts").
    - Note: Raises FileNotFoundError if path doesn’t exist unless wrapped in try-except.
- Additional Useful Method:
  - `copy(src, dst)`: Copies a file from source to destination.
    - Params: `src` (str), `dst` (str) - e.g., "file.txt", "backup/file.txt".

8. os (Standard Python Library)
-------------------------------
- Purpose: Interacts with the operating system (e.g., file/directory management).
- Key Methods:
  - `makedirs(path, exist_ok=False)`: Creates directories recursively.
    - Params:
      - `path` (str) - Directory path (e.g., "output/receipts").
      - `exist_ok` (bool) - If True, doesn’t raise error if directory exists.
- Additional Useful Method:
  - `path.exists(path)`: Checks if a file or directory exists.
    - Params: `path` (str) - Returns bool.

Notes:
------
- These libraries/classes are part of the Robocorp ecosystem (except `shutil` and `os`), designed for RPA tasks.
- Additional methods can enhance functionality (e.g., waiting for elements, combining PDFs).
- Parameters are often optional with sensible defaults; check library docs for full details.
"""