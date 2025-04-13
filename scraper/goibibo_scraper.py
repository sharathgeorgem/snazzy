from playwright.async_api import async_playwright
from typing import List, Dict

async def scrape_train_data(source: str, destination: str, date: str, class_type: str) -> List[Dict]:
    """
    Use Playwright to scrape train data from Goibibo.
    Returns a list of train dicts matching the target schema.
    """

    trains = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to Goibibo train page with search parameters
        search_url = (
            f"https://www.goibibo.com/trains/{source.lower()}-to-{destination.lower()}/"
        )
        await page.goto(search_url, timeout=60000)

        await page.wait_for_selector('div.TrainCardstyles__Card-sc', timeout=15000)

        train_cards = await page.query_selector_all("div.TrainCardstyles__Card-sc")

        for card in train_cards:
            try:
                name_text = await card.query_selector("h4")
                name = await name_text.inner_text() if name_text else ""

                number_text = await card.query_selector("span.TrainCardstyles__TrainNumber-sc")
                number = await number_text.inner_text() if number_text else ""

                dep_text = await card.query_selector("span.TrainCardstyles__DepartureTime-sc")
                dep = await dep_text.inner_text() if dep_text else ""

                arr_text = await card.query_selector("span.TrainCardstyles__ArrivalTime-sc")
                arr = await arr_text.inner_text() if arr_text else ""

                duration_text = await card.query_selector("span.TrainCardstyles__Duration-sc")
                duration = await duration_text.inner_text() if duration_text else ""

                availability_text = await card.query_selector("span[data-testid='availability']")
                availability = await availability_text.inner_text() if availability_text else "Check Manually"

                fare = 1999  # You can refine this by scraping actual fare data

                trains.append({
                    "train_number": number.strip(),
                    "train_name": name.strip(),
                    "departure": dep.strip(),
                    "arrival": arr.strip(),
                    "duration": duration.strip(),
                    "availability": availability.strip(),
                    "fare": fare
                })

            except Exception as e:
                print(f"Error parsing a train card: {e}")

        await browser.close()

    return trains