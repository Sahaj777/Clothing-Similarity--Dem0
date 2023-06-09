from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from flask_ngrok import run_with_ngrok

from flask import Flask,request


app = Flask(__name__)
run_with_ngrok(app)   


@app.route("/",methods=['POST'])
def get_data():
    
    data = request.get_json()
    
    input_product = data['product_name']
    
    input_brand = data['brand_name']
    
    options = webdriver.ChromeOptions()
    options.binary_location= '/usr/bin/google-chrome-stable'
    driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options);
    
    url = "https://www.ajio.com/men-jeans/c/830216001?query=%3Arelevance&gridColumns=5"
   

    driver.get(url)
   


    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    soup = BeautifulSoup(driver.page_source, "html.parser")

    product_cards = soup.find_all("div", class_="item rilrtl-products-list__item item")

    product_name_list = []

    brand_name_list = []

    product_price_list = []

    product_url_list = []

    for product_card in product_cards:

        brand_name = product_card.find("div", class_="brand").text

        product_name = product_card.find("div", class_="nameCls").text

        product_price = product_card.find("span", class_="price").text

        product_url = product_card.find("a", class_="rilrtl-products-list__link").get("href")

        split_value = product_price.split("₹")
        product_price= split_value[1]

        if ',' in product_price:
            product_price = product_price.replace(",", "")

        product_name_list.append(product_name)
        brand_name_list.append(brand_name)
        product_price_list.append(int(product_price))
        product_url_list.append(product_url)

    driver.close()

    output = []

    for x in range(len(product_name_list)):
        if input_product in product_name_list[x].lower() or input_product in product_name_list[x].upper() or input_product in product_name_list[x]:
            if input_brand in brand_name_list[x].lower() or input_brand in brand_name_list[x].upper() or input_brand in brand_name_list[x]:
                list1 = [product_name_list[x],brand_name_list[x],product_price_list[x],product_url_list[x]]
                output.append(list1)

    money_int_values = [item[2] for item in output]

    sorted_money_int_values = sorted(money_int_values)

    sorted_jeans_list = []
    for money_int_value in sorted_money_int_values:
        for item in output:
            if item[2] == money_int_value:
                print(item,'item')
                output_res = {
                    "product_name" : item[0],
                    "brand_name" : item[1],
                    "product_price" : item[2],
                    "product_url" : item[3]
                }
                sorted_jeans_list.append(output_res)
       
    ranked_list = {
        "ranked_products" : sorted_jeans_list
    } 

    return ranked_list



if __name__ == "__main__":
    app.run(port=4040)