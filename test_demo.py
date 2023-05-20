import requests
import json
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_clothing_items(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    items = soup.find_all("div", class_="product-item")
    return items


def get_item_description(item):
    description = item.find("div", class_="product-description").text
    return description


def clean_text(text):
    text = text.lower()
    text = " ".join(word for word in text.split() if word not in stopwords.words("english"))
    return text


def get_features(text):
    vectorizer = TfidfVectorizer()
    features = vectorizer.fit_transform([text])
    return features


def get_similarity(text1, text2):
    features1 = get_features(text1)
    features2 = get_features(text2)
    similarity = cosine_similarity(features1, features2)[0][0]
    return similarity


def get_similar_items(text, n=5):
    items = get_clothing_items("https://www.myntra.com/women-clothing")
    descriptions = [get_item_description(item) for item in items]
    cleaned_descriptions = [clean_text(description) for description in descriptions]
    similarities = [get_similarity(text, description) for description in cleaned_descriptions]
    similar_items = sorted(items, key=lambda item: similarities[items.index(item)], reverse=True)[:n]
    return similar_items


def main():
    text = input("Enter a description of a clothing item: ")
    similar_items = get_similar_items(text)
    print("Here are the top 5 most similar items:")
    for item in similar_items:
        print(item.find("a", class_="product-link").get("href"))


if __name__ == "__main__":
    main()
