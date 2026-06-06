import asyncio
import itertools
import logging
import re
import sys
from argparse import ArgumentParser
from pathlib import Path

import anyio
from playwright.async_api import BrowserContext, async_playwright, expect

from tts.logging_config import set_logging_config

LOGGER = logging.getLogger("tts.scrape")

N_BOOKS = 10

PARAGRAPHS_TO_DROP = {
    "",
    "Next Chapter",
    "Optional Interlude",
}


def slugify(s: str) -> str:
    s = re.sub(r"['’]", "", s)  # noqa: RUF001
    s = re.sub(r"\W+", "-", s)
    s = s.strip("-").lower()
    return s


def chapter_name_from_url(url: str) -> str:
    # https://crosswiredgeeks.com/biologicalchronicle-book9chapter1/
    match = re.fullmatch(r"https://crosswiredgeeks\.com/biologicalchronicle-book\d+(\w+)/", url)
    if not match:
        raise ValueError(f"Regex match failed on unexpected URL format: {url}")
    slug = match.group(1).lower()
    slug = re.sub(r"(\d)(\D)", r"\1-\2", slug)
    slug = re.sub(r"(\D)(\d)", r"\1-\2", slug)
    return slug


def slug_to_title(s: str) -> str:
    return " ".join(s.split("-")).title()


async def scrape_book(context: BrowserContext, book_start_url: str, out_dir: Path):
    async with await context.new_page() as page:
        await page.goto(book_start_url)

        title_re = re.compile(r"Book (\d+): (.*)")
        title_locator = page.get_by_role("heading", name=title_re)
        await expect(title_locator).to_be_visible()
        title_re_match = title_re.fullmatch(await title_locator.inner_text())
        assert title_re_match is not None  # noqa: S101
        book_number = int(title_re_match.group(1))
        book_title = title_re_match.group(2)
        book_slug = f"book-{book_number:02d}-{slugify(book_title)}"
        LOGGER.info(f"{book_slug = }")

        book_dir = anyio.Path(out_dir / book_slug)
        await book_dir.mkdir(parents=True, exist_ok=True)

        await page.get_by_role("link", name="Begin reading").click()

        for i in itertools.count():
            article_locator = page.get_by_role("article")
            await expect(article_locator).to_have_count(1)
            chapter_name_slug = chapter_name_from_url(page.url)

            paragraph_texts = [slug_to_title(chapter_name_slug)]

            paragraph_locator = article_locator.locator("p")
            try:
                await expect(paragraph_locator.first).to_be_visible()
            except AssertionError:
                LOGGER.warning(f"No paragraph elements in the article on {page.url}")
                paragraph_texts.append("(No text content)")
            else:
                paragraph_texts += [
                    paragraph_text
                    for paragraph in await paragraph_locator.all()
                    if (paragraph_text := (await paragraph.inner_text()).strip())
                ]
            chapter_text = "\n\n".join(paragraph_texts)
            chapter_file = book_dir / f"{i:02d}-{chapter_name_slug}.txt"
            await chapter_file.write_text(chapter_text + "\n")

            optional_interlude_link = page.get_by_role("link", name="Optional Interlude")
            if await optional_interlude_link.count() > 0:
                await optional_interlude_link.click()
                continue

            await page.get_by_role("link", name="Next Chapter").click()


async def scrape(out_dir: Path) -> bool:
    async with (
        async_playwright() as pw,
        await pw.chromium.launch(channel="chromium", headless=False, slow_mo=0.5) as browser,
        await browser.new_context() as context,
        await context.new_page() as page,
    ):
        await page.goto("https://crosswiredgeeks.com/biologicalchronicle/")

        book_collapser_locator = page.get_by_text(re.compile(r"> Book (\d+):"))
        await expect(book_collapser_locator).to_have_count(N_BOOKS)
        book_collapsers = await book_collapser_locator.all()
        book_urls: list[str] = []
        for book_collapser in book_collapsers:
            await book_collapser.click()  # Open the collapser
            book_url = await page.get_by_role("link", name="Read Online").first.get_attribute("href")
            if not book_url:
                book_title = await book_collapser.inner_text()
                LOGGER.warning(f"Failed to get book url for {book_title}")
                continue
            book_urls.append(book_url)
            await book_collapser.click()  # Close the collapser

        # book_urls = [book_urls[0]]  # TODO: take this out

        results = await asyncio.gather(
            *(scrape_book(context, url, out_dir) for url in book_urls),
            return_exceptions=True,
        )
        n_errors = 0
        for result in results:
            if result is not None:
                n_errors += 1
                LOGGER.error("Scraping error", exc_info=result)
        if n_errors > 0:
            return False
        LOGGER.info(f"Successfully scraped all {len(results)} book(s)")
        return True


if __name__ == "__main__":
    set_logging_config()
    arg_parser = ArgumentParser(description="Clean text files")
    arg_parser.add_argument("--out-dir", "-o", type=Path, required=True)
    # arg_parser.add_argument("--out-dir", "-o", type=Path, default=Path("data/text"))
    args = arg_parser.parse_args()
    success_ = asyncio.run(scrape(args.out_dir))
    sys.exit(0 if success_ else 1)
