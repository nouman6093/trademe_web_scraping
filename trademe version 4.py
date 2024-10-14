#combined bidbud + trademe 2 softwares into 1 single software
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from openpyxl import load_workbook
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup Chrome options for headless execution
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Function to get all product links from a TradeMe store
def get_all_product_links(store_url):
    product_links = []
    page_number = 1

    while True:
        if page_number == 1:
            current_page_url = store_url
        else:
            current_page_url = f"{store_url}&page={page_number}"

        print(f"Accessing: {current_page_url}")
        driver.get(current_page_url)

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.tm-marketplace-search-card__detail-section--link"))
            )
            product_elements = driver.find_elements(By.CSS_SELECTOR, "a.tm-marketplace-search-card__detail-section--link")
            print(f"Found {len(product_elements)} products on page {page_number}.")

            if len(product_elements) == 0:
                print("No more products found, ending.")
                break

            for elem in product_elements:
                product_url = elem.get_attribute('href')
                product_links.append(product_url)

            next_button = driver.find_elements(By.CSS_SELECTOR, 'a[rel="nofollow"][aria-label*="Next page"]')
            if next_button:
                page_number += 1
            else:
                break

        except Exception as e:
            print(f"Error extracting product links: {e}")
            break

    print(f"Total product links found: {len(product_links)}")
    return product_links

# Function to get product information from TradeMe
def get_product_info(url):
    driver.get(url)
    time.sleep(10)

    try:
        title = driver.find_element(By.CLASS_NAME, 'tm-marketplace-buyer-options__listing_title').text.strip()
    except:
        title = 'N/A'

    try:
        listing_number_divs = driver.find_elements(By.CLASS_NAME, 'tm-share-listing-link__info-block')
        listing_number = 'N/A'
        for div in listing_number_divs:
            text = div.text.strip()
            if 'Listing #' in text:
                listing_number = text.split('Listing #')[-1].strip()
                break
    except Exception as e:
        print(f"Error finding listing number: {e}")
        listing_number = 'N/A'

    try:
        script = driver.find_element(By.ID, 'frend-state').get_attribute('innerHTML')
        start_index = script.find('"sKU":"') + len('"sKU":"')
        end_index = script.find('"', start_index)
        sku = script[start_index:end_index]
    except:
        sku = 'N/A'

    try:
        breadcrumbs = driver.find_elements(By.CLASS_NAME, 'o-breadcrumbs__item')
        category = ' > '.join([crumb.text.strip() for crumb in breadcrumbs if crumb.text.strip()])
    except Exception as e:
        print(f"Error finding category: {e}")
        category = 'N/A'

    try:
        description_element = driver.find_element(By.CLASS_NAME, 'tm-markdown')
        description = description_element.text.strip()
    except:
        description = 'N/A'

    try:
        price_element = driver.find_element(By.CSS_SELECTOR, '.tm-buy-now-box__price strong')
        price = price_element.text.strip()
    except:
        price = 'N/A'

    try:
        quantity_element = driver.find_element(By.CSS_SELECTOR, 'input[name="quantity"]').get_attribute("value")
        quantity = quantity_element if quantity_element else 'N/A'
    except:
        quantity = 'N/A'

    try:
        available_element = driver.find_element(By.CSS_SELECTOR, 'input[name="quantityRemaining"]').get_attribute("value")
        available = available_element if available_element else 'N/A'
    except:
        available = 'N/A'

    images = []
    for i in range(1, 6):
        try:
            image_element = driver.find_element(By.CSS_SELECTOR, f'.tm-marketplace-listing-photos__thumbnail-slider-item:nth-child({i}) .o-aspect-ratio')
            image_url = image_element.get_attribute('style')
            start_index = image_url.find('url("') + len('url("')
            end_index = image_url.find('")', start_index)
            image_url = image_url[start_index:end_index]
            images.append(image_url)
        except:
            images.append('N/A')

    images += ['N/A'] * (5 - len(images))

    try:
        details_element = driver.find_element(By.CSS_SELECTOR, '.o-rack-item__secondary')
        details = details_element.text.strip()
    except:
        details = 'N/A'

    try:
        shipping_elements = driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
        shipping_data = []
        for row in shipping_elements:
            cols = row.find_elements(By.TAG_NAME, 'td')
            if len(cols) >= 2:
                shipping_info = f"{cols[0].text.strip()}\t{cols[1].text.strip()}"
                shipping_data.append(shipping_info)
        shipping = '\n'.join(shipping_data) if shipping_data else 'N/A'
    except:
        shipping = 'N/A'

    try:
        page_views_element = driver.find_element(By.CSS_SELECTOR, '.tm-share-listing-link__info-block b')
        page_views = page_views_element.text.strip()
    except:
        page_views = 'N/A'

    data = {
        "Link": url,
        "Listing Number": listing_number,
        "SKU": sku,
        "Category": category,
        "Product Title": title,
        "Selling Price": price,
        "Quantity": quantity,
        "Available": available,
        "Main Image": images[0],
        "Image #2": images[1],
        "Image #3": images[2],
        "Image #4": images[3],
        "Image #5": images[4],
        "Details": details,
        "Description": description,
        "Shipping": shipping,
        "Page Views": page_views,
    }

    return data

# Function to save data to an Excel file
def save_to_excel(all_data, filename="trademe_and_bidbud_scraped_file.xlsx"):
    file_path = os.path.join("/content/", filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    df = pd.DataFrame(all_data)

    try:
        df.to_excel(file_path, index=False, header=True)
        print(f"File saved at: {file_path}")
    except Exception as e:
        print(f"Error saving Excel file: {e}")

# Function to scrape BidBud feedback data
def scrape_bidbud_feedback(driver):
    feedback_data = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    counter = 1

    while True:
        rows = driver.find_elements(By.CSS_SELECTOR, 'table#feedback_table tr')
        for row in rows:
            try:
                username = row.find_element(By.CSS_SELECTOR, 'a[title="View member\'s listings"]').text.strip()
                listing_number_tag = row.find_element(By.CSS_SELECTOR, 'td.nowrap.hidden-xs a')
                listing_number = listing_number_tag.text.strip() if listing_number_tag else "N/A"
                date = row.find_element(By.CSS_SELECTOR, 'td.align-right').text.strip()
                feedback = row.find_element(By.CSS_SELECTOR, 'td.wordwrap').text.strip()

                feedback_data.append([username, listing_number, date, feedback])
                print(f"{counter}) Scraped: {username}, {listing_number}, {date}, {feedback}")
                counter += 1
            except Exception as e:
                continue

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    return feedback_data

# Main function
def main():
    trademe_store_url = input("Enter the TradeMe store URL: ").strip()
    bidbud_store_url = input("Enter the BidBud feedback section URL (must end with '/selling'): ").strip()

    if "page=" in trademe_store_url:
        trademe_store_url = trademe_store_url.split("?")[0]  # Get the main page URL

    print(f"Processing TradeMe store: {trademe_store_url}")

    # Get TradeMe product links and information
    product_links = get_all_product_links(trademe_store_url)
    print(f"Total products found on TradeMe: {len(product_links)}")

    trademe_data = []
    for idx, link in enumerate(product_links, start=1):
        try:
            product_data = get_product_info(link)
            trademe_data.append(product_data)
            print(f"Successfully processed data for TradeMe product: {link} [{idx}/{len(product_links)}]")
        except Exception as e:
            print(f"An error occurred with TradeMe product URL {link}: {e}")

    # Save TradeMe data to a separate Excel file
    save_to_excel(trademe_data, "trademe.xlsx")

    print(f"\nProcessing BidBud feedback section: {bidbud_store_url}")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(bidbud_store_url)
    feedback_data = scrape_bidbud_feedback(driver)

    # Save BidBud data to a separate Excel file
    save_to_excel(feedback_data, "bidbud.xlsx")

    driver.quit()

if __name__ == "__main__":
    main()
