import pandas as pd
import requests
import sqlite3


df = pd.read_csv("DataCoSupplyChainDataset.csv", encoding="latin-1")

print("Duplicate order items:", df.duplicated("Order Item Id").sum())

df["order_date"] = pd.to_datetime(df["order date (DateOrders)"], format="%m/%d/%Y %H:%M")
df["ship_date"] = pd.to_datetime(df["shipping date (DateOrders)"], format="%m/%d/%Y %H:%M")

keep = {
    "Order Id": "order_id",
    "Order Item Id": "order_item_id",
    "order_date": "order_date",
    "ship_date": "ship_date",
    "Shipping Mode": "shipping_mode",
    "Days for shipment (scheduled)": "scheduled_days",
    "Days for shipping (real)": "real_days",
    "Delivery Status": "delivery_status",
    "Market": "market",
    "Order Region": "order_region",
    "Order Country": "order_country",
    "Category Name": "category_name",
    "Customer Segment": "customer_segment",
    "Sales": "sales",
    "Order Profit Per Order": "profit",
}
df = df[list(keep)].rename(columns=keep)

for col in ["shipping_mode", "order_region", "order_country", "category_name"]:
    df[col] = df[col].str.strip()

df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")
df["ship_date"] = df["ship_date"].dt.strftime("%Y-%m-%d")

df["is_canceled"] = (df["delivery_status"] == "Shipping canceled").astype(int)
df["gap"] = df["real_days"] - df["scheduled_days"]
df["is_late"] = ((df["gap"] > 0) & (df["is_canceled"] == 0)).astype(int)


def get_lpi(year):
    url = "https://api.worldbank.org/v2/country/all/indicator/LP.LPI.OVRL.XQ"
    response = requests.get(url, params={"format": "json", "date": year, "per_page": 500}, timeout=30)
    response.raise_for_status()
    _, rows = response.json()
    return pd.DataFrame([
        {"country_en": item["country"]["value"], "iso3": item["countryiso3code"], "lpi_score": item["value"]}
        for item in rows if item["value"] is not None
    ])


lpi = get_lpi(2018)
print("LPI countries retrieved:", len(lpi))

name_map = {
    "Estados Unidos": "United States",
    "Francia": "France",
    "Alemania": "Germany",
    "Reino Unido": "United Kingdom",
    "Brasil": "Brazil",
    "Italia": "Italy",
    "Rusia": "Russian Federation",
    "Corea del Sur": "Korea, Rep.",
    "Países Bajos": "Netherlands",
    "Bélgica": "Belgium",
    "Suecia": "Sweden",
    "Dinamarca": "Denmark",
    "Noruega": "Norway",
    "Polonia": "Poland",
    "Suiza": "Switzerland",
    "Irlanda": "Ireland",
    "Grecia": "Greece",
    "República Dominicana": "Dominican Republic",
    "Venezuela": "Venezuela, RB",
    "Egipto": "Egypt, Arab Rep.",
    "Irán": "Iran, Islamic Rep.",
}
df["country_en"] = df["order_country"].replace(name_map)
df = df.merge(lpi, on="country_en", how="left")
print("Rows after merge:", len(df))

iso_map = {
    "Afganistán": "AFG",
    "Arabia Saudí": "SAU",
    "Argelia": "DZA",
    "Azerbaiyán": "AZE",
    "Bangladés": "BGD",
    "Barbados": "BRB",
    "Baréin": "BHR",
    "Belice": "BLZ",
    "Benín": "BEN",
    "Bielorrusia": "BLR",
    "Bosnia y Herzegovina": "BIH",
    "Botsuana": "BWA",
    "Bután": "BTN",
    "Camboya": "KHM",
    "Camerún": "CMR",
    "Chipre": "CYP",
    "Costa de Marfil": "CIV",
    "Croacia": "HRV",
    "Emiratos Árabes Unidos": "ARE",
    "Eslovaquia": "SVK",
    "Eslovenia": "SVN",
    "España": "ESP",
    "Etiopía": "ETH",
    "Filipinas": "PHL",
    "Finlandia": "FIN",
    "Gabón": "GAB",
    "Guinea Ecuatorial": "GNQ",
    "Haití": "HTI",
    "Hong Kong": "HKG",
    "Hungría": "HUN",
    "Irak": "IRQ",
    "Japón": "JPN",
    "Jordania": "JOR",
    "Kazajistán": "KAZ",
    "Kenia": "KEN",
    "Kirguistán": "KGZ",
    "Laos": "LAO",
    "Lesoto": "LSO",
    "Libia": "LBY",
    "Lituania": "LTU",
    "Luxemburgo": "LUX",
    "Líbano": "LBN",
    "Macedonia": "MKD",
    "Malasia": "MYS",
    "Marruecos": "MAR",
    "Moldavia": "MDA",
    "Mozambique": "MOZ",
    "Myanmar (Birmania)": "MMR",
    "México": "MEX",
    "Namibia": "NAM",
    "Nicaragua": "NIC",
    "Nueva Zelanda": "NZL",
    "Níger": "NER",
    "Omán": "OMN",
    "Pakistán": "PAK",
    "Panamá": "PAN",
    "Papúa Nueva Guinea": "PNG",
    "Perú": "PER",
    "República Centroafricana": "CAF",
    "República Checa": "CZE",
    "República Democrática del Congo": "COD",
    "República de Gambia": "GMB",
    "República del Congo": "COG",
    "Ruanda": "RWA",
    "Rumania": "ROU",
    "Sierra Leona": "SLE",
    "Singapur": "SGP",
    "Siria": "SYR",
    "Somalia": "SOM",
    "Suazilandia": "SWZ",
    "SudAfrica": "ZAF",
    "Sudán": "SDN",
    "Sudán del Sur": "SSD",
    "Surinam": "SUR",
    "Tailandia": "THA",
    "Taiwán": "TWN",
    "Tanzania": "TZA",
    "Tayikistán": "TJK",
    "Trinidad y Tobago": "TTO",
    "Turkmenistán": "TKM",
    "Turquía": "TUR",
    "Túnez": "TUN",
    "Ucrania": "UKR",
    "Uzbekistán": "UZB",
    "Vietnam": "VNM",
    "Yemen": "YEM",
    "Yibuti": "DJI",
    "Zimbabue": "ZWE",
}

print(lpi[lpi["iso3"].duplicated(keep=False)])
lpi_clean = lpi[lpi["iso3"].str.len() == 3].drop_duplicates("iso3")
lpi_by_iso = lpi_clean.set_index("iso3")["lpi_score"]
df["lpi_score"] = df["lpi_score"].fillna(df["order_country"].map(iso_map).map(lpi_by_iso))

print("Rows with an LPI score: {:.1%}".format(df["lpi_score"].notna().mean()))
unmatched = sorted(df.loc[df["lpi_score"].isna(), "order_country"].unique())
print("UNMATCHED:", unmatched)

delivered = df[df["is_canceled"] == 0]

matched = delivered.dropna(subset=["lpi_score"])
by_country = matched.groupby("order_country").agg(
    items=("order_item_id", "count"),
    late_rate=("is_late", "mean"),
    lpi=("lpi_score", "first"),
)
by_country = by_country[by_country["items"] >= 100]
print(by_country[["late_rate", "lpi"]].corr().round(3))

for q in [0.5, 0.8, 0.9]:
    promise = delivered.groupby("shipping_mode")["real_days"].quantile(q)
    new_late = delivered["real_days"] > delivered["shipping_mode"].map(promise)
    result = pd.DataFrame({
        "new_promise_days": promise,
        "late_now": delivered.groupby("shipping_mode")["is_late"].mean(),
        "late_after": new_late.groupby(delivered["shipping_mode"]).mean(),
    }).round(3)
    print(f"\nWhat-if: promise = {int(q * 100)}th percentile")
    print(result)

d = delivered.copy()
d["days_late"] = d["gap"].clip(lower=0)
d["profit_late"] = d["profit"] * d["is_late"]

risk = d.groupby(["shipping_mode", "order_region"]).agg(
    items=("order_item_id", "count"),
    late_rate=("is_late", "mean"),
    avg_days_late=("days_late", "mean"),
    profit_on_late=("profit_late", "sum"),
).reset_index()
risk = risk[risk["items"] >= 500]


def scale(s):
    return (s - s.min()) / (s.max() - s.min())


risk["risk_score"] = 100 * (
    0.50 * scale(risk["late_rate"]) +
    0.25 * scale(risk["avg_days_late"]) +
    0.25 * scale(risk["profit_on_late"])
)
risk = risk.sort_values("risk_score", ascending=False)
print(risk.head(10).round(2))


def top_set(w, n=10):
    s = 100 * (
        w[0] * scale(risk["late_rate"]) +
        w[1] * scale(risk["avg_days_late"]) +
        w[2] * scale(risk["profit_on_late"])
    )
    return set(s.nlargest(n).index)


base = top_set((0.50, 0.25, 0.25))
for w in [(0.40, 0.30, 0.30), (0.34, 0.33, 0.33), (0.60, 0.20, 0.20)]:
    print(w, "->", len(base & top_set(w)), "of 10 stay in the top 10")

conn = sqlite3.connect("supply_chain.db")
df.to_sql("orders", conn, if_exists="replace", index=False)
lpi_clean.to_sql("lpi", conn, if_exists="replace", index=False)
risk.to_sql("risk_scores", conn, if_exists="replace", index=False)
df.to_csv("orders_clean.csv", index=False)
risk.to_csv("risk_scores.csv", index=False)
conn.close()
print("Saved supply_chain.db")