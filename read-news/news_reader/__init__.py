from robocorp import browser
import time
import random
import re
from datetime import datetime


# Money has 2 main formats
# - a dollar sign ($) followed by
#   - number, from 1 to 3 digits
#   - optional thousands, as much as it finds. Ex 1,111 or 1,111,111 or 1,111,111,111 etc
#   - optional decimals, up to two digits
# - a number with any amount of digits followd by either "dollars" or "USD" words
MONEY_REGEX = re.compile(r"(\$\d{1,3}(,\d{3})*(\.\d{1,2})?|\d+ (dollars|USD))")


class NewsReader:
    """
    Generic implementation of a news reader using Robocorp framework <https://robocorp.com/docs>.
    Should be good for reading news from any news website. A few examples follow:

    * https://apnews.com/
    * https://aljazeera.com/
    * https://reuters.com/
    * https://gothamist.com/
    * https://latimes.com/
    * https://news.yahoo.com/

    Each website reader is required to inherit this class and implement website-specific methods

    Attributes
    ----------
    url : str
        website url
    search_bar_locator : str
        HTML DOM locator (tag/class/id etc) for the search bar
    sound : str
        the sound that the animal makes
    num_legs : int
        the number of legs the animal has (default 4)
    """

    url = None
    available_sections = []
    locators = {}

    def random_delay(self):
        """Sleep a random amount of seconds (1 to 5) to act as user and not block the website"""
        time.sleep(random.randint(1, 5))

    def get_element(self, locator_name, format_values={}, element=browser.page()):
        """
        Return an element of the current page based of `locator_name`.
        If `format_values` is not empty, it means the final locator
        depends on a custom value
        """
        locator = self.locators[locator_name] if locator_name in self.locators else locator_name
        if len(format_values):
            locator = locator.format(**format_values)
        return element.locator(locator)

    def get_search_bar(self):
        """Retrieve search input bar element"""
        raise NotImplementedError

    def get_search_submit_button(self):
        """Retrieve search submit button element"""
        raise NotImplementedError

    def sort_by_newest(self):
        """Sort news by latest first"""
        raise NotImplementedError

    def filter_by_section(self, section):
        """Filter news by section"""
        raise NotImplementedError

    def collect_news(self, months_ago):
        """Collect all news that are newer than `months_ago`"""
        raise NotImplementedError

    def search(self, search_phrase, section=None, months_ago=0, output_filename=None):
        """
        Main method, that does:

        1. Visit the website
        2. Lookup search bar
        3. Input the value of `search_phrase`
        4. Hit <enter>
        5. If `section` is available, filter by it
        6. Iterate over the findings until `months_ago`
        7. Get the values: title, date, description, and picture (if any)
        8. Go to next page, if available, if not, go to step 10
        9. Repeat 6, 7, and 8
        10. Save everything to an Excel file with the following columns
          - Title
          - Date
          - Description
          - Picture filename
          - Count of search phrases in title and description
          - Mentions money (either title or description contains money)
        """

        # Visit website
        browser.goto(self.url)

        # Find search bar and submit button
        search_bar = self.get_search_bar()
        submit_button = self.get_search_submit_button()

        # Fill in search phrase, typing one character every 100ms (avoid blocking)
        search_bar.type(search_phrase, delay=100)

        # Submit search
        self.random_delay()
        submit_button.click()

        # Sort by newest
        self.random_delay()
        self.sort_by_newest()

        # Filter by section, if any
        if section:
            self.filter_by_section(section)

        # Collect all news up to `months_ago`
        news = self.collect_news(months_ago)
        
        # Set count of search phrase
        for n in news:
            n.set_count_of_search_phrase(search_phrase)

        return news


class News:
    """
    Generic news
    """

    title = None
    date = None
    description = None
    picture_url = None
    count_of_search_phrase = 0

    def __init__(self, title=None, date=None, description=None, picture_url=None):
        self.title = title
        self.date = date
        self.description = description
        self.picture_url = picture_url

    @property
    def content(self):
        content = self.title or ""
        content += self.description or ""
        return content
    
    @property
    def mentions_money(self):
        """
        True or False, depending on whether the title or description contains any amount of money
        
        Possible formats: $11.1 | $111,111.11 | 11 dollars | 11 USD
        """

        if len(self.content) == 0:
            return False

        return MONEY_REGEX.match(content) is not None

    def set_count_of_search_phrase(self, search_phrase):
        self.count_of_search_phrase = len(re.findall(search_phrase, self.content))
