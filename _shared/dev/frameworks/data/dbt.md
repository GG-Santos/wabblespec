# dbt (data build tool)

Loaded by Apply when dbt models are detected.

## Version baseline

dbt Core 1.7+ or dbt Cloud. Declare adapter (BigQuery, Snowflake, Redshift, DuckDB, etc.).

## Model structure

```
models/
  staging/          ← source-facing; 1:1 with source tables
    stg_users.sql
    stg_orders.sql
  intermediate/     ← business logic; joins and transforms
    int_user_orders.sql
  marts/            ← consumer-facing; final tables for analytics/BI
    dim_users.sql
    fct_orders.sql
```

Staging models: rename columns, cast types, light cleaning — no joins to other sources.
Intermediate models: joins, aggregations, business logic.
Mart models: final shape for consumption — dimension (dim_) or fact (fct_) tables.

## Model configuration

```sql
-- models/marts/fct_orders.sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='sync_all_columns',
    partition_by={
      "field": "created_date",
      "data_type": "date"
    },
    cluster_by=['user_id']
) }}

select
    order_id,
    user_id,
    created_at::date as created_date,
    total_amount
from {{ ref('int_user_orders') }}

{% if is_incremental() %}
where created_at > (select max(created_at) from {{ this }})
{% endif %}
```

## Materializations

| Materialization | When |
|---|---|
| `view` | Development, rarely queried, staging |
| `table` | Final marts, frequently queried |
| `incremental` | Large tables that grow over time |
| `ephemeral` | CTEs — not persisted; inlined into dependent models |

Incremental models must declare `unique_key` for upsert. Spec must declare materialization for each model and justify incremental models.

## Sources

```yaml
# models/staging/sources.yml
sources:
  - name: raw_data
    database: my_database
    schema: raw
    tables:
      - name: users
        freshness:
          warn_after: {count: 1, period: hour}
          error_after: {count: 24, period: hour}
        loaded_at_field: _loaded_at
```

Sources declare freshness expectations. `dbt source freshness` alerts when data is stale.

## Tests

```yaml
# models/marts/schema.yml
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - not_null
          - unique
      - name: user_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_users')
              field: user_id
      - name: total_amount
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
```

Every mart model must have: `not_null` and `unique` tests on the primary key; `relationships` tests for foreign keys.

## Documentation

```yaml
models:
  - name: fct_orders
    description: "One row per order. Grain: order_id."
    columns:
      - name: order_id
        description: "Unique identifier for the order."
      - name: total_amount
        description: "Total order amount in USD cents."
```

All mart models must have descriptions. `dbt docs generate` + `dbt docs serve` for documentation site.

## CI pipeline

```yaml
# GitHub Actions
- run: dbt deps
- run: dbt compile
- run: dbt test --select staging
- run: dbt run --select staging --target ci
- run: dbt test --select marts --target ci
```

Spec must declare: CI target configuration, which models run in CI, and what a CI failure means for deployment.
