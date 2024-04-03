from flask import Flask, render_template, jsonify, request
from scrapers.amazon import AmazonScraper
from scrapers.base_scraper import BaseScraper
from scrapers.bestbuy import BestBuyScraper
from scrapers.ebay import EbayScraper
import json
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
  
@app.route('/fetch_products', methods=['POST'])
def fetch_products():
    data = request.get_json()
    tac_code = data.get('tacCode', '')

    if tac_code:
        result = run_scraper(tac_code)
        if result is None:  
            return jsonify({"error": "Invalid TAC or IMEI code provided. Please enter a valid 8-digit TAC or 15-digit IMEI code."}), 404  
        else:
          return jsonify({"products": json.loads(result[0]), "product_name": result[1]})
    else:
        return jsonify({"error": "TAC code is required"}), 400
      
def run_scraper(code):
    base_scraper = BaseScraper()
    amazon_scraper = AmazonScraper()
    bestbuy_scraper = BestBuyScraper()
    ebay_scraper = EbayScraper()

    code_str = str(code)
    if len(code_str) == 8:  # Input is a TAC code
        cleaned_tac_str = base_scraper.clean_tac(code_str)
        imei_str = base_scraper.generate_imei_from_tac(cleaned_tac_str)
    else:
        imei_str = code_str  # Input is an IMEI code
    device_info_dict = base_scraper.get_device_name(imei_str, "https://imeicheck.com/imei-tac-database-info/")

    if device_info_dict:
        brand = device_info_dict.get("Brand", "")
        model_name = device_info_dict.get("Model Name", "")
        product_name = f"{brand} {model_name}"
        
        ebay_products = ebay_scraper.get_phone(brand, model_name)
        amazon_products = amazon_scraper.get_phone(brand, model_name)
        bestbuy_products = bestbuy_scraper.get_phone(brand, model_name)
        
        products = []
        if isinstance(ebay_products, list) and ebay_products:
            products += ebay_products
        if isinstance(amazon_products, list) and amazon_products:
            products += amazon_products
        if isinstance(bestbuy_products, list) and bestbuy_products:
            products += bestbuy_products
            
        # Convert Product instances to dictionaries
        products_data = [{
            "title": product.title,
            "price": product.price,
            "rating": product.rating,
            "review": product.review,
            "url": product.url,
            "image": product.image, 
            "source": product.source
        } for product in products]

        # Serialize to JSON
        products_json = json.dumps(products_data, indent=4)

        with open('products_data.json', 'w') as f:
            f.write(products_json)
            
        return products_json, product_name
    else:
      return None

if __name__ == '__main__':
    app.run(debug=True)
