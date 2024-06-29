import json
import re

import requests
from bs4 import BeautifulSoup

from ipad_pricer.product import Product


def get_conversion_rate_gbp_eur():
    url = "https://api.exchangerate-api.com/v4/latest/GBP"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["rates"].get("EUR", 1)
    else:
        print(
            f"Failed to retrieve conversion rate. Status code: {response.status_code}"
        )
        return 1


def convert_price(price_str, conversion_rate):
    if not isinstance(price_str, str):
        price_str = str(price_str)
    price_match = re.search(r"(\d+(\.\d+)?)", price_str)
    if not price_match:
        return price_str
    price_gbp = float(price_match.group(1))
    price_eur = price_gbp * conversion_rate
    return f"EUR {price_eur:.2f}"


def scrape_ipads_from_plaisio(base_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    products = []
    page = 1

    while True:
        url = f"{base_url};page={page};pagesize=48"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(
                f"[PLAISIO] Failed to retrieve the page. Status code: {response.status_code}"
            )
            break

        soup = BeautifulSoup(response.content, "html.parser")
        product_elements = soup.select(
            "ul.product-list div.product div.product-bottom-part"
        )

        if not product_elements:
            break

        for product in product_elements:
            url = product.select_one(".product-title a")
            title = product.select_one(".product-title a div")
            price = product.select_one(".price-container .price .price")
            if url and title and price:
                product = Product.from_title(
                    title.get_text(strip=True),
                    f"EUR {price.get_text(strip=True)}",
                    "PLAISIO",
                )
                products.append(product)

        print(f"[PLAISIO] Scraped page {page} with {len(product_elements)} products.")
        page += 1

    print(f"[PLAISIO] Found {len(products)} products")
    return products


def scrape_ipads_from_apple(url, conversion_rate):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(
            f"[APPLE] Failed to retrieve the page. Status code: {response.status_code}"
        )
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    products = []

    products_script = soup.find("script", {"id": "metrics", "type": "application/json"})
    if products_script:
        products_data = json.loads(products_script.get_text())
        for product in products_data["data"]["products"]:
            title = product["name"]
            price = convert_price(product["price"]["fullPrice"], conversion_rate)
            product = Product.from_title(title, price, "APPLE")
            products.append(product)

    print(f"[APPLE] Found {len(products)} products")
    return products


def main():
    conversion_rate = get_conversion_rate_gbp_eur()
    print(f"Conversion rate 1 GBP = {conversion_rate} EUR")

    plaisio_url = "https://www.plaisio.gr/tilefonia-tablet/tablet/apple?location=categories=Τηλεφωνία+%26+tablet,tablet;brand=apple;tab_model=ipad+air+6th+gen"
    plaisio_ipads = scrape_ipads_from_plaisio(plaisio_url)

    apple_url = "https://www.apple.com/uk-edu/shop/buy-ipad/ipad-air/"
    apple_ipads = scrape_ipads_from_apple(apple_url, conversion_rate)

    all_ipads = plaisio_ipads + apple_ipads

    print(f"Found a total of {len(all_ipads)} products from all sources")

    grouped_products = {}
    for ipad in all_ipads:
        if ipad.title in grouped_products:
            grouped_products[ipad.title].append((ipad.price, ipad.source))
        else:
            grouped_products[ipad.title] = [(ipad.price, ipad.source)]

    product_diffs = []
    for title, prices_sources in grouped_products.items():
        prices = [float(price[0].split()[1]) for price in prices_sources]
        if len(prices) > 1:
            min_price = min(prices)
            max_price = max(prices)
            price_difference = max_price - min_price
            product_diffs.append((title, price_difference, prices_sources))

    product_diffs.sort(key=lambda x: x[1])

    for title, price_difference, prices_sources in product_diffs:
        print(f"\n{title}")
        for price, source in prices_sources:
            print(f"  - {source}: {price}")
        print(f"  Price difference: {price_difference:.2f}")


if __name__ == "__main__":
    main()
