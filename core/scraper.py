"""
Web scraper for Cardamom daily prices from indianspices.com
Runs once a day via management command or APScheduler.
"""

import requests
from bs4 import BeautifulSoup
from datetime import date
import logging

logger = logging.getLogger(__name__)

PRICE_URL = "https://www.indianspices.com/marketing/price/domestic/daily-price.html"

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def clean_market_name(name):
    """Remove company names and map to Kerala auction centers."""
    import re
    name = name.upper()
    
    # Mapping of auctioneers to Kerala locations
    kerala_map = {
        'CPMC': 'Kumily',
        'KCPMC': 'Kumily',
        'CPM': 'Puttady',
        'MAS': 'Vandanmedu',
        'SITCO': 'Puttady',
        'STC': 'Puttady',
        'GREEN HOUSE': 'Vandanmedu',
        'CPA': 'Bodi',
        'CARDAMOM PLANTERS': 'Bodi',
        'NEDUMKANDAM': 'Nedumkandam',
        'KUMILY': 'Kumily',
        'VANDANMEDU': 'Vandanmedu',
        'PUTTADY': 'Puttady',
        'BODINAYAKANUR': 'Bodi',
        'IDUKKI': 'Idukki',
    }
    
    for key, location in kerala_map.items():
        if key in name:
            return location
            
    # Fallback cleaning
    name = re.sub(r'\(.*?\)', '', name)
    companies = ['LTD', 'PVT', 'LIMITED', 'COMPANY', 'MARKETING', 'PRODUCER', 'CO-OP']
    for comp in companies:
        name = re.sub(rf'\b{comp}\b', '', name)
    
    name = name.strip().title()
    return name if name else "Kerala Market"

def scrape_cardamom_prices():
    """
    Scrape daily small cardamom prices with history from indianspices.com.
    """
    try:
        response = requests.get(PRICE_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        prices = []
        
        # Look for small cardamom tables/sections
        for table in soup.find_all('table'):
            rows = table.find_all('tr')
            if not rows: continue
            
            # Check if this table contains small cardamom keywords
            table_text = table.get_text().lower()
            if 'small' not in table_text and 'cardamom' not in table_text:
                continue

            for i, row in enumerate(rows):
                cols = row.find_all(['td', 'th'])
                if len(cols) < 5: continue
                
                col_texts = [c.get_text(strip=True) for c in cols]
                row_text = " ".join(col_texts).lower()
                
                # Skip headers or irrelevant rows
                if 'date' in row_text and 'market' in row_text: continue
                if 'sno' in row_text: continue

                # Try to find the date column (usually 2nd col or matches date pattern)
                price_date = None
                date_str = ""
                for col in col_texts:
                    match = re.search(r'\d{1,2}-[A-Za-z]{3}-\d{4}', col)
                    if match:
                        date_str = match.group(0)
                        try:
                            # Parse 07-Mar-2026
                            price_date = datetime.strptime(date_str, "%d-%b-%Y").date()
                        except: pass
                        break
                
                if not price_date: continue

                # Identify market (usually after date)
                market_raw = ""
                for txt in col_texts:
                    if txt == date_str:
                        # Market is usually the next non-empty, non-numeric column
                        idx = col_texts.index(txt)
                        for next_txt in col_texts[idx+1:]:
                            if next_txt and not next_txt.replace('.','').isdigit():
                                market_raw = next_txt
                                break
                        break
                
                if not market_raw: continue
                
                # Clean and filter
                market_clean = clean_market_name(market_raw)
                
                # Modal price is usually the last column
                try:
                    p_str = "".join(c for c in col_texts[-1] if c.isdigit() or c == '.')
                    modal_price = float(p_str)
                except: continue

                if market_clean and modal_price:
                    prices.append({
                        'market': market_clean,
                        'grade': 'Auction Avg',
                        'modal_price': modal_price,
                        'date': price_date,
                        'raw_data': ' | '.join(col_texts)
                    })

        # Remove duplicates
        unique_results = []
        seen = set()
        for p in prices:
            key = (p['market'], p['date'])
            if key not in seen:
                unique_results.append(p)
                seen.add(key)
        
        return unique_results

    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        return []


def get_latest_prices_fallback():
    """Return sample Cardamom price data when scraping fails (for demo purposes)."""
    import decimal
    today = date.today()
    return [
        {
            'market': 'Bodinayakanur (ICRI)',
            'grade': '8mm',
            'min_price': decimal.Decimal('1800'),
            'max_price': decimal.Decimal('2200'),
            'modal_price': decimal.Decimal('2050'),
            'unit': 'per kg',
            'raw_data': 'Bodinayakanur | 8mm | 1800 | 2200 | 2050',
            'date': today,
        },
        {
            'market': 'Kumily',
            'grade': '7mm',
            'min_price': decimal.Decimal('1600'),
            'max_price': decimal.Decimal('2000'),
            'modal_price': decimal.Decimal('1850'),
            'unit': 'per kg',
            'raw_data': 'Kumily | 7mm | 1600 | 2000 | 1850',
            'date': today,
        },
        {
            'market': 'Vandanmedu',
            'grade': '6mm',
            'min_price': decimal.Decimal('1400'),
            'max_price': decimal.Decimal('1800'),
            'modal_price': decimal.Decimal('1600'),
            'unit': 'per kg',
            'raw_data': 'Vandanmedu | 6mm | 1400 | 1800 | 1600',
            'date': today,
        },
        {
            'market': 'Nedumkandam',
            'grade': 'bold',
            'min_price': decimal.Decimal('2000'),
            'max_price': decimal.Decimal('2400'),
            'modal_price': decimal.Decimal('2200'),
            'unit': 'per kg',
            'raw_data': 'Nedumkandam | Bold | 2000 | 2400 | 2200',
            'date': today,
        },
    ]
