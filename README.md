# TAC/IMEI Mobile Device Web-Scraping 

This project is designed to scrape product listings from various e-commerce websites based on a TAC or IMEI code provided by the user. It leverages Python with Flask for the backend, along with Selenium and BeautifulSoup for web scraping functionalities.

## Project Overview

The application allows users to input a TAC or IMEI code, upon which it fetches relevant product listings from Amazon, BestBuy, and eBay. This is particularly useful for obtaining detailed information and comparison shopping for mobile devices and other electronic products.

## Dependencies

To run this project, you'll need the following installed on your system:

- Flask
- requests
- BeautifulSoup
- Selenium
- webdriver-manager
## How to Run the Program

To get the program running on your local environment, follow these steps:

1. **Clone the repository** to your local machine.
2. **Install the required dependencies** using pip:

   ```bash
   pip install -r requirements.txt

3. **Run the Flask application** by executing the `app.py` file:

   ```bash
   python app.py

4. Access the application in your web browser at `http://localhost:5000.`
