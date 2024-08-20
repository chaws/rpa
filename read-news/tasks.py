from RPA.Excel.Files import Files
from news_reader.npr import Npr
from robocorp import browser, workitems
from robocorp.tasks import task

import requests


def download_file(url, local_filename):
    _8kb = 8192
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=_8kb):
                f.write(chunk)
    return local_filename


def export_to_excel(news):
    data = []
    for n in news:
        # Download picture
        picture_filename = None
        if n.picture_url:
            picture_filename = str(n.id) + ".jpg"
            download_file(n.picture_url, "output/" + picture_filename)

        # Save entry
        data.append({
            "Title": n.title,
            "Date": n.date,
            "Description": n.description or "N/A",
            "Picture filename": picture_filename or "N/A",
            "Count of search phrases": n.count_of_search_phrase,
            "Mentions money": n.mentions_money,
        })

    # Save content to an excel spreadsheet
    lib = Files()
    lib.create_workbook(path="./output/npr_news.xlsx", fmt="xlsx")
    lib.create_worksheet(name="NPR News", content=data, header=True)
    lib.save_workbook()


@task
def read_news():
    """Extract news from and save it to an excel file"""

    browser.configure(
        # Makes execution wait, avoid bot detection
        slowmo=100,
        headless=False,
        browser_engine="firefox",
    )

    # Define some default parameters for local testing
    search = "ai"
    section = "health"
    months_ago = 1
    for item in workitems.inputs:
        if item.payload is None:
            continue

        search = item.payload.get("search") or search
        section = item.payload.get("section") or section
        months_ago = item.payload.get("months_ago") or months_ago

        # For now, only allow 1 payload
        break

    reader = Npr()
    news = reader.search(search, section, months_ago=months_ago)
    export_to_excel(news)
