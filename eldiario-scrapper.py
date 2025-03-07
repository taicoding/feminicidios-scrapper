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

base_url = "https://www.eldiario.net/"
urls = [
    "https://www.eldiario.net/portal/page/{}/?s=feminicidio",
]
session = HTMLSession()
for url in urls:
    stop_count = 0
    stop = True
    page = 1
    while stop:
        request_url = url.format(page)
        print(request_url)
        r = session.get(request_url)
        if r.status_code == 200:
            print(r.status_code)
            div_result = r.html.find("div[class *= jeg_posts]")[0]
            div_article = div_result.find("h3[class *= jeg_post_title]")
            for div in div_article:
                notas = div.find("a")
                link_nota = notas[0].attrs["href"]
                full_path_url = link_nota
                print(full_path_url)
                q = session.get(full_path_url)
                if q.status_code == 200:
                    title = q.html.find("h1")
                    title = title[0].full_text.strip()
                    title = title.replace("“", '"')
                    title = title.replace("”", '"')
                    link_nota_split = link_nota.split("/")
                    tags = (
                        q.html.find("div[class = jeg_meta_category] >span >a")[0]
                        .text.lower()
                        .split("-")
                    )
                    tags = [t.strip() for t in tags]
                    if len(tags) > 1:
                        section = tags[1]
                    else:
                        section = tags[0]
                    date_publish = (
                        link_nota_split[4] + link_nota_split[5] + link_nota_split[6]
                    )
                    date_publish = datetime.strptime(date_publish, "%Y%m%d")
                    cuerpo_nota = q.html.find("div[class=content-inner ] > p")

                    body = [c.full_text.replace("\n", " ").strip() for c in cuerpo_nota]
                    body = [b.replace("“", '"') for b in body]
                    body = [b.replace("”", '"') for b in body]
                    articulo = {
                        "url": full_path_url,
                        "title": title,
                        "body": body,
                        "tags": tags,
                        "date_published": date_publish,
                        "section": section,
                        "source": "eldiario",
                    }
                    try:
                        collection.insert_one(articulo)
                    except pymongo.errors.DuplicateKeyError:
                        print("Duplicate key")
                        stop_count += 1
            page += 1
            time.sleep(5)
            # stop = False
        else:
            if stop_count > 5:
                stop = False

            stop = False
