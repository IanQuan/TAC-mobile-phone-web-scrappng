import requests
from bs4 import BeautifulSoup
import time
import re
from .base_scraper import BaseScraper

class AmazonScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        
    def get_phone(self, brand, model_name):
        mobile_device = brand + " " + model_name
        query = mobile_device.replace(" ", "+")
        keywords = model_name.lower().split()

        search_url = f"https://www.amazon.ca/s?k={query}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1",
                        "referer": "https://google.com"}
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            pass
        elif response.status_code in [429, 503]:
            print(f"Error: {response.status_code}")
            return 
        soup = BeautifulSoup(response.text, 'html.parser')

        try: 
            start_time = time.time()

            result_container = soup.find("div", {"class": "s-main-slot s-result-list s-search-results sg-row"})
            if not result_container:
                raise ValueError("Result container not found.")
            result_div = result_container.find_all("div", {"data-component-type": "s-search-result"})
            
            product_list = []
            for div in result_div:
                # Extract the title
                title_tag = div.find("span", {"class": "a-size-base-plus a-color-base a-text-normal"})
                title = title_tag.text.strip() if title_tag else None
                # Only add the title(s) that has all the keywords and no negative
                if not(title and self.match_keywords_with_negatives(title, keywords, self.negative_keywords)):
                    continue
                
                # Extract the price
                price = None
                price_div = div.find("span", {"class": "a-price"})
                if price_div:
                    price_span = price_div.find("span", {"class": "a-offscreen"})
                    if price_span:
                        price_str = price_span.text.strip().replace('$', '').replace(',', '')
                        try:
                            price = format(float(price_str), '.2f')
                        except ValueError:
                            continue

                # Extract the review count
                review = 0
                review_tag = div.find("span", {"class": "a-size-base s-underline-text"})
                if review_tag:
                    review_str = review_tag.text.strip().replace(',', '')
                    try:
                        review = int(review_str)
                    except ValueError:
                        continue
                
                # Extract the rating
                rating = None
                rating_tag = div.find("a", class_="a-popover-trigger a-declarative")
                if rating_tag:
                    rating_span = rating_tag.find("span", class_="a-icon-alt")
                    if rating_span:
                        rating_str = rating_span.text
                        rating_match = re.search(r'\d+\.\d+', rating_str)
                        rating = rating_match.group() if rating_match else None

                # Extract the product URL
                full_url = None
                url_tag = div.find("a", {"class": "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"})
                if url_tag and 'href' in url_tag.attrs:
                    full_url = f"https://www.amazon.ca{url_tag['href']}"
                            
                # Extract the product image
                image_url = None
                image_tag = div.find("img", {"class": "s-image"})
                if image_tag and image_tag.has_attr('src'):
                    image_url = image_tag['src']
                    
                product = self.Product(
                    title=title, 
                    price=price,
                    rating=rating,
                    review=int(review),
                    url=full_url,
                    image=image_url,
                    source="Amazon"
                )
                product_list.append(product)

        except Exception as e:
            print(f"Error during scraping: {str(e)}")
                
        finally:
            end_time = time.time()
            processing_time = end_time - start_time
            print(f"Number of products:{len(product_list)}")
            print(f"Processing time for amazon: {processing_time} seconds")
            return product_list
            
            
    # def get_text_or_default(self, soup, selector, attribute=None, default="Not Available"):
    #     """
    #     Attempts to find text for a given CSS selector within a BeautifulSoup object.
    #     If the element or attribute is not found, returns a default value.
    #     """
    #     element = soup.select_one(selector)
    #     if element:
    #         if attribute:
    #             return element[attribute].strip()
    #         return element.get_text(strip=True)
    #     return default


    # def get_product_details(self, product_url, headers):
    #     response = requests.get(product_url, headers=headers)
    #     product_soup = BeautifulSoup(response.text, 'html.parser')
        
    #     product = self.Product(
    #         title=self.get_text_or_default(product_soup, "span#productTitle"),
    #         price=self.get_text_or_default(product_soup, "span.a-price span.a-offscreen"),
    #         review=self.get_text_or_default(product_soup, "span[data-action='acrStarsLink-click-metrics'] .a-size-base.a-color-base"),
    #         storage=self.get_text_or_default(product_soup, "tr.po-memory_storage_capacity .a-size-base.po-break-word"),
    #         sold_by=self.get_text_or_default(product_soup, "a#sellerProfileTriggerId"),
    #         url=product_url,
    #         source="Amazon"
    #     )
        
        # return product
        # print(f"Product Title: {product_title}")
        # print(f"Price: {price}")
        # print(f"Review: {review}")
        # print(f"Memory Storage Capacity: {storage}")
        # print(f"Sold By: {sold_by}")
        # print(f"URL: {product_url}\n")
        
# # Example usage
# amazon_scraper = AmazonScraper()
# tac_str = "35645710"
# cleaned_tac_str = amazon_scraper.clean_tac(tac_str)
# imei_str = amazon_scraper.generate_imei_from_tac(cleaned_tac_str)
# device_info_dict = amazon_scraper.get_device_name(imei_str, "https://imeicheck.com/imei-tac-database-info/")
# if device_info_dict:
#     amazon_products =amazon_scraper.get_phone(brand=device_info_dict.get("Brand", ""), model_name=device_info_dict.get("Model Name", ""))

# print(amazon_products)