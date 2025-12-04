import streamlit as st
import json
import matplotlib.pyplot as plt

# Load products
with open("products.json", "r") as f:
    products = json.load(f)

st.title("🛍️ Autonomous Shopping Recommender Agent")
st.write("Compare prices, find best deals, with AI reasoning, charts, voice input & alerts 💜")

# User input
product_query = st.text_input("🔍 Enter product name:")
budget = st.number_input("💸 Enter your budget (₹):", min_value=0, value=5000, step=500)

# Search function
def search_products(query, budget):
    results = []
    for product in products:
        if query.lower() in product["name"].lower() and product["price"] <= budget:
            results.append(product)
    return results

# Display results
if st.button("Search"):
    results = search_products(product_query, budget)
    
    if results:
        st.success(f"Found {len(results)} product(s) within your budget!")
        
        # Show results
        for p in results:
            st.write(f"**{p['name']}** - ₹{p['price']} - {p['store']} ({p['category']})")
        
        # Plot bar chart
        names = [p['name'] for p in results]
        prices = [p['price'] for p in results]
        plt.figure(figsize=(8, 4))
        plt.bar(names, prices, color='plum')
        plt.title("Product Prices")
        plt.xlabel("Product")
        plt.ylabel("Price (₹)")
        plt.xticks(rotation=45)
        st.pyplot(plt)
        
    else:
        st.warning("⚠️ No products found. Try another query.")
