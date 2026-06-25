import pandas as pd

df = pd.read_csv("OnlineRetail.csv", encoding="latin1")

df["Revenue"] = df["Quantity"] * df["UnitPrice"]
product_revenue = df.groupby("Description")["Revenue"].sum().sort_values(ascending=False)

print("Top 10 Products by Revenue:")
print(product_revenue.head(10))