#added graphical user interface
import os
import sys
import re
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QLineEdit, QPushButton, QTextEdit, QMessageBox, QStackedWidget
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QIcon

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class ScraperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TradeMe & BidBud Scraper")
        self.setWindowIcon(QIcon('icons/favicon.png'))
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        # Setting up the main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Dark gray background
        self.setStyleSheet("background-color: #2e2e2e; color: white;")

        # Navbar setup
        self.navbar = QHBoxLayout()
        self.home_button = QPushButton("Home")
        self.instruction_button = QPushButton("Instruction")
        self.documentation_button = QPushButton("Documentation")
        self.contact_button = QPushButton("Contact")

        # Adding styles for navbar buttons (gray by default, white with black text on hover)
        self.set_button_styles(self.home_button)
        self.set_button_styles(self.instruction_button)
        self.set_button_styles(self.documentation_button)
        self.set_button_styles(self.contact_button)

        self.navbar.addWidget(self.home_button)
        self.navbar.addWidget(self.instruction_button)
        self.navbar.addWidget(self.documentation_button)
        self.navbar.addWidget(self.contact_button)
        self.layout.addLayout(self.navbar)

        # Stacked widget to switch between pages
        self.pages = QStackedWidget()
        self.layout.addWidget(self.pages)

        # Creating individual pages
        self.home_page = self.createHomePage()
        self.instruction_page = self.createInstructionPage()
        self.documentation_page = self.createDocumentationPage()
        self.contact_page = self.createContactPage()

        # Adding pages to the stacked widget
        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.instruction_page)
        self.pages.addWidget(self.documentation_page)
        self.pages.addWidget(self.contact_page)

        # Connecting navbar buttons to their corresponding pages
        self.home_button.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.instruction_button.clicked.connect(lambda: self.pages.setCurrentIndex(1))
        self.documentation_button.clicked.connect(lambda: self.pages.setCurrentIndex(2))
        self.contact_button.clicked.connect(lambda: self.pages.setCurrentIndex(3))

    def set_button_styles(self, button):
        # Gray background with hover effect (white background, black text)
        button.setStyleSheet("""
            QPushButton {
                background-color: #4f4f4f;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: white;
                color: black;
            }
        """)

    def createHomePage(self):
        home_page = QWidget()
        layout = QVBoxLayout(home_page)

        # Input fields for Home page
        self.trademe_label = QLabel("TradeMe Store URL:")
        self.trademe_input = QLineEdit()

        self.bidbud_label = QLabel("BidBud Feedback Section URL:")
        self.bidbud_input = QLineEdit()

        self.email_label = QLabel("Your Email:")
        self.email_input = QLineEdit()

        self.start_button = QPushButton("Start Scraping")
        self.start_button.clicked.connect(self.startScraping)
        
        # Start Scraping button style (dark blue with light blue on hover)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #003366;
                color: white;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #3399ff;
            }
        """)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)

        # Adding widgets to the layout
        layout.addWidget(self.trademe_label)
        layout.addWidget(self.trademe_input)
        layout.addWidget(self.bidbud_label)
        layout.addWidget(self.bidbud_input)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.start_button)
        layout.addWidget(self.log_text)

        return home_page

    def createInstructionPage(self):
        instruction_page = QWidget()
        layout = QVBoxLayout(instruction_page)

        font = QFont()
        font.setPointSize(12)
        font.setBold(True)

        instructions = QLabel(
            "<b>Instructions:</b><br>"
            "1) Trademe: On the Trademe website, go to the store you want to scrape. Scroll to the bottom; there will be pages (like 1 2 3 4 Next). Go to page 2, then go back to page 1. Paste this link of page 1 in this software.<br>"
            "2) Bidbud: Make sure you enter the link ending with /selling.<br>"
            "3) Email: Ensure you write the correct email.<br>"
            "4) File Location: Two files will be generated at the end. Both will be stored in the 'content' folder of the drive where you installed the software. If you can't find the files, search for 'content/bidbud' or 'content/trademe' on your PC.<br>"
            "5) Start Time: After clicking on the 'Start Scraping' button, the software will take 2 to 3 minutes to start.<br>"
            "6) New Scraping: Whenever you start a new scraping session, make sure to move previous files out of the content folder.<br>"
            "7) VPN: for good quality work and faster execution paid vpn is required.<br>"
        )

        instructions.setFont(font)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: white;")  # Text in white

        layout.addWidget(instructions)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(instructions, Qt.AlignTop)

        return instruction_page

    def createDocumentationPage(self):
        documentation_page = QWidget()
        layout = QVBoxLayout(documentation_page)

        font = QFont()
        font.setPointSize(12)
        font.setBold(True)

        doc_label = QLabel(
            "<b>Documentation:</b><br>"
            "1) Platform: This software is designed for Windows only. It will not work on macOS or any other platform.<br>"
            "2) Testing: The software was tested over 100 times after each step before delivery.<br>"
            "3) Summary of All Versions:<br>"
            "   - Version 1: Unlimited rows + cloud processing for faster execution.<br>"
            "   - Version 2: Added dynamic waiting at some points instead of fixed waiting.<br>"
            "   - Version 3: Removed unnecessary columns and console messages, and cleaned up the software.<br>"
            "   - Version 4: Combined two different software (Bidbud and Trademe) into a single software.<br>"
            "   - Version 5: Added email functionality.<br>"
            "   - Version 6: Added a graphical user interface.<br>"
            "4) Updates: The software extracts data based on the website's CSS. If the website's CSS is updated, some functionality may stop working. If this happens, the software needs to be updated.<br>"
            "5) Dependencies: How well this software works depends upon your internet connection, vpn quality, computer power.<br>"
        )

        doc_label.setFont(font)
        doc_label.setWordWrap(True)
        doc_label.setStyleSheet("color: white;")  # Text in white

        layout.addWidget(doc_label)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(doc_label, Qt.AlignTop)

        return documentation_page

    def createContactPage(self):
        contact_page = QWidget()
        layout = QVBoxLayout(contact_page)

        font = QFont()
        font.setPointSize(12)
        font.setBold(True)

        contact_label = QLabel(
            "<b>Contact Developer:</b><br>"
            "Phone: 0329-2555574 (No Calls Please)<br>"
            "Mail: <a href='mailto:hameednouman12@gmail.com'>hameednouman12@gmail.com</a><br>"
            "GitHub: <a href='https://github.com/nouman6093'>https://github.com/nouman6093</a><br>"
            "LinkedIn: <a href='https://www.linkedin.com/in/nouman6093/'>LinkedIn</a>"
        )

        contact_label.setFont(font)
        contact_label.setOpenExternalLinks(True)
        contact_label.setStyleSheet("color: white;")  # Links in white

        layout.addWidget(contact_label)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(contact_label, Qt.AlignTop)

        return contact_page

    def startScraping(self):
        trademe_url = self.trademe_input.text()
        bidbud_url = self.bidbud_input.text()
        user_email = self.email_input.text()

        if not self.validateInputs(trademe_url, bidbud_url, user_email):
            return

        # Check if the bidbud_url ends with "/selling"
        if not bidbud_url.endswith("/selling"):
            QMessageBox.warning(
                self,
                "Input Error",
                'The BidBud URL must end with "/selling". '
                'For example: "https://www.bidbud.co.nz/members/feedback/7535514/selling" is acceptable, '
                'but "https://www.bidbud.co.nz/members/feedback/7535514" is not.',
            )
            return

        self.thread = ScraperThread(trademe_url, bidbud_url, user_email)
        self.thread.progress_signal.connect(self.updateLog)
        self.thread.start()

    def validateInputs(self, trademe_url, bidbud_url, email):
        if not trademe_url or not bidbud_url or not email:
            QMessageBox.warning(self, "Input Error", "All fields must be filled.")
            return False
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Input Error", "Invalid email format.")
            return False
        return True

    def updateLog(self, message):
        self.log_text.append(message)
        # Limit the number of lines displayed
        max_lines = 1000
        if self.log_text.document().blockCount() > max_lines:
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.End)
            cursor.movePosition(cursor.Start, cursor.KeepAnchor, self.log_text.document().blockCount() - max_lines)
            cursor.removeSelectedText()
            cursor.deleteChar()
            self.log_text.setTextCursor(cursor)


class ScraperThread(QThread):
    progress_signal = pyqtSignal(str)

    def __init__(self, trademe_url, bidbud_url, user_email):
        super().__init__()
        self.trademe_url = trademe_url
        self.bidbud_url = bidbud_url
        self.user_email = user_email
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
        self.sender_email = "nouman6093@yahoo.com"
        self.sender_password = "akjpcjmqzqlogktq"

    def log(self, message):
        self.progress_signal.emit(message)

    def run(self):
        self.log(f"Processing TradeMe store: {self.trademe_url}")
        try:
            product_links = self.get_all_product_links(self.trademe_url)
            self.log(f"Total products found on TradeMe: {len(product_links)}")

            trademe_data = []
            for idx, link in enumerate(product_links, start=1):
                try:
                    product_data = self.get_product_info(link)
                    trademe_data.append(product_data)
                    self.log(f"Successfully processed data for TradeMe product: {link} [{idx}/{len(product_links)}]")
                except Exception as e:
                    self.log(f"An error occurred with TradeMe product URL {link}: {e}")

            self.save_to_excel(trademe_data, "trademe.xlsx")
            self.log("TradeMe data saved.")

            self.log("Processing BidBud feedback section...")
            feedback_data = self.scrape_bidbud_feedback()
            self.save_to_excel(feedback_data, "bidbud.xlsx")
            self.log("BidBud data saved.")
            self.log("Scraping complete.")

            self.send_email(
                self.user_email,
                "Scraping Done!",
                "Your Scraping for Trademe and Bidbud is done. Check your Computer."
            )
        finally:
            self.driver.quit()

    def send_email(self, to_email, subject, body):
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP("smtp.mail.yahoo.com", 587) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
                self.log("Email sent successfully!")
        except Exception as e:
            self.log(f"Error sending email: {e}")

    def get_all_product_links(self, store_url):
        product_links = []
        page_number = 1
        while True:
            current_page_url = f"{store_url}&page={page_number}" if page_number > 1 else store_url
            self.log(f"Accessing: {current_page_url}")
            self.driver.get(current_page_url)
            time.sleep(2)

            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.tm-marketplace-search-card__detail-section--link"))
                )
                product_elements = self.driver.find_elements(By.CSS_SELECTOR, "a.tm-marketplace-search-card__detail-section--link")
                if not product_elements:
                    self.log("No more products found.")
                    break

                self.log(f"Found {len(product_elements)} products on Page {page_number}.")
                product_links.extend([elem.get_attribute('href') for elem in product_elements])
                page_number += 1

            except Exception as e:
                if "no results found" in self.driver.page_source.lower():
                    self.log("No more Pages Found.")
                else:
                    self.log(f"Error extracting product links: {e}")
                break

        self.log(f"Total product links found: {len(product_links)}")
        return product_links

    def get_product_info(self, url):
        self.driver.get(url)
        time.sleep(10)

        try:
            title = self.get_text(By.CLASS_NAME, 'tm-marketplace-buyer-options__listing_title')
            listing_number = self.get_listing_number()
            sku = self.get_sku()
            category = self.get_category()
            description = self.get_text(By.CLASS_NAME, 'tm-markdown')
            price = self.get_text(By.CSS_SELECTOR, '.tm-buy-now-box__price strong')
            quantity = self.get_input_value('quantity')
            available = self.get_input_value('quantityRemaining')

            # Extract all 5 image URLs
            images = []
            for i in range(1, 6):
                images.append(self.get_image(i))

            details = self.get_text(By.CSS_SELECTOR, '.o-rack-item__secondary')
            shipping = self.get_shipping()
            watchlist = self.get_watchlist_count_with_bs4()
            page_views = self.get_text(By.CSS_SELECTOR, '.tm-share-listing-link__info-block b')
        except Exception as e:
            self.log(f"Error extracting product information from {url}: {e}")
            return {}

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
            "Watchlist": watchlist,
            "Page Views": page_views,
        }

        return data

    def get_watchlist_count_with_bs4(self):
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        try:
            watch_list_element = soup.select_one('p.tm-marketplace-buyer-options__watchers-count strong')
            return watch_list_element.text.strip() if watch_list_element else 'N/A'
        except Exception as e:
            self.log(f"Error scraping watchlist count: {e}")
            return 'N/A'

    def save_to_excel(self, all_data, filename):
        content_folder = os.path.join("D:\\content")
        os.makedirs(content_folder, exist_ok=True)
        file_path = os.path.join(content_folder, filename)
        df = pd.DataFrame(all_data)

        try:
            df.to_excel(file_path, index=False, header=True)
            self.log(f"File saved at: {file_path}")
        except Exception as e:
            self.log(f"Error saving Excel file: {e}")

    def scrape_bidbud_feedback(self):
        feedback_data = []
        self.driver.get(self.bidbud_url)
        self.log(f"Accessing BidBud feedback section: {self.bidbud_url}")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        counter = 1
        while True:
            rows = self.driver.find_elements(By.CSS_SELECTOR, 'table#feedback_table tr')
            for row in rows:
                try:
                    username = row.find_element(By.CSS_SELECTOR, 'a[title="View member\'s listings"]').text.strip()
                    listing_number = row.find_element(By.CSS_SELECTOR, 'td.nowrap.hidden-xs a').text.strip()
                    date = row.find_element(By.CSS_SELECTOR, 'td.align-right').text.strip()
                    feedback = row.find_element(By.CSS_SELECTOR, 'td.wordwrap').text.strip()
                    feedback_data.append([username, listing_number, date, feedback])
                    self.log(f"{counter}) Scraped: {username}, {listing_number}, {date}, {feedback}")
                    counter += 1
                except Exception as e:
                    self.log(f"Error extracting feedback: {e}")
                    continue
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                self.log("Reached the end of the feedback section.")
                break
            last_height = new_height
        self.log("Feedback data extraction completed.")
        return feedback_data

    def get_text(self, by, selector):
        try:
            return self.driver.find_element(by, selector).text.strip()
        except:
            return 'N/A'

    def get_input_value(self, name):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, f'input[name="{name}"]').get_attribute("value")
        except:
            return 'N/A'

    def get_listing_number(self):
        try:
            listing_number_divs = self.driver.find_elements(By.CLASS_NAME, 'tm-share-listing-link__info-block')
            for div in listing_number_divs:
                text = div.text.strip()
                if 'Listing #' in text:
                    return text.split('Listing #')[-1].strip()
        except:
            pass
        return 'N/A'

    def get_sku(self):
        try:
            script = self.driver.find_element(By.ID, 'frend-state').get_attribute('innerHTML')
            start_index = script.find('"sKU":"') + len('"sKU":"')
            end_index = script.find('"', start_index)
            return script[start_index:end_index]
        except:
            return 'N/A'

    def get_category(self):
        try:
            breadcrumbs = self.driver.find_elements(By.CLASS_NAME, 'o-breadcrumbs__item')
            return ' > '.join([crumb.text.strip() for crumb in breadcrumbs if crumb.text.strip()])
        except:
            return 'N/A'

    def get_image(self, index):
        try:
            image_element = self.driver.find_element(By.CSS_SELECTOR, f'.tm-marketplace-listing-photos__thumbnail-slider-item:nth-child({index}) .o-aspect-ratio')
            style = image_element.get_attribute('style')
            start_index = style.find('url("') + len('url("')
            end_index = style.find('")', start_index)
            return style[start_index:end_index]
        except:
            return 'N/A'

    def get_shipping(self):
        try:
            shipping_elements = self.driver.find_elements(By.CSS_SELECTOR, 'tbody tr')
            shipping_data = []
            for row in shipping_elements:
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) >= 2:
                    shipping_info = f"{cols[0].text.strip()}\t{cols[1].text.strip()}"
                    shipping_data.append(shipping_info)
            return '\n'.join(shipping_data) if shipping_data else 'N/A'
        except:
            return 'N/A'


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScraperApp()
    window.show()
    sys.exit(app.exec_())
