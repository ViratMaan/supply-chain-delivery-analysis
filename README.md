# Supply Chain Delivery Analysis: Is Lateness a Logistics Problem or a Promise Problem?

I built this project to answer one question: **when orders arrive late, is it because the logistics are failing, or because the delivery promises are unrealistic?**

The short answer from this data is that the promises are the main problem. Late rates barely move across regions, product categories, months or country logistics scores. They change massively with **shipping mode**.

![Dashboard](dashboard.png)

## What I found

1. **First Class is promised in 1 day but always takes 2 days, so it is late 100% of the time.** Every single First Class item in the data takes exactly 2 days. Nothing about the operation is inconsistent here. The promise is simply wrong. If the promise were 2 days, its late rate would drop to 0%.
2. **Second Class delivers at the same speed as Standard Class** (3.99 days on average for both) but promises 2 days instead of 4. That is why it is 79.8% late versus 39.8% for Standard. Either the product is mispriced or it needs a real operational fix.
3. **First and Second Class together are 35% of delivered items but 54% of late items.** Standard Class is 60% of items and 41% of late items.
4. **Geography, category, time and country logistics quality do not explain lateness.** Late rates stay between about 52% and 60% across all regions, between 53% and 58% across categories, and between 55% and 59% across months. The correlation between a country's World Bank logistics score and its late rate is -0.015, which is effectively zero.
5. **Volume is not the cause either.** Monthly order volume rose by roughly 20% from October 2017, and the late rate did not move.

### What I would recommend

- Reset the First Class promise from 1 day to 2 days, and the Same Day promise from 0 to 1 day. In a simple what-if, both drop to 0% late.
- Review whether Second Class is worth selling as a premium product, since it delivers at Standard speed.
- Standard Class is promised at 4 days but delivery times are spread between 2 and 6 days. A 6-day promise would remove its lateness, but that is a commercial decision about how slow the offer looks, not something this data can answer.

## The data

- **DataCo Smart Supply Chain** (Kaggle): 180,519 rows and 53 columns of order data. Download it from Kaggle yourself; I have not included it here.
- **World Bank Logistics Performance Index** (2018), pulled live from the World Bank API with Python. I used it to test whether poor-logistics countries really have more late deliveries.

**Limitations of the data you should know about:**

- There is **no supplier column**, so I could not do supplier-level analysis. I defined risk by shipping mode, region and product category instead.
- The delivery times look partly synthetic. Second and Standard Class are spread almost perfectly evenly across 2 to 6 days, which real logistics data rarely is. I treat the findings as a demonstration of the method, not as claims about a real company.

## How it works

```
DataCo CSV + World Bank API
        |
     Python (pandas)  -> cleaning, merging, risk score, what-if
        |
     SQLite           -> KPI queries and validation
        |
     Power BI         -> dashboard
```

Files:

- `pipeline.py`: loads, cleans, merges, scores and exports everything
- `queries.sql`: the SQL KPI queries I ran in DB Browser
- `supply_chain.pbix`: the Power BI dashboard
- `dashboard.png`: screenshot

To rerun it: put `DataCoSupplyChainDataset.csv` in the same folder, run `pip install pandas requests`, then `python pipeline.py`.

## Data problems I found and how I dealt with them

| Problem | What I did |
|---|---|
| File would not open with the default encoding | Read it with `latin-1` |
| 180,519 rows but only 65,752 orders (each row is an order item) | Count unique `Order Id` for order KPIs, not rows |
| Dates stored as text | Converted with an explicit format so day and month can't be swapped |
| Customer emails and passwords in the file | Dropped them, along with other personal columns |
| One column completely empty, another 86% empty | Dropped both |
| 7,754 cancelled items counted as "not late" in the original flag | Excluded cancelled items from all late rate calculations |
| 4,423 items with a positive gap but not flagged late | Checked them: every one was a cancelled order |
| Country names in Spanish, so the first merge with the World Bank data matched only 73.3% of rows | Matched on ISO3 country codes instead, which brought coverage to 97.7% |
| World Bank list also contains regional groups like "High income" with no country code, which broke the lookup | Kept only rows with a proper 3-letter code |

The country matching fix changed the result. With the 73% match, the correlation between LPI and late rate looked like 0.115. After fixing the join it was -0.015. The first number was a side effect of only matching the larger Western countries.

The remaining 2.3% of rows are territories the World Bank doesn't score (Guadalupe, Martinica and similar) or countries with no 2018 value.

## How I defined the KPIs

- **Late item:** real shipping days are greater than scheduled days, and the item was not cancelled. I used my own definition instead of the dataset's `Late_delivery_risk` flag, because that flag is just a copy of the "Late delivery" status and counts cancelled items as on time.
- **Late %:** late items divided by delivered (non-cancelled) items. Overall this is 57.29%.
- **Risk score** (per shipping mode and region, only groups with at least 500 items): a weighted mix of three things, each scaled from 0 to 1 so they can be added together.
  - 50% late rate
  - 25% average days late
  - 25% profit on late items (the money exposed)

  I picked the 50% because late rate is the main service failure, and the other two measure how bad it is and how much money is at stake.

**How stable is the risk score?** I reran it with different weights. The top 5 or 6 combinations (First and Second Class in Western Europe, Central America and South America) stay at the top under every weighting I tried. Ranks 7 to 10 change, especially when I give late rate more weight (only 6 of 10 stayed in the top 10 at 60/20/20, and 8 of 10 at 40/30/30). So I trust the top of the ranking more than the bottom.

## Checking my own numbers

The late rate by shipping mode (100%, 79.8%, 47.9%, 39.8%) came out identical in pandas, SQL and Power BI. I used that as a check that none of the three tools was doing something silly.

## Known limitations

- The risk score table in Power BI is a finished summary and is not linked to the slicers, so it doesn't change when you filter.
- Some of the very small region and mode groups give noisy percentages (for example Canada and Central Asia have only a few hundred items).
- The what-if only resets the promise. It does not model what a longer promise would do to sales.
- No supplier data, so no supplier performance analysis.

## What I would do next

With real supplier data I would add the supplier level: late rate, lead time variability and cost per supplier, then rank suppliers with the same kind of risk score. I would also compare promised vs. actual lead times per supplier, since this project shows that the promise itself can be the problem.
