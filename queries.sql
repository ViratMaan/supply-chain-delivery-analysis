
Supply chain delivery analysis: KPI queries (SQLite)
Table: orders (one row per order item, cancelled items flagged)
is_late = real days > scheduled days, excluding cancelled items


1. Late % and average delivery time by shipping mode
SELECT shipping_mode,
       COUNT(DISTINCT order_id) AS orders,
       ROUND(AVG(is_late) * 100, 1) AS late_pct,
       ROUND(AVG(real_days), 2) AS avg_days
FROM orders
WHERE is_canceled = 0
GROUP BY shipping_mode
ORDER BY late_pct DESC;

2. Late rate by region, and each region's share of all late items
SELECT order_region,
       COUNT(*) AS items,
       ROUND(AVG(is_late) * 100, 1) AS late_pct,
       ROUND(SUM(is_late) * 100.0 / (SELECT SUM(is_late) FROM orders), 1) AS share_of_all_late_pct
FROM orders
WHERE is_canceled = 0
GROUP BY order_region
ORDER BY share_of_all_late_pct DESC;

3. Profit sitting on late items, by product category (top 10)
SELECT category_name,
       COUNT(*) AS items,
       ROUND(AVG(is_late) * 100, 1) AS late_pct,
       ROUND(SUM(CASE WHEN is_late = 1 THEN profit ELSE 0 END), 0) AS profit_on_late_items
FROM orders
WHERE is_canceled = 0
GROUP BY category_name
ORDER BY profit_on_late_items DESC
LIMIT 10;

4. Monthly trend of orders and late %
SELECT SUBSTR(order_date, 1, 7) AS month,
       COUNT(DISTINCT order_id) AS orders,
       ROUND(AVG(is_late) * 100, 1) AS late_pct
FROM orders
WHERE is_canceled = 0
GROUP BY month
ORDER BY month;

5. Does the destination country's World Bank logistics score explain lateness?
SELECT CASE WHEN lpi_score >= 3.5 THEN 'High LPI (3.5+)'
            WHEN lpi_score >= 3.0 THEN 'Medium LPI (3.0 to 3.5)'
            WHEN lpi_score IS NOT NULL THEN 'Low LPI (<3.0)'
            ELSE 'No score' END AS lpi_band,
       COUNT(*) AS items,
       ROUND(AVG(is_late) * 100, 1) AS late_pct
FROM orders
WHERE is_canceled = 0
GROUP BY lpi_band;

6. Share of delivered items vs share of late items, by shipping mode
SELECT shipping_mode,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders WHERE is_canceled = 0), 1) AS share_of_items_pct,
       ROUND(SUM(is_late) * 100.0 / (SELECT SUM(is_late) FROM orders), 1) AS share_of_late_pct
FROM orders
WHERE is_canceled = 0
GROUP BY shipping_mode;

7. Late % by shipping mode within each region
(shows that mode, not region, drives lateness)
SELECT order_region,
  ROUND(AVG(CASE WHEN shipping_mode='First Class'    THEN is_late END)*100,1) AS first_class,
  ROUND(AVG(CASE WHEN shipping_mode='Second Class'   THEN is_late END)*100,1) AS second_class,
  ROUND(AVG(CASE WHEN shipping_mode='Standard Class' THEN is_late END)*100,1) AS standard_class
FROM orders
WHERE is_canceled = 0
GROUP BY order_region;

8. Data quality check: countries with no LPI score after the join
SELECT order_country, COUNT(*) AS items
FROM orders
WHERE lpi_score IS NULL AND is_canceled = 0
GROUP BY order_country
ORDER BY items DESC;