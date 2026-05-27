# Apache Spark

Loaded by Apply when Spark jobs are detected.

## Version baseline

Spark 3.5.x. Declare: Scala or PySpark; cluster manager (Databricks, EMR, GKE Spark Operator, standalone).

## Core concepts

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder \
    .appName("MyJob") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()

# Read
df = spark.read.parquet("s3://bucket/path/")

# Transform (lazy — no execution yet)
result = df \
    .filter(F.col("status") == "active") \
    .groupBy("user_id") \
    .agg(F.sum("amount").alias("total_amount")) \
    .where(F.col("total_amount") > 100)

# Write (triggers execution)
result.write \
    .mode("overwrite") \
    .partitionBy("date") \
    .parquet("s3://bucket/output/")
```

## Lazy evaluation and the DAG

Spark builds a DAG of transformations. Nothing executes until an action (`write`, `count`, `collect`, `show`).

- **Transformations**: `filter`, `select`, `groupBy`, `join` — lazy
- **Actions**: `write`, `count`, `collect`, `show` — trigger execution

`collect()` brings all data to the driver — only use for small results. Use `write` for large outputs.

## Partitioning and shuffle

Shuffle (redistributing data across nodes) is expensive. Minimize it:

```python
# Bad: join on non-partitioned keys causes shuffle
result = df1.join(df2, "user_id")

# Better: broadcast join for small tables
from pyspark.sql.functions import broadcast
result = df1.join(broadcast(df2), "user_id")

# For large joins: repartition before join
df1_repart = df1.repartition(200, "user_id")
df2_repart = df2.repartition(200, "user_id")
result = df1_repart.join(df2_repart, "user_id")
```

Spec must declare: partition count, join strategy for large-to-large joins, and expected shuffle size.

## Adaptive Query Execution (AQE)

AQE is enabled in Spark 3.2+. It automatically:
- Merges small partitions after shuffle
- Converts sort-merge joins to broadcast joins when one side is small
- Optimizes skewed joins

Enable: `spark.sql.adaptive.enabled=true` (declare in spec).

## Skew handling

Data skew: one partition has significantly more data than others, causing one task to run much longer.

```python
# Detect skew: check partition sizes
df.groupBy(spark_partition_id()).count().show()

# Mitigate: salting
import random

df_salted = df.withColumn("salt", (F.rand() * 10).cast("int"))
df_salted.groupBy("user_id", "salt").agg(...)
```

Spec must identify: known skew keys; mitigation strategy.

## Performance configuration

Spec must declare:
- `spark.executor.memory`: memory per executor
- `spark.executor.cores`: cores per executor
- `spark.sql.shuffle.partitions`: default 200; set to 2-3x number of executors for large jobs
- `spark.dynamicAllocation.enabled`: true for variable workloads

## Idempotency in Spark

```python
# Write mode overwrite: safe for full recomputation
df.write.mode("overwrite").parquet(output_path)

# Overwrite partition: overwrite only affected partition
spark.conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")
df.write.mode("overwrite").partitionBy("date").parquet(output_path)
```

Dynamic partition overwrite is the standard idempotency pattern for date-partitioned Spark jobs.

## Testing

```python
# PySpark testing with pytest
from pyspark.sql import SparkSession
import pytest

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[1]").appName("test").getOrCreate()

def test_filter_active_users(spark):
    data = [("u1", "active"), ("u2", "inactive")]
    df = spark.createDataFrame(data, ["user_id", "status"])
    result = filter_active_users(df)
    assert result.count() == 1
    assert result.first()["user_id"] == "u1"
```

Unit test transformations in isolation with `local[1]` SparkSession. Integration tests run on a real cluster.
