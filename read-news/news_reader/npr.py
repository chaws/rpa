from news_reader import NewsReader, News

import logging


logger = logging.getLogger("npr")


class Npr(NewsReader):
    url = "https://www.npr.org"

    # TODO: work out sections
    available_sections = []

    # These are all necessary CSS locators for Reuters
    locators = {
        "close_cookie_settings_button": "div#onetrust-close-btn-container",
        "search_bar_button": "a#navigation_dropdown-search",
        "search_bar_input": "div.non-hidden-search input[type=search]",
        "search_submit_button": "div.non-hidden-search button[type=submit]",
        "search_sort_div": "div.sortType",
        "news_container": "article.item",
        "news_description": "p.teaser",
        "news_title": "h2.title",
    }

    def pre_work(self):
        logger.debug("Closing cookie settings")
        button = self.get_element("close_cookie_settings_button")
        if button.is_visible():
            button.click()

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
        sort_div = self.get_element("search_sort_div")
        newest_link = sort_div.get_by_role("link", name="newest")
        if newest_link.is_visible():
            newest_link.click()

        # TODO: figure a better way to know when results are ready
        #       as the website uses ajax to return results
        self.random_delay(2)

    def filter_by_section(self, section):
        # TODO: sections will depend on results set
        #       so we should get that list first, check if desired section is contained, then filter
        pass

    def collect_news(self, months_ago):
        # TODO: follow pagination
        min_year, min_month = self.get_min_year_and_month(months_ago)

        all_news = []
        articles = self.get_element("news_container").all()
        for article in articles:

            # Some articles do not have image in them
            img = self.get_element("img", root=article)
            picture_url = None
            if img.is_visible():
                picture_url = img.get_attribute("src")

            date = self.get_element("time", root=article).get_attribute("datetime")
            description = self.get_element("news_description", root=article).text_content()
            title = self.get_element("news_title", root=article).text_content()

            logger.debug(f"{date=} | {picture_url=} | {title=} | {description=}")

            news = News(
                title=title,
                description=description,
                date=date,
                picture_url=picture_url,
            )
            all_news.append(news)

        return all_news
