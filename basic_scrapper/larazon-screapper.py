from matplotlib.pyplot import title
from requests_html import HTMLSession
from pymongo import MongoClient
import pymongo
import time
from datetime import datetime
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
collection = db[os.getenv("COLLECTION_NAME")]
try:
    collection.create_index([("url", pymongo.ASCENDING)], unique=True)
except Exception as e:
    print(e)

base_url = "https://www.la-razon.com"
urls = [
    "https://www.la-razon.com/tags/feminicidio/",
    "https://www.la-razon.com/tags/feminicidios/",
]
session = HTMLSession()

for url in urls:
    stop = True
    page = 1
    while stop:
        request_url = url + "page/{}/".format(page)
        print(request_url)
        r = session.get(request_url)
        if r.status_code == 200:
            print(r.status_code)
            div_block = r.html.find("div[class = articles-list]")[0]
            div_article = div_block.find("div[class = article-meta]")
            for div in div_article:
                notas = div.find("a")
                link_nota = notas[0].attrs["href"]
                full_path_url = link_nota

                if (
                    ("/lr-article/" not in full_path_url)
                    and ("/mundo/" not in full_path_url)
                    and ("/voces/" not in full_path_url)
                    and ("/la-revista/" not in full_path_url)
                ):
                    q = session.get(full_path_url)
                    print(full_path_url)
                    if q.status_code == 200:
                        title = q.html.find("h1[class = title]")
                        title = title[0].full_text
                        title = title.replace("“", '"')
                        title = title.replace("”", '"')
                        link_nota_split = link_nota.split("/")
                        section = link_nota_split[3]
                        date_publish = (
                            link_nota_split[4] + link_nota_split[5] + link_nota_split[6]
                        )
                        date_publish = datetime.strptime(date_publish, "%Y%m%d")

                        div_cuerpo = q.html.find("div[class=article-body]")[0]
                        cuerpo_nota = div_cuerpo.find("p")
                        body = [c.full_text.strip() for c in cuerpo_nota]
                        body = [b.replace("“", '"') for b in body]
                        body = [b.replace("”", '"') for b in body]
                        div_tags = q.html.find("div[class=lr-tags-cloud-block]")[0]
                        tags = div_tags.find("a[href*=tag]>li")
                        tags = [t.full_text.lower() for t in tags]
                        articulo = {
                            "url": full_path_url,
                            "title": title,
                            "body": body,
                            "tags": tags,
                            "date_published": date_publish,
                            "section": section,
                            "source": "larazon",
                        }
                        try:
                            collection.insert_one(articulo)
                        except pymongo.errors.DuplicateKeyError:
                            print("Duplicate key")
            page += 1
            time.sleep(5)
            # stop = False
        else:
            stop = False
