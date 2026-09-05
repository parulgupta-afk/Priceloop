# Database Design — PriceLoop

## ER Diagram (Mermaid)

```mermaid
erDiagram
    USER ||--o{ PRODUCT : owns
    PRODUCT ||--o{ PRODUCT_LISTING : has
    SOURCE ||--o{ PRODUCT_LISTING : provides
    PRODUCT_LISTING ||--o{ PRICE_OBSERVATION : records
    USER ||--o{ ALERT : configures
    PRODUCT ||--o{ AI_INSIGHT : generates
    PRODUCT ||--o{ PRODUCT_MATCH : "matched with"

    USER {
        uuid id PK
        string email UK
        string hashed_password
        string full_name
        enum role
        bool is_active
        bool is_verified
        timestamp created_at
    }

    PRODUCT {
        uuid id PK
        uuid user_id FK
        string name
        string brand
        string model
        string category
        string sku
        string gtin
        text description
        string image_url
        jsonb attributes
        bool is_active
        timestamp created_at
    }

    SOURCE {
        uuid id PK
        string name UK
        string base_url
        bool is_active
        float rate_limit_per_second
    }

    PRODUCT_LISTING {
        uuid id PK
        uuid product_id FK
        uuid source_id FK
        string external_url
        string external_id
        string title
        decimal current_price
        string currency
        enum availability
        float match_confidence
        timestamp last_scraped_at
        bool is_active
    }

    PRICE_OBSERVATION {
        uuid id PK
        uuid listing_id FK
        decimal price
        string currency
        enum availability
        timestamp scraped_at
        jsonb raw_data
    }

    PRODUCT_MATCH {
        uuid id PK
        uuid product_a_id FK
        uuid product_b_id FK
        float confidence
        string method
        bool reviewed
    }

    ALERT {
        uuid id PK
        uuid user_id FK
        uuid product_id FK
        string rule_type
        float threshold
        jsonb channels
        bool is_active
    }

    AI_INSIGHT {
        uuid id PK
        uuid product_id FK
        string type
        string summary
        jsonb evidence
        string recommendation
        float confidence
        timestamp created_at
    }
```

## Core Tables (Current Implementation)

### users
- Authentication & RBAC (USER / ANALYST / ADMIN)

### products
- Canonical product the user wants to track

### sources
- Supported e-commerce sources (amazon, flipkart, demo, …)

### product_listings
- Concrete URL / listing on a source linked to a product

### price_observations
- Time-series price + availability snapshots

## Future Tables (planned)

- scrape_jobs / scrape_results
- product_matches
- alerts / alert_events
- ai_insights
- notifications
- cost_records
- audit_logs

## Notes

- `price_observations` will later be partitioned by time for performance.
- `pgvector` extension is available for embedding-based product matching.
- All monetary values use `Numeric(12, 2)`.
- Timestamps are timezone-aware (UTC).
