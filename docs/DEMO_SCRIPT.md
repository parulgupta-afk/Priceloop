# PriceLoop — Demo script (2–3 minutes)

Use a live environment with `demo@priceloop.ai` / seeded books.toscrape data when possible.

## Flow

1. **Login** (15s)  
   Show AuthScreen → JWT session → dashboard shell.

2. **Catalog** (20s)  
   Open product list from API (not mock Sony cards).  
   Open one books.toscrape product → listings → last scraped price.

3. **History & analytics** (30s)  
   Price history chart / table from observations.  
   Call out min/max/avg and % change from **stored** data.

4. **Anomaly** (20s)  
   Open anomalies endpoint or UI badge.  
   Say: “Statistical only — not automatically a deal.”

5. **Alert** (20s)  
   Create PRICE_DROP_PCT alert → evaluate-deduped once.

6. **AI analyst** (40s)  
   Ask: “Which products had unusual price moves?”  
   Show **answer + tool_trace + limitations**.  
   Emphasize: tools are user-scoped; no free-form SQL.

7. **Forecast** (15s)  
   Open forecast → read `label: experimental` and disclaimer.

8. **Close** (10s)  
   Mention Docker, CI, rate limits, multi-tenant isolation.

## Do not claim

- Live Amazon/Walmart scraping without permitted APIs  
- Production accuracy of forecasts  
- That mock UI prices are real market data  
