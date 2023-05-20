import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from flask import Flask, request, jsonify
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import nltk
nltk.download('stopwords')
nltk.download('punkt')


app = Flask(__name__)


# Step 1: Data Collection and Preprocessing

def scrape_data():
    url = "https://www.myntra.com/women-clothing"
    response = requests.get(url)
    print("$$$$",response)

    soup = BeautifulSoup(response.content, 'html.parser')
    clothing_data = []

    items = soup.find_all("div", class_="product-item")
    print("$@@@@@@##$####",items)
    for item in items:
        print("ITM",item)
        title = item.find("h2", class_="product-name").text.strip()
        # url = item.find('a', class_='a-link-normal')['href']
        description = item.find("div", class_="product-description").text.strip()

        clothing_item = {
            'title': title,
            'description': description
        }

        print("$$$$$$$$$$$$$$",clothing_item)

        clothing_data.append(clothing_item)
    print(clothing_data)
    return clothing_data

def preprocess_text(text):
    text = re.sub('<.*?>', '', text)
    text = re.sub('[^a-zA-Z0-9\s]', '', text)

    # Convert to lowercase
    text = text.lower()

    # Tokenize the text
    tokens = word_tokenize(text)

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]

    # Stemming
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(token) for token in tokens]

    # Join tokens back into a single string
    preprocessed_text = ' '.join(tokens)

    return preprocessed_text  

# Step 2: Measure Similarity

def extract_features(corpus):
    vectorizer = TfidfVectorizer(preprocessor=preprocess_text)
    features = vectorizer.fit_transform(corpus)
    return vectorizer, features

def compute_similarity(query, vectorizer, features):
    query_vec = vectorizer.transform([query])
    similarity_scores = cosine_similarity(query_vec, features)
    return similarity_scores

# Step 3: Return Ranked Results

def get_top_similar_items(query, data, vectorizer, features, top_n=5):
    similarity_scores = compute_similarity(query, vectorizer, features)
    ranked_indices = similarity_scores.argsort()[0][-top_n:][::-1]
    ranked_items = [data[i] for i in ranked_indices]
    return ranked_items

# Step 4: Deploy the Function

def similarity_search(query):
    # Preprocess the query
    data = scrape_data()
    corpus = [item['description'] for item in data]
    vectorizer, features = extract_features(corpus)

    query = request.json['query']
    ranked_items = get_top_similar_items(query, data, vectorizer, features)

    response_data = {'results': ranked_items}
    return json.dumps(response_data)


# API route for similarity search
@app.route('/similarity-search', methods=['POST'])
def api_similarity_search():
    data = request.get_json()
    query = data['query']
    
    # Scrape data from Amazon
    # amazon_url = 'https://www.amazon.com/s?k=clothing'
    # descriptions, urls = scrape_data(amazon_url)

    # Perform similarity search
    results = similarity_search(query)

    # Return the ranked list of similar item URLs
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)