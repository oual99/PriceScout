from src.tools.tools import web_search, scrape_url

# res = web_search("PS5 slim digital prix maroc")
# print(res)

url = "https://micromagma.ma/consoles"
scraped_content = scrape_url.invoke(url)
print(scraped_content)