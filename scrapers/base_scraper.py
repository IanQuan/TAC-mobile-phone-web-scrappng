import requests
import re
import random

class BaseScraper:
    def __init__(self):
        self.negative_keywords = ['usb-flash-drives', 'thumb-drive', 'case', 'cases' 
                                  'protector', 'charger', 'charging', 'cushion', 
                                  'usb', 'adapter', 'headphone', 'repair', 
                                  'replacement', 'wallet', 'holder', 'headphone',
                                  'headphones', 'earbud', 'earbuds', 'laptop', 'glass', 'frame', 
                                  'cable', 'charge', 'airpods', 'Compatible', 'stand', 
                                  'protector', 'replacements', 'protective', 'cover']

    def get_phone(self, brand, model_name):
        raise NotImplementedError("Subclasses must implement this method")

    def clean_tac(self, tac_str):
        if len(tac_str) == 8:
            return tac_str
        elif len(tac_str) == 7:
            return "0" + tac_str
        else:
            return "Error: TAC must be either 7 or 8 digits long."


    def get_device_name(self, imei_str, imei_checker_url):
        try:     
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1",
                            "referer": "https://google.com"}
            form_data = {'imei': imei_str}  # input field for IMEI  
            response = requests.post(imei_checker_url, data=form_data, headers=headers)
            
            if response.status_code == 200:
                # Use regex to find the Swal.fire call and extract the title content
                match = re.search(r'Swal\.fire\(\{\s*title:\s*"([^"]+)"', response.text, re.DOTALL)
                if match:
                    device_info_text = match.group(1).replace('<br>', '\n')  # Convert <br> to newline
                    device_info_lines = device_info_text.split("\n")
                    
                    device_info_dict = {}
                    for line in device_info_lines:
                        if ": " in line:  # Ensure the line contains ": " before attempting to split
                            key, value = line.split(": ", 1)
                            device_info_dict[key.strip()] = value.strip()
                            
                    return device_info_dict
            else:
                print("Failed to retrieve the web page.")
                return False

        except Exception as e:
            print(f"An error occurred: {e}")
            return False
    
    
    def generate_imei_from_tac(self, tac):
        """
        Generates a valid IMEI number from a given TAC code using Luhn algorithm.

        Returns:
        str: A random valid IMEI number generated from the given TAC.
        """

        def checksum(digitSequence):
            digits = list(map(int, digitSequence))
            odd_sum = sum(digits[-1::-2])
            even_sum = sum([sum(divmod(2 * d, 10)) for d in digits[-2::-2]])
            return (odd_sum + even_sum) % 10

        def generate(digitSequence):
            cksum = checksum(digitSequence + '0')
            return (10 - cksum) % 10

        def append_luhn(digitSequence):
            return digitSequence + str(generate(digitSequence))

        imei_digits = [tac[i] if i < len(tac) else str(random.randint(0, 9)) for i in range(14)]
        return append_luhn("".join(imei_digits))
            
            
    def match_keywords_with_negatives(self, text, keywords, negative_keywords):
        text_lower = text.lower()
        
        keyword_patterns = [r'\b' + re.escape(keyword) + r'\b' for keyword in keywords]
        negative_keyword_patterns = [r'\b' + re.escape(neg_kw) + r'\b' for neg_kw in negative_keywords]
        
        if not all(re.search(pattern, text_lower) for pattern in keyword_patterns):
            return False  # At least one keyword was not found as a whole word
        
        if any(re.search(pattern, text_lower) for pattern in negative_keyword_patterns):
            return False  # At least one negative keyword was found as a whole word

        return True
    
        
    class Product:
        def __init__(self, title, price, rating, review, url, image, source):
            self.title = title
            self.price = price
            self.rating = rating
            self.review = review
            self.url = url
            self.image=image
            self.source = source  # "Amazon" or "BestBuy" or "Ebay"
