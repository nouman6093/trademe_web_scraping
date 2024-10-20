import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pandas import ExcelWriter
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def get_text(driver, by, selector):
    try:
        element = driver.find_element(by, selector)
        if element:
            return element.text.strip() if element.text.strip() else 'N/A'
    except Exception as e:
        print(f"Error getting text from selector {selector}: {e}")
    return 'N/A'

def get_input_value(driver, name):
    try:
        return driver.find_element(By.CSS_SELECTOR, f'input[name="{name}"]').get_attribute("value")
    except:
        return 'N/A'

def get_listing_number(driver):
    try:
        listing_info = driver.find_element(By.CSS_SELECTOR, 'tm-listing-id-views span:nth-child(2)')
        text = listing_info.text.strip()
        if 'Listing #' in text:
            return text.split('Listing #')[-1].strip()
    except Exception:
        pass
    return 'N/A'

def get_sku(driver):
    try:
        script = driver.find_element(By.ID, 'frend-state').get_attribute('innerHTML')
        start_index = script.find('"sKU":"') + len('"sKU":"')
        end_index = script.find('"', start_index)
        return script[start_index:end_index]
    except:
        return 'N/A'

def get_price(driver):
    try:
        script = driver.find_element(By.ID, 'frend-state').get_attribute('innerHTML')
        start_index = script.find('"priceDisplay":"') + len('"priceDisplay":"')
        end_index = script.find(' per', start_index)
        price = script[start_index:end_index].strip()

        if not price or price.startswith('b{"'):
            return 'N/A'

        return price
    except Exception as e:
        print(f"Error extracting price: {e}")
        return 'N/A'

def get_quantity(driver):
    try:
        script = driver.find_element(By.ID, 'frend-state').get_attribute('innerHTML')
        start_index = script.find('"quantityRemaining":') + len('"quantityRemaining":')
        end_index = script.find(',', start_index)
        quantity = script[start_index:end_index].strip()
        return quantity
    except Exception as e:
        print(f"Error extracting quantity: {e}")
        return 'N/A'

def get_available(driver):
    try:
        script = driver.find_element(By.ID, 'frend-state').get_attribute('innerHTML')
        start_index = script.find('"availableToBuy":"') + len('"availableToBuy":"')
        end_index = script.find('"', start_index)
        available = script[start_index:end_index].strip()
        return available
    except Exception as e:
        print(f"Error extracting available: {e}")
        return 'N/A'

def get_category_with_bs(driver):
    try:
        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')

        breadcrumbs = soup.find_all('li', class_='o-breadcrumbs__item')

        category = ' > '.join([crumb.get_text(strip=True) for crumb in breadcrumbs if crumb.get_text(strip=True)])

        return category if category else 'N/A'
    except Exception as e:
        print(f"Error finding category with BeautifulSoup: {e}")
        return 'N/A'

def get_product_title(driver):
    try:
        title_element = driver.find_element(By.CSS_SELECTOR, 'h1.tm-motors-listing__title')
        return title_element.text.strip()
    except Exception as e:
        print(f"Error extracting product title: {e}")
        return 'N/A'


def get_images(driver):
    try:
        image_elements = driver.find_elements(By.CSS_SELECTOR, 'div.tm-gallery-thumbnail-slider__item img')

        images = [img.get_attribute('src') for img in image_elements[:5]]
        return images + ['N/A'] * (5 - len(images))
    except Exception as e:
        print(f"Error extracting images: {e}")
        return ['N/A'] * 5

def get_shipping(driver):
    try:
        shipping_elements = driver.find_elements(By.CSS_SELECTOR, 'table.o-table tbody tr')
        shipping_data = []
        for row in shipping_elements:
            destination_description = row.find_element(By.CSS_SELECTOR, 'td:nth-child(1)').text.strip()
            price = row.find_element(By.CSS_SELECTOR, 'td.h-text-align-right').text.strip()
            shipping_info = f"{destination_description}\t{price}"
            shipping_data.append(shipping_info)
        return '\n'.join(shipping_data) if shipping_data else 'N/A'
    except Exception as e:
        print(f"Error extracting shipping information: {e}")
        return 'N/A'

def get_full_description(driver):
    try:
        show_more_button = driver.find_elements(By.CSS_SELECTOR, 'button.tm-motors-listing-body__item-show-more-button')
        if show_more_button:
            show_more_button[0].click()
            time.sleep(1)

        description_element = driver.find_element(By.CSS_SELECTOR, 'div.tm-markdown')
        return description_element.text.strip()
    except Exception as e:
        print(f"Error extracting description: {e}")
        return 'N/A'

def get_page_views(driver):
    try:
        page_views_element = driver.find_element(By.CSS_SELECTOR, 'span.tm-listing-id-views__views strong')
        return page_views_element.text.strip()
    except Exception:
        pass
    return 'N/A'

def get_watchlist_count_with_bs4(driver):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    try:
        watch_list_element = soup.select_one('span.tm-motors-date-city-watchlist__watchlists strong')
        if watch_list_element:
            return watch_list_element.text.strip()
        else:
            return 'N/A'
    except Exception as e:
        print(f"Error scraping watchlist count: {e}")
        return 'N/A'

def get_product_info(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        category = get_category_with_bs(driver)
        product_data = {
            'Link': url,
            'Listing Number': get_listing_number(driver),
            'SKU': get_sku(driver),
            'Category': category,
            'Product Title': get_product_title(driver),
            'Price': get_price(driver),
            'Quantity': get_quantity(driver),
            'Available': get_available(driver),
            'Description': get_full_description(driver),
            'Main Image': get_images(driver)[0],
            'Image #2': get_images(driver)[1],
            'Image #3': get_images(driver)[2],
            'Image #4': get_images(driver)[3],
            'Image #5': get_images(driver)[4],
            'Details': get_text(driver, By.CSS_SELECTOR, 'tg-rack-item-secondary.o-rack-item__secondary'),
            'Shipping': get_shipping(driver),
            'Page Views': get_page_views(driver),
            'Watchlist': get_watchlist_count_with_bs4(driver),
        }
        return product_data
    except Exception as e:
        print(f"Error getting product info: {e}")
        return None

def save_to_excel(data, filename):
    file_path = os.path.join("/content/", filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df = pd.DataFrame(data)
    if filename == "BidBud.xlsx":
        df.columns = ["Username", "Listing Number", "Sold Date", "FeedBack"]
    df.to_excel(file_path, index=False)
    print(f"Data saved to {file_path}")


def scrape_bidbud_feedback(driver):
    feedback_data = []
    listing_numbers = []
    counter = 1
    last_row_count = 0

    total_feedback_str = driver.find_element(By.CSS_SELECTOR, 'div.col-sm-3 p b:nth-of-type(2)').text
    total_feedback = int(total_feedback_str.replace(',', ''))

    while True:
        rows = driver.find_elements(By.CSS_SELECTOR, 'table#feedback_table tr')

        for row in rows[last_row_count:]:
            try:
                username = row.find_element(By.CSS_SELECTOR, 'a[title="View member\'s listings"]').text.strip()

                listing_number_tag = row.find_element(By.CSS_SELECTOR, 'td.nowrap.hidden-xs a')
                listing_number = listing_number_tag.text.strip() if listing_number_tag else "N/A"
                listing_numbers.append(listing_number)

                date = row.find_element(By.CSS_SELECTOR, 'td.align-right').text.strip()
                feedback = row.find_element(By.CSS_SELECTOR, 'td.wordwrap').text.strip()

                feedback_data.append([username, listing_number, date, feedback])
                print(f"{counter}) Scraped: {username}, {listing_number}, {date}, {feedback}")
                counter += 1

                if counter > total_feedback:
                    return feedback_data, listing_numbers

            except NoSuchElementException:
                continue

        last_row_count = len(rows)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        try:
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, 'table#feedback_table tr')) > last_row_count
            )
        except TimeoutException:
            print("No more new feedback loaded.")
            break

        time.sleep(5)

    return feedback_data, listing_numbers


def run_scraper():
    link = input("Enter link of feedback section of a store from BidBud (must end with '/selling'): ")
    trademe_base_link = "https://www.trademe.co.nz/a/motors/trucks/parts-accessories/listing/"
    if not link.endswith('/selling'):
        print("Error: The link must end with '/selling'. Please provide the correct link.")
        return

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(link)

    feedback_data, listing_numbers = scrape_bidbud_feedback(driver)
    save_to_excel(feedback_data, "BidBud.xlsx")

    trademe_links = [trademe_base_link + listing for listing in listing_numbers]
    print(f"All listing numbers added at the end of link: {trademe_base_link}")

    print("Now Starting to Scrape each link individually...")
    trademe_data = []
    total_products = len(trademe_links)
    for idx, link in enumerate(trademe_links, start=1):
        try:
            product_data = get_product_info(driver, link)
            trademe_data.append(product_data)
            print(f"Successfully Processed: {link} [{idx}/{total_products}]")

        except Exception as e:
            print(f"Error scraping product {link}: {e}")

    save_to_excel(trademe_data, "TradeMe.xlsx")
    driver.quit()


if __name__ == "__main__":
    run_scraper()
