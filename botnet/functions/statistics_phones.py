import asyncio
import phonenumbers

from phonenumbers import geocoder
from collections import Counter

from rich.table import Table
from rich.console import Console

from functions.base import TelethonFunction

console = Console()


class PhoneNumbersStatsFunc(TelethonFunction):
    """Статистика(номера)"""

    async def get_phone_number(self, session):
        try:
            await session.connect()
        except Exception:
            return
        else:
            me = await session.get_me()
            return me.phone

    async def execute(self):
        with console.status("Пожалуйста, подождите..."):
            phones = await asyncio.gather(*[
                self.get_phone_number(session)
                for session in self.sessions
            ])

        countries = []
        countries_by_country_code = {}
        
        table = Table()

        table.add_column("Код страны", justify="left", style="white")
        table.add_column("Страна", style="white")
        table.add_column("Количество", justify="center", style="white")

        for phone in phones:
            if phone is not None:
                try:
                    parsed_phone = phonenumbers.parse(f"+{phone}", None)
                except Exception:
                    continue

                country = geocoder.description_for_number(parsed_phone, "en")

                if not countries_by_country_code.get(parsed_phone.country_code):
                    countries_by_country_code[parsed_phone.country_code] = country
                
                countries.append(parsed_phone.country_code)

        countries = Counter(countries)

        for country_code, count in countries.items():
            country_name = countries_by_country_code[country_code]

            if not country_name:
                country_name = "N/A"

            table.add_row(
                str(country_code), country_name, str(count)
            )
        
        console.print(table)