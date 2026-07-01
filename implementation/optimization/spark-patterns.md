# Apache Spark Optimization

Production patterns for optimizing Apache Spark jobs including partitioning strategies, memory management, shuffle optimization, and performance tuning.

## Core Concepts

### Spark Execution Model

```
Driver Program
    ↓
Job (triggered by action)
    ↓
Stages (separated by shuffles)
    ↓
Tasks (one per partition)
```

### Key Performance Factors

| Factor            | Impact                | Solution                      |
| ----------------- | --------------------- | ----------------------------- |
| **Shuffle**       | Network I/O, disk I/O | Minimize wide transformations |
| **Data Skew**     | Uneven task duration  | Salting, broadcast joins      |
| **Serialization** | CPU overhead          | Use Kryo, columnar formats    |
| **Memory**        | GC pressure, spills   | Tune executor memory          |
| **Partitions**    | Parallelism           | Right-size partitions         |

## Quick Start

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (SparkSession.builder
    .appName("OptimizedJob")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .config("spark.sql.adaptive.skewJoin.enabled", "true")
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    .config("spark.sql.shuffle.partitions", "200")
    .getOrCreate())

df = (spark.read
    .format("parquet")
    .option("mergeSchema", "false")
    .load("s3://bucket/data/"))

result = (df
    .filter(F.col("date") >= "2024-01-01")
    .select("id", "amount", "category")
    .groupBy("category")
    .agg(F.sum("amount").alias("total")))

result.write.mode("overwrite").parquet("s3://bucket/output/")
```

## Detailed Patterns

### Pattern 1: Optimal Partitioning

```python
def calculate_partitions(data_size_gb: float, partition_size_mb: int = 128) -> int:
    """
    Optimal partition size: 128MB - 256MB
    """
    return max(int(data_size_gb * 1024 / partition_size_mb), 1)

# Repartition for even distribution
df_repartitioned = df.repartition(200, "partition_key")

# Coalesce to reduce partitions (no shuffle)
df_coalesced = df.coalesce(100)

# Partition pruning with predicate pushdown
df = (spark.read.parquet("s3://bucket/data/")
    .filter(F.col("date") == "2024-01-01"))

# Write with partitioning for future queries
(df.write
    .partitionBy("year", "month", "day")
    .mode("overwrite")
    .parquet("s3://bucket/partitioned_output/"))
```

### Pattern 2: Join Optimization

```python
from pyspark.sql import functions as F

# 1. Broadcast Join - Small table joins
small_df = spark.read.parquet("s3://bucket/small_table/")
large_df = spark.read.parquet("s3://bucket/large_table/")

result = large_df.join(
    F.broadcast(small_df),
    on="key",
    how="left"
)

# 2. Sort-Merge Join - Default for large tables
result = large_df1.join(large_df2, on="key", how="inner")

# 3. Bucket Join - Pre-sorted, no shuffle at join time
(df.write
    .bucketBy(200, "customer_id")
    .sortBy("customer_id")
    .mode("overwrite")
    .saveAsTable("bucketed_orders"))

orders = spark.table("bucketed_orders")
customers = spark.table("bucketed_customers")
result = orders.join(customers, on="customer_id")

# 4. Skew Join Handling
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")

# Manual salting for severe skew
def salt_join(df_skewed, df_other, key_col, num_salts=10):
    df_salted = df_skewed.withColumn(
        "salt",
        (F.rand() * num_salts).cast("int")
    ).withColumn(
        "salted_key",
        F.concat(F.col(key_col), F.lit("_"), F.col("salt"))
    )

    df_exploded = df_other.crossJoin(
        spark.range(num_salts).withColumnRenamed("id", "salt")
    ).withColumn(
        "salted_key",
        F.concat(F.col(key_col), F.lit("_"), F.col("salt"))
    )

    return df_salted.join(df_exploded, on="salted_key", how="inner")
```

### Pattern 3: Caching and Persistence

```python
from pyspark import StorageLevel

df = spark.read.parquet("s3://bucket/data/")
df_filtered = df.filter(F.col("status") == "active")

df_filtered.cache()
df_filtered.count()

agg1 = df_filtered.groupBy("category").count()
agg2 = df_filtered.groupBy("region").sum("amount")

df_filtered.unpersist()

# Checkpoint for complex lineage
spark.sparkContext.setCheckpointDir("s3://bucket/checkpoints/")
df_complex = (df
    .join(other_df, "key")
    .groupBy("category")
    .agg(F.sum("amount")))
df_complex.checkpoint()
```

### Pattern 4: Memory Tuning

```python
spark = (SparkSession.builder
    .config("spark.executor.memory", "8g")
    .config("spark.executor.memoryOverhead", "2g")
    .config("spark.memory.fraction", "0.6")
    .config("spark.memory.storageFraction", "0.5")
    .config("spark.sql.shuffle.partitions", "200")
    .config("spark.sql.autoBroadcastJoinThreshold", "50MB")
    .config("spark.sql.files.maxPartitionBytes", "128MB")
    .getOrCreate())

def print_memory_usage(spark):
    sc = spark.sparkContext
    for executor in sc._jsc.sc().getExecutorMemoryStatus().keySet().toArray():
        mem_status = sc._jsc.sc().getExecutorMemoryStatus().get(executor)
        total = mem_status._1() / (1024**3)
        free = mem_status._2() / (1024**3)
        print(f"{executor}: {total:.2f}GB total, {free:.2f}GB free")
```

### Pattern 5: Shuffle Optimization

```python
spark.conf.set("spark.sql.shuffle.partitions", "auto")
spark.conf.set("spark.shuffle.compress", "true")
spark.conf.set("spark.shuffle.spill.compress", "true")

# Pre-aggregate before shuffle
df_optimized = (df
    .groupBy("key", "partition_col")
    .agg(F.sum("value").alias("partial_sum"))
    .groupBy("key")
    .agg(F.sum("partial_sum").alias("total")))

# Use coalesce instead of repartition when reducing partitions
df_reduced = df.coalesce(10)
```

### Pattern 6: Data Format Optimization

```python
# Parquet optimizations
(df.write
    .option("compression", "snappy")
    .option("parquet.block.size", 128 * 1024 * 1024)
    .parquet("s3://bucket/output/"))

# Column pruning
df = (spark.read.parquet("s3://bucket/data/")
    .select("id", "amount", "date"))

# Delta Lake optimizations
(df.write
    .format("delta")
    .option("optimizeWrite", "true")
    .option("autoCompact", "true")
    .mode("overwrite")
    .save("s3://bucket/delta_table/"))

spark.sql("""
    OPTIMIZE delta.`s3://bucket/delta_table/`
    ZORDER BY (customer_id, date)
""")
```

### Pattern 7: Monitoring and Debugging

```python
spark.conf.set("spark.sql.codegen.wholeStage", "true")

df.explain(mode="extended")

def check_partition_skew(df):
    partition_counts = (df
        .withColumn("partition_id", F.spark_partition_id())
        .groupBy("partition_id")
        .count()
        .orderBy(F.desc("count")))

    partition_counts.show(20)

    stats = partition_counts.select(
        F.min("count").alias("min"),
        F.max("count").alias("max"),
        F.avg("count").alias("avg"),
        F.stddev("count").alias("stddev")
    ).collect()[0]

    skew_ratio = stats["max"] / stats["avg"]
    print(f"Skew ratio: {skew_ratio:.2f}x (>2x indicates skew)")
```

## Configuration Cheat Sheet

```python
spark_configs = {
    # Adaptive Query Execution (AQE)
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true",
    "spark.sql.adaptive.skewJoin.enabled": "true",

    # Memory
    "spark.executor.memory": "8g",
    "spark.executor.memoryOverhead": "2g",
    "spark.memory.fraction": "0.6",
    "spark.memory.storageFraction": "0.5",

    # Parallelism
    "spark.sql.shuffle.partitions": "200",
    "spark.default.parallelism": "200",

    # Serialization
    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",

    # Compression
    "spark.io.compression.codec": "lz4",
    "spark.shuffle.compress": "true",

    # Broadcast
    "spark.sql.autoBroadcastJoinThreshold": "50MB",

    # File handling
    "spark.sql.files.maxPartitionBytes": "128MB",
    "spark.sql.files.openCostInBytes": "4MB",
}
```

## Best Practices

### Do's
- **Enable AQE** — Adaptive query execution handles many issues
- **Use Parquet/Delta** — Columnar formats with compression
- **Broadcast small tables** — Avoid shuffle for small joins
- **Monitor Spark UI** — Check for skew, spills, GC
- **Right-size partitions** — 128MB - 256MB per partition

### Don'ts
- **Don't collect large data** — Keep data distributed
- **Don't use UDFs unnecessarily** — Use built-in functions
- **Don't over-cache** — Memory is limited
- **Don't ignore data skew** — It dominates job time
- **Don't use `.count()` for existence** — Use `.take(1)` or `.isEmpty()`
