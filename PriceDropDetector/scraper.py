import asyncio
from playwright.async_api import async_playwright


async def fetch_amazon_price(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_selector("#productTitle", timeout=10000)

            name = await page.locator("#productTitle").first.inner_text()
            price_raw = await page.locator("span.a-price-whole").first.inner_text()
            image = await page.locator("#landingImage").get_attribute("src")

            # Remove commas + non digits
            clean_price = "".join(filter(str.isdigit, price_raw))

            return {
                "name": name.strip(),
                "price": float(clean_price),
                "image": image
            }
           

        except Exception as e:
            print(f"Scraper error: {e}")
            return None

        finally:
            await browser.close()


# UPDATED FIX — compatible with FastAPI
def get_amazon_price(url):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(fetch_amazon_price(url))
        loop.close()
        return result
    except Exception as e:
        print(f"Sync Runner Error: {e}")
        return None
