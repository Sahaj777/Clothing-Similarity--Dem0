import requests
from bs4 import BeautifulSoup
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import FastAPI
import pandas as pd

url = "https://www.myntra.com/women-clothing"
response = requests.get(url)
print("RESPONSE",response)
soup = BeautifulSoup(response.content, "html.parser")

product_cards = soup.find_all("div", class_="product-item")
print("$$$$$", product_cards)
for product_card in product_cards:
    product_title = product_card.find("h2", class_="product-name").text
    product_description = product_card.find("div", class_="product-description").text

    product_features = {
        "product_title": product_title,
        "product_description": product_description    }

    with open("clothing_similarity_data.csv", "a") as f:
        f.write(",".join([str(k) for k in product_features.keys()]) + "\n")
        f.write(",".join([str(v) for v in product_features.values()]) + "\n")

data = pd.read_csv("clothing_similarity_data.csv")

vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(data["product_description"])

cosine_similarities = cosine_similarity(X, X)

def get_similar_products(product_title, n=5):
    index = data[data["product_title"] == product_title].index[0]

    similarities = cosine_similarities[index, :]

    similarities.sort(reverse=True)

    top_n_indices = similarities.argsort()[:n]

    top_n_products = data.iloc[top_n_indices]["product_title"].tolist()

    return top_n_products

top_5_products = get_similar_products("Men's T-Shirt")

print(top_5_products)

app = FastAPI()

@app.get("/similar_products")
async def get_similar_products(product_title: str, n: int = 5):
    top_n_products = get_similar_products(product_title, n)

    return {
        "top_n_products": top_n_products
    }

if __name__ == "__main__":
    app.run(debug=True)