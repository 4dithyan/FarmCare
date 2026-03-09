"""
Management command to scrape daily cardamom prices.
Run with: python manage.py scrape_prices
Schedule with cron/task scheduler to run once per day.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from core.scraper import scrape_cardamom_prices, get_latest_prices_fallback
from core.models import CardamomPrice
from datetime import date
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Scrape daily cardamom prices from indianspices.com'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force scrape even if prices for today already exist',
        )
        parser.add_argument(
            '--use-fallback',
            action='store_true',
            help='Use fallback sample data (for testing)',
        )

    def handle(self, *args, **options):
        today = date.today()
        force = options.get('force', False)
        use_fallback = options.get('use_fallback', False)

        # Check if already scraped today
        if not force and CardamomPrice.objects.filter(date=today).exists():
            self.stdout.write(
                self.style.WARNING(f'Prices for {today} already exist. Use --force to re-scrape.')
            )
            return

        self.stdout.write(f'Scraping cardamom prices for {today}...')

        if use_fallback:
            prices_data = get_latest_prices_fallback()
            self.stdout.write(self.style.WARNING('Using fallback sample data'))
        else:
            prices_data = scrape_cardamom_prices()

        if not prices_data:
            self.stdout.write(self.style.WARNING('No prices found from scraping. Using fallback data.'))
            prices_data = get_latest_prices_fallback()

        # Save to database
        created_count = 0
        updated_count = 0
        for price_data in prices_data:
            try:
                p_date = price_data.get('date', today)
                market = price_data.get('market', 'Unknown')
                
                # Check if this specific market/date combo exists
                obj, created = CardamomPrice.objects.update_or_create(
                    market=market,
                    date=p_date,
                    defaults={
                        'grade': price_data.get('grade', 'other'),
                        'modal_price': price_data.get('modal_price'),
                        'raw_data': price_data.get('raw_data', ''),
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                logger.error(f"Error saving price data: {e}")

        self.stdout.write(
            self.style.SUCCESS(f'Finished! Created {created_count}, Updated {updated_count} price entries.')
        )
