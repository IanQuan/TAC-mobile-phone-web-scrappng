import requests
from bs4 import BeautifulSoup
import time
import re
from scrapers.base_scraper import BaseScraper

class EbayScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        
    def get_phone(self, brand, model_name):
        mobile_device = brand + " " + model_name
        query = mobile_device.replace(" ", "+")
        keywords = model_name.lower().split()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
                  "referer": "https://google.com"}

        search_url = f"https://www.ebay.ca/sch/i.html?_from=R40&_trksid=p4432023.m570.l1313&_nkw={query}"
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            pass
        elif response.status_code in [429, 503]:
            print(f"Error: {response.status_code}")
            return 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        try: 
            start_time = time.time()

            result_container = soup.find("ul", {"class": "srp-results srp-list clearfix"})
            if not result_container:
                raise ValueError("Result container not found.")
            result_list = result_container.find_all("li", {"class": "s-item s-item__pl-on-bottom"})
            
            product_list = []
            for li in result_list:
                # Extract the title
                title_tag = li.find("div", {"class": "s-item__title"}).find("span", {"role": "heading"})
                title = title_tag.text.strip() if title_tag else None
                # Only add the title(s) that has all the keywords and no negative
                if not(title and self.match_keywords_with_negatives(title, keywords, self.negative_keywords)):
                    continue
                
                # Extract the price
                price = None
                price_span = li.find("span", {"class": "s-item__price"})
                if price_span:
                    match = re.search(r"C \$([\d,]+\.?\d*)", price_span.get_text())
                    if match:
                        try:
                            price = format(float(match.group(1).replace(',', '')), '.2f')
                        except ValueError:
                            continue

                # Extract the review count
                review = 0
                review_span = li.find("span", {"class": "s-item__reviews-count"})
                if review_span:
                    review_text = review_span.text
                    # Extract the number of reviews from the text
                    numbers = [int(s) for s in review_text.split() if s.isdigit()]
                    review = numbers[0] if numbers else None
        
                # Extract the rating
                rating = None
                rating_div = li.find("div", class_="x-star-rating")
                if rating_div:
                    rating_span = rating_div.find("span", class_="clipped")
                    if rating_span:
                        rating_str = rating_span.text
                        rating_match = re.search(r'\d+\.\d+', rating_str)
                        rating = rating_match.group() if rating_match else None
                        
                # Extract the product URL
                full_url = None
                url_tag = li.find("a", {"class": "s-item__link"})
                if url_tag and 'href' in url_tag.attrs:
                    full_url = url_tag['href']
                            
                # Extract the product image
                image_url = None
                image_tag  = li.find("div", {"class": "s-item__image-wrapper image-treatment"}).find("img")
                if image_tag and image_tag.has_attr('src'):
                    image_url = image_tag['src']
                    
                product = self.Product(
                    title=title, 
                    price=price,
                    rating=rating,
                    review=review,
                    url=full_url,
                    image=image_url,
                    source="Ebay"
                )
                product_list.append(product)

        except Exception as e:
            print(f"Error during scraping: {str(e)}")
                
        finally:
            end_time = time.time()
            processing_time = end_time - start_time
            print(f"Number of products:{len(product_list)}")
            print(f"Processing time for ebay: {processing_time} seconds")
            return product_list
            
            
# # Example usage
# ebay_scraper = EbayScraper()
# tac_str = "35225056"
# cleaned_tac_str = ebay_scraper.clean_tac(tac_str)
# imei_str = ebay_scraper.generate_imei_from_tac(cleaned_tac_str)
# device_info_dict = ebay_scraper.get_device_name(imei_str, "https://imeicheck.com/imei-tac-database-info/")
# if device_info_dict:
#     ebay_products =ebay_scraper.get_phone(brand=device_info_dict.get("Brand", ""), model_name=device_info_dict.get("Model Name", ""))

# print(ebay_products)