import os
from robocorp.tasks import task
from robocorp import browser
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from RPA.PDF import PDF

from news_reader.reuters import Reuters


http = HTTP()


def export_to_excel(news):
    data = []
    for n in news:
        
        # Download picture
        picture_filename = "output/" + os.path.basename(n.picture_url)
        http.download(url=n.picture_url, to_path=picture_filename, overwrite=True)

        # Save entry
        data.append({
            "Title": n.title,
            "Date": n.date,
            "Description": n.description,
            "Picture filename": picture_filename,
            "Count of search phrases": n.count_of_search_phrase,
            "Mentions money": n.mentions_money,
        })

    # Save content to an excel spreadsheet
    lib = Files()
    lib.create_workbook(path="./output/news.xlsx", content=data, fmt="xlsx")
    lib.save_workbook()


@task
def read_news():
    """Insert the sales data for the week and export it as a PDF"""
    browser.configure(
        # Makes execution wait 1s
        slowmo=1000,
        headless=False,
        #browser_engine="firefox",
    )

    reader = Reuters()
    news = reader.search("brazil+planes", "World")
    export_to_excel(news)
