import requests
from bs4 import BeautifulSoup
import re

def scrape_etsy_low_price_items(search_term="digital download", target_price=0.065, price_tolerance=0.015):
    """
    Scrapes Etsy for items matching a search term, sorted by price ascending,
    and identifies items close to a target price.
    """
    # Construct the Etsy search URL. The 'sort_by=price_asc' parameter is crucial
    # for finding the lowest-priced items, as highlighted in the article.
    url = f"https://www.etsy.com/search?q={search_term.replace(' ', '+')}&sort_by=price_asc"
    
    # Use a User-Agent header to mimic a browser and avoid basic blocking by websites.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"Searching Etsy for '{search_term}' and sorting by price ascending...")
    print(f"Targeting items around ${target_price:.3f} (tolerance: +/- ${price_tolerance:.3f})\n")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        print("Etsy might have blocked the request or the URL structure has changed.")
        print("For robust scraping of dynamic sites like Etsy, consider using tools like Selenium.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Identify product listings. Etsy's HTML structure can change, requiring updates to selectors.
    # We look for common elements that encapsulate a product card.
    listings = soup.find_all('div', class_='v2-listing-card') # This class often denotes a product card

    found_items = []
    for listing in listings:
        # Extract the title, price, and URL for each product.
        title_tag = listing.find('h3', class_='v2-listing-card__title')
        price_tag = listing.find('span', class_='currency-value') # This class typically holds the numerical price
        link_tag = listing.find('a', class_='v2-listing-card__link')

        if title_tag and price_tag and link_tag:
            title = title_tag.text.strip()
            
            # Clean and parse the price string into a float.
            price_text = price_tag.text.strip().replace(',', '')
            match = re.search(r'\d+\.?\d*', price_text) # Regex to extract the number part
            if match:
                try:
                    price = float(match.group(0))
                except ValueError:
                    price = None
            else:
                price = None

            item_url = link_tag['href']

            if price is not None:
                # This is where we apply the article's core logic: finding items
                # with a price very close to the specified target (e.g., $0.065).
                if abs(price - target_price) <= price_tolerance:
                    found_items.append({
                        "title": title,
                        "price": price,
                        "url": item_url
                    })
    return found_items

if __name__ == "__main__":
    # The article focuses on discovering items around $0.065.
    search_term = "digital download" # A category often containing very low-priced items
    target_price = 0.065
    price_tolerance = 0.015 # Defines the range (e.g., $0.050 to $0.080)

    print("--- Etsy Low Price Item Finder ---")
    print(f"Searching for '{search_term}' items near ${target_price:.3f}\n")

    items = scrape_etsy_low_price_items(search_term, target_price, price_tolerance)

    if items:
        print(f"Found {len(items)} items near ${target_price:.3f}:\n")
        for item in items:
            print(f"Title: {item['title']}")
            print(f"Price: ${item['price']:.3f}")
            print(f"URL: {item['url']}\n")
    else:
        print(f"No items found near ${target_price:.3f} for '{search_term}'.")
        print("This could be due to Etsy's anti-scraping measures, HTML structure changes, or no matching products.")
