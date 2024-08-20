from datetime import datetime
import logging
from news_reader import NewsReader, News


logger = logging.getLogger("reuters")


# TODO: reuters website has strong bot detection, making our lives hard :)
#       Investigate using undetected chromium for it: https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/1608
class Reuters(NewsReader):
    url = "https://www.reuters.com"
    available_sections = [
        "World",
        "Business",
        "Legal",
        "Markets",
        "Breakingviews",
        "Technology",
        "Sustainability",
        "Science",
        "Sports",
        "Lifestyle",
    ]

    # These are all necessary CSS locators for Reuters
    locators = {
        "search_bar_button": "button[aria-label='Open search bar']",
        "search_bar_input": "input[type=search]",
        "search_submit_button": "button[aria-label=Search]",
        "section_filter_dropdown": "button#sectionfilter",
        "section_filter_item": "li[data-key={section}]",
        "search_sort_dropdown": "button#sortby",
        "search_sort_item": "li[data-key={sortby}]",
        "result_item": "li[class*=results__item]",
        "news_title_span": "span[data-testid=Heading]",
    }

    def get_search_bar(self):
        logger.debug("Getting search bar button")
        button = self.get_element("search_bar_button")
        button.click()

        self.random_delay()

        logger.debug("Getting search bar input")
        return self.get_element("search_bar_input")

    def get_search_submit_button(self):
        logger.debug("Getting search bar submit button")
        return self.get_element("search_submit_button")

    def sort_by_newest(self):
        logger.debug("Getting sort dropdown for search results and clicking on it")
        dropdown = self.get_element("search_sort_dropdown")
        dropdown.click()

        self.random_delay()

        logger.debug("Getting sort dropdown item and clicking on it")
        sort_item = self.get_element("search_sort_item", format_values={
            "sortby": "Newest",
        })
        sort_item.click()

    def filter_by_section(self, section):
        """
        Reuters section filtering works by clicking on the section
        dropdown, then selecting one of the available sections.
        The page will auto-refresh after picking a section.
        """

        if section not in self.available_sections:
            return

        # Open dropdown
        dropdown = self.get_element("section_filter_dropdown")
        dropdown.click()

        self.random_delay()

        # Pick section
        section_item = self.get_element("section_filter_item", format_values={
            "section": section,
        })
        section_item.click()

    def collect_news(self, months_ago):
        # TODO: follow pagination
        # Determine the oldest year/month for the news
        today = datetime.now()
        min_year = today.year
        min_month = today.month
        if months_ago > 0:
            min_year -= months_ago // 12
            min_month -= months_ago % 12

        all_news = []
        results = self.get_element("result_item").all()
        for result in results:

            # News are sorted by latest first, stop grabbing after the next older than `months_ago`
            date = self.get_element("time", element=result).get_attribute("datetime")
            year, month, _ = date.split("-")
            if int(year) < min_year or int(month) < min_month:
                break

            title = self.get_element("news_title_span", element=result).text_content()
            picture_url = self.get_element("img", element=result).get_attribute("src")
            print(f"{date}: {title} {picture_url}")

            news = News(
                title=title,
                date=date,
                picture_url=picture_url,
            )
            all_news.append(news)

        return all_news
