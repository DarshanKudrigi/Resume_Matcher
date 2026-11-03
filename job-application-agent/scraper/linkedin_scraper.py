import time
import random
import urllib.parse
from datetime import datetime
from playwright.sync_api import sync_playwright
from scraper.base_scraper import BaseScraper
from tracker.models import Job

class LinkedInScraper(BaseScraper):
    BASE_URL = "https://www.linkedin.com/jobs/search/"

    def __init__(self, keywords: list[str], location: str, headless: bool = True):
        super().__init__(keywords, location, headless)

    def scrape(self, max_jobs: int = 10) -> list[Job]:
        jobs = []
        max_jobs = min(max(1, max_jobs), 10)
        encoded_keyword = urllib.parse.quote(" ".join(self.keywords))
        encoded_location = urllib.parse.quote(self.location)
        url = f"{self.BASE_URL}?keywords={encoded_keyword}&location={encoded_location}"

        try:
            with sync_playwright() as p:
                launch_kwargs = {
                    "headless": self.headless,
                    "args": ["--disable-blink-features=AutomationControlled", "--no-sandbox"]
                }
                try:
                    browser = p.chromium.launch(channel="chrome", **launch_kwargs)
                except Exception:
                    browser = p.chromium.launch(**launch_kwargs)

                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 800}
                )
                context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                page = context.new_page()
                try:
                    page.goto(url, timeout=30000)
                    page.wait_for_timeout(2500)
                except Exception as e:
                    print(f"LinkedIn: Page load warning: {e}")

                all_cards = page.query_selector_all(".base-card")
                cards = all_cards[:max_jobs]
                print(f"LinkedIn: Found {len(all_cards)} job cards (fetching top {len(cards)})")

                for card in cards:
                    try:
                        title_el = card.query_selector(".base-search-card__title")
                        company_el = card.query_selector(".base-search-card__subtitle")
                        location_el = card.query_selector(".job-search-card__location")
                        link_el = card.query_selector("a.base-card__full-link")
                        time_el = card.query_selector("time")

                        if not (title_el and company_el and link_el):
                            continue

                        title = title_el.inner_text().strip()
                        company = company_el.inner_text().strip()
                        location = location_el.inner_text().strip() if location_el else self.location
                        raw_link = link_el.get_attribute("href") or ""
                        link = raw_link.split("?")[0] if raw_link else ""
                        posted_date = time_el.inner_text().strip() if time_el else ""

                        if not title or not link:
                            continue

                        job = Job(
                            title=title,
                            company=company,
                            location=location,
                            url=link,
                            description="",
                            source="linkedin",
                            scraped_at=datetime.now().isoformat(),
                        )
                        job.match_meta = {
                            "posted_date": posted_date,
                            "experience": "Entry / Mid Level",
                            "salary": "Not specified"
                        }
                        jobs.append(job)
                        time.sleep(random.uniform(0.1, 0.4))
                    except Exception as e:
                        print(f"LinkedIn: Skipped card due to error: {e}")
                        continue

                # Fetch individual job descriptions (up to top 7)
                for job in jobs[:max_jobs]:
                    job.description = self.get_description(page, job.url)
                    time.sleep(random.uniform(0.3, 0.6))

                browser.close()
        except Exception as e:
            print(f"LinkedInScraper error: {e}")

        return self._dedupe(jobs)

    def get_description(self, page, url: str) -> str:
        if not url:
            return ""
        try:
            # 1. Navigate with domcontentloaded and 28-second timeout
            page.goto(url, timeout=28000, wait_until="domcontentloaded")
            
            # Dismiss sign-in prompt / modal if present
            try:
                close_btn = page.query_selector("button[aria-label='Dismiss'], button.modal__dismiss, [data-tracking-control-name='public_jobs_contextual-sign-in-modal_modal_dismiss']")
                if close_btn:
                    close_btn.click(timeout=1500)
            except Exception:
                pass

            # 2. Wait separately for job description element
            selectors = [
                ".show-more-less-html__markup",
                ".description__text",
                ".decorated-job-posting__details",
                "section.show-more-less-html",
                "div.show-more-less-html__markup"
            ]
            selector_query = ", ".join(selectors)

            try:
                page.wait_for_selector(selector_query, timeout=5000)
            except Exception:
                pass

            # 3. Extract description text from primary selectors
            for sel in selectors:
                el = page.query_selector(sel)
                if el:
                    text = el.inner_text().strip()
                    if text:
                        return text

            # 4. Fallback extraction methods
            # Fallback A: Meta tags (og:description or description)
            for meta_sel in ["meta[property='og:description']", "meta[name='description']"]:
                meta_el = page.query_selector(meta_sel)
                if meta_el:
                    meta_content = meta_el.get_attribute("content")
                    if meta_content and len(meta_content.strip()) > 30:
                        return meta_content.strip()

            # Fallback B: Main article or content container
            article_el = page.query_selector("article, main, .core-section-container__content")
            if article_el:
                text = article_el.inner_text().strip()
                if len(text) > 40:
                    return text[:3000]

            return ""
        except Exception as e:
            # Log notice and continue processing remaining jobs safely without failing the batch
            print(f"LinkedIn: Could not fetch description for {url} ({e}). Continuing remaining jobs...")
            return ""
