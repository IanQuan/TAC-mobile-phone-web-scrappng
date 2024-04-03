from bs4 import BeautifulSoup
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_scraper import BaseScraper
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


class BestBuyScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        
    def get_phone(self, brand, model_name):
        mobile_device = brand + " " + model_name
        query = mobile_device.replace(" ", "+")
        keywords = model_name.lower().split()
        
        search_url = f"https://www.bestbuy.ca/en-ca/search?search={query}"
        
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito") # Fresh start every time so no interference
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.geolocation": 2,  # Block the geolocation
        })
        # options.add_argument("--headless") 
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(search_url) # Bring the browser to the url specified above
        driver.set_window_size(1200, 900) # Set window resolution so that all elements can still load on page


        try: 
            start_time = time.time()
            # Wait for the dynamic content to load
            wait = WebDriverWait(driver, 10)  
            products_container = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "productListingContainer_1Iyio"))
            )
            
            for _ in range(3):  # Purposely click "Show More" only three times since results are already sorted by relevance
                try:
                    parent_div = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'loadMoreButtonContainer_35w02'))
                    )
                    button = WebDriverWait(parent_div, 10).until(
                        EC.element_to_be_clickable((By.TAG_NAME, 'button'))
                    )
                    driver.execute_script("arguments[0].click();", button)
                    print("\"Show more\" button has been clicked.")
                except NoSuchElementException:
                    print("The \"Show more\" button was not found on the page.")
                    break
                except WebDriverException as e:
                    print(f"A WebDriver error occurred: {e}")
                    break
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                    break
                
            # Simulate more human-like scrolling by doing it in increments
            for _ in range(6):  # Scroll down in increments
                driver.execute_script("window.scrollBy(0, document.body.scrollHeight / 6);")
                time.sleep(1)  # Wait a bit between scrolls for content to load


            # Now that the content is loaded
            html_content = products_container.get_attribute('innerHTML')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            results_div = soup.find_all("div", class_="col-xs-12_198le col-sm-4_13E9O col-lg-3_ECF8k x-productListItem productLine_2N9kG")
            
            product_list = []
            for div in results_div:
                # Extract the title
                title_div = div.find("div", class_="productItemName_3IZ3c")
                if title_div:
                    title = title_div.text.strip()
                    # Only add the title(s) that has all the keywords and no negative
                    if not(title and self.match_keywords_with_negatives(title, keywords, self.negative_keywords)):
                        continue
                else:
                    continue

                # Extract the price
                price_span = div.find("span", class_="style-module_screenReaderOnly__4QmbS style-module_large__g5jIz")
                if price_span:
                    price_str = price_span.text.strip()
                    clean_price_str = price_str.replace('$', '').replace(',', '')
                    try:
                        price = format(float(clean_price_str), '.2f')
                    except ValueError:
                        price = None
                else:
                    price = None

                # Extract the number of reviews
                review_span = div.find('span', {'data-automation': 'rating-count'})
                if review_span:
                    review_text = review_span.text
                    review = re.search(r'\d+', review_text).group() if re.search(r'\d+', review_text) else None
                else:
                    review = 0

                # Extract the rating
                rating = 0.0
                if review and int(review) > 0:
                    star_divs = div.find_all('div', class_='style-module_ratableStar__UU280')
                    for star_div in star_divs:
                        partial_star = star_div.find('div', class_='style-module_partialStar__QWaDh')
                        if partial_star:
                            try:
                                width_percent = float(partial_star['style'].split(':')[1].replace('%;', '').strip())
                                rating += width_percent / 100
                            except ValueError:
                                continue
                else:
                    rating = None
                    
                # Extract the product URL
                url_tag = div.find("a", class_="link_3hcyN")
                if url_tag and 'href' in url_tag.attrs:
                    full_url = f"https://www.bestbuy.ca{url_tag['href']}"
                else:
                    full_url = None

                # Extract the product image
                image_tag = div.find("img", class_="productItemImage_1en8J")
                if image_tag and image_tag.has_attr('src'):
                    image_url = image_tag['src']
                elif image_tag and image_tag.has_attr('data-src'):  # Fallback for lazy-loaded images
                    image_url = image_tag['data-src']
                else:
                    image_url = None
                    
                product = self.Product(
                    title=title, 
                    price=price,
                    rating=rating,
                    review=int(review),
                    url=full_url,
                    image=image_url,
                    source="BestBuy"
                )
                product_list.append(product)
                
        except Exception as e:
            # Handle or log the error
            print(f"Error during scraping: {str(e)}")
            
        finally:
            end_time = time.time()
            processing_time = end_time - start_time
            print(f"Number of products:{len(product_list)}")
            print(f"Processing time for bestbuy: {processing_time} seconds")
            return product_list

            
        
        
# # Example usage
# bestbuy_scraper = BestBuyScraper()
# tac_str = "35848515"
# cleaned_tac_str = bestbuy_scraper.clean_tac(tac_str)
# imei_str = bestbuy_scraper.generate_imei_from_tac(cleaned_tac_str)
# device_info_dict = bestbuy_scraper.get_device_name(imei_str, "https://imeicheck.com/imei-tac-database-info/")
# if device_info_dict:
#     bestbuy_proudcts = bestbuy_scraper.get_phone(brand=device_info_dict.get("Brand", ""), model_name=device_info_dict.get("Model Name", ""))
