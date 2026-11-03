import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright

from scraper.base_scraper import BaseScraper
from tracker.models import Job


import re

class NaukriScraper(BaseScraper):
    def __init__(self, keywords: list[str], location: str, headless: bool = True):
        super().__init__(keywords, location, headless)

    def _build_url(self) -> str:
        first_kw = self.keywords[0] if self.keywords else "software-engineer"
        clean_kw = re.sub(r'[^a-zA-Z0-9\s-]', '', first_kw).strip()
        keyword = "-".join(clean_kw.lower().split()) or "software-engineer"

        # Sanitize location: remove commas/state suffixes to prevent malformed Naukri slugs
        loc_str = self.location or "bangalore"
        primary_loc = loc_str.split(",")[0].strip()
        clean_loc = re.sub(r'[^a-zA-Z0-9\s-]', '', primary_loc).strip()
        location = "-".join(clean_loc.lower().split()) or "bangalore"

        return f"https://www.naukri.com/{keyword}-jobs-in-{location}"

    def scrape(self, max_jobs: int = 10) -> list[Job]:
        jobs = []
        max_jobs = min(max(1, max_jobs), 10)
        url = self._build_url()

        try:
            with sync_playwright() as p:
                launch_kwargs = {
                    "headless": self.headless,
                    "args": [
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-setuid-sandbox"
                    ]
                }
                try:
                    browser = p.chromium.launch(channel="chrome", **launch_kwargs)
                except Exception:
                    browser = p.chromium.launch(**launch_kwargs)

                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    viewport={"width": 1366, "height": 768},
                    extra_http_headers={
                        "Accept-Language": "en-US,en;q=0.9"
                    }
                )
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    window.navigator.chrome = { runtime: {} };
                    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                """)
                page = context.new_page()

                try:
                    page.goto(url, timeout=30000, wait_until="load")
                    page.wait_for_timeout(3500)
                except Exception as e:
                    print(f"Naukri: Page load warning: {e}")

                # Wait for any job cards to render
                try:
                    page.wait_for_selector(
                        ".srp-jobtuple-wrapper, .cust-job-tuple, article.jobTuple, div[data-job-id], [class*='srp-jobtuple']",
                        timeout=7000
                    )
                except Exception:
                    pass

                # Dismiss any popups
                try:
                    close = page.query_selector("button.close-btn")
                    if close:
                        close.click(timeout=1500)
                        page.wait_for_timeout(300)
                except Exception:
                    pass

                all_cards = page.query_selector_all(
                    ".srp-jobtuple-wrapper, .cust-job-tuple, article.jobTuple, div[data-job-id], [class*='srp-jobtuple']"
                )
                cards = all_cards[:max_jobs]
                print(f"Naukri: Found {len(all_cards)} job cards (fetching top {len(cards)})")

                for card in cards:
                    try:
                        title_el   = card.query_selector(".title, a.title, [class*='title']")
                        company_el = card.query_selector(".comp-name, a.comp-name, [class*='comp-name'], [class*='compName']")
                        location_el = card.query_selector(".locWdth, .loc-wrap, [class*='locWdth'], [class*='location']")
                        link_el    = card.query_selector("a.title, a[href*='job-listings'], a")
                        exp_el     = card.query_selector(".expwdth, .exp-wrap, [class*='expwdth'], [class*='experience']")
                        sal_el     = card.query_selector(".sal-wrap, .salary, [class*='sal-wrap'], [class*='salary']")
                        date_el    = card.query_selector(".job-post-day, .date, [class*='job-post-day'], [class*='date']")

                        if not (title_el and company_el and link_el):
                            continue

                        title    = title_el.inner_text().strip()
                        company  = company_el.inner_text().strip()
                        location = location_el.inner_text().strip() if location_el else self.location
                        link     = link_el.get_attribute("href")
                        exp_text = exp_el.inner_text().strip() if exp_el else "Not specified"
                        sal_text = sal_el.inner_text().strip() if sal_el else "Not disclosed"
                        date_text = date_el.inner_text().strip() if date_el else ""

                        if not title or not link:
                            continue

                        job = Job(
                            title=title,
                            company=company,
                            location=location,
                            url=link,
                            description="",
                            source="naukri",
                            scraped_at=datetime.now().isoformat(),
                        )
                        job.match_meta = {
                            "experience": exp_text,
                            "salary": sal_text,
                            "posted_date": date_text
                        }
                        jobs.append(job)
                        time.sleep(random.uniform(0.1, 0.4))

                    except Exception as e:
                        print(f"Naukri: Skipped card — {e}")
                        continue

                # Fetch descriptions (up to top 7)
                for job in jobs[:max_jobs]:
                    job.description = self._get_description(page, job.url)
                    time.sleep(random.uniform(0.3, 0.6))

                browser.close()
        except Exception as e:
            print(f"NaukriScraper error: {e}")

        return self._dedupe(jobs)

    def _get_description(self, page, url: str) -> str:
        if not url:
            return ""
        try:
            page.goto(url, timeout=28000, wait_until="domcontentloaded")
            
            selectors = [
                ".styles_JDC__dang-inner-html__h0K4t",
                "section.job-desc-wrap",
                ".styles_job-desc-container__raw-content",
                ".job-desc",
                "#job-desc",
                "[class*='dang-inner-html']"
            ]
            try:
                page.wait_for_selector(", ".join(selectors), timeout=5000)
            except Exception:
                pass

            for sel in selectors:
                desc_el = page.query_selector(sel)
                if desc_el:
                    text = desc_el.inner_text().strip()
                    if text:
                        return text

            # Fallback to meta description
            for meta_sel in ["meta[property='og:description']", "meta[name='description']"]:
                meta_el = page.query_selector(meta_sel)
                if meta_el:
                    content = meta_el.get_attribute("content")
                    if content and len(content.strip()) > 30:
                        return content.strip()

            return ""
        except Exception as e:
            print(f"Naukri: Could not fetch description for {url} ({e}). Continuing remaining jobs...")
            return ""
