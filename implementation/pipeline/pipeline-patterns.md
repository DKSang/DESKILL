# Data Pipeline Architecture Patterns

Scalable, reliable, and cost-effective data pipeline patterns for batch and streaming data processing.

## Architecture Design

### Pattern Selection

| Pattern        | Use Case                                    | Characteristics                        |
| -------------- | ------------------------------------------- | -------------------------------------- |
| **ETL**        | Transform before load, legacy systems       | Heavy pre-processing, smaller target   |
| **ELT**        | Load then transform, modern cloud DW        | Raw data preserved, scalable compute   |
| **Lambda**     | Batch + speed layers, high freshness needs  | Two pipelines, complex to maintain     |
| **Kappa**      | Stream-only, simplified architecture        | Single pipeline, immutable log         |
| **Lakehouse**  | Unified batch/streaming, ACID on object store | Delta/Iceberg/Hudi, ML + analytics   |

### Design Flow

```
sources → ingestion → processing → storage → serving
                            ↓
                    observability touchpoints
```

## Ingestion Patterns

### Batch Incremental Loading

```python
from batch_ingestion import BatchDataIngester
from storage.delta_lake_manager import DeltaLakeManager
from data_quality.expectations_suite import DataQualityFramework

ingester = BatchDataIngester(config={})

df = ingester.extract_from_database(
    connection_string='postgresql://host:5432/db',
    query='SELECT * FROM orders',
    watermark_column='updated_at',
    last_watermark=last_run_timestamp
)

schema = {'required_fields': ['id', 'user_id'], 'dtypes': {'id': 'int64'}}
df = ingester.validate_and_clean(df, schema)

dq = DataQualityFramework()
result = dq.validate_dataframe(df, suite_name='orders_suite', data_asset_name='orders')

delta_mgr = DeltaLakeManager(storage_path='s3://lake')
delta_mgr.create_or_update_table(
    df=df,
    table_name='orders',
    partition_columns=['order_date'],
    mode='append'
)

ingester.save_dead_letter_queue('s3://lake/dlq/orders')
```

### Streaming Ingestion

- Kafka consumers with exactly-once semantics
- Manual offset commits within transactions
- Windowing for time-based aggregations
- Error handling and replay capability

## Orchestration Patterns

### Airflow

- Task groups for logical organization
- XCom for inter-task communication
- SLA monitoring and email alerts
- Incremental execution with execution_date
- Retry with exponential backoff

### Prefect

- Task caching for idempotency
- Parallel execution with .submit()
- Artifacts for visibility
- Automatic retries with configurable delays

## Transformation Patterns

### dbt Layers

- **Staging layer**: incremental materialization, deduplication, late-arriving data handling
- **Marts layer**: dimensional models, aggregations, business logic
- **Tests**: unique, not_null, relationships, accepted_values, custom data quality tests
- **Sources**: freshness checks, loaded_at_field tracking
- **Incremental strategy**: merge or delete+insert

## Storage Strategy

### Delta Lake

- ACID transactions with append/overwrite/merge modes
- Upsert with predicate-based matching
- Time travel for historical queries
- Optimize: compact small files, Z-order clustering
- Vacuum to remove old files

### Apache Iceberg

- Partitioning and sort order optimization
- MERGE INTO for upserts
- Snapshot isolation and time travel
- File compaction with binpack strategy
- Snapshot expiration for cleanup

## Monitoring & Cost Optimization

### Monitoring

- Track: records processed/failed, data size, execution time, success/failure rates
- SNS alerts for critical/warning/info events
- Data freshness checks
- Performance trend analysis

### Cost Optimization

| Strategy | Implementation |
| -------- | -------------- |
| Partitioning | Date/entity-based, keep >1GB per partition |
| File sizes | 512MB-1GB for Parquet |
| Lifecycle policies | Hot (Standard) → Warm (IA) → Cold (Glacier) |
| Compute | Spot for batch, on-demand for streaming, serverless for adhoc |
| Query optimization | Partition pruning, clustering, predicate pushdown |

## Output Deliverables

### 1. Architecture Documentation
- Architecture diagram with data flow
- Technology stack with justification
- Failure modes and recovery strategies

### 2. Implementation Code
- Ingestion: batch/streaming with error handling
- Transformation: dbt models or Spark jobs
- Orchestration: Airflow/Prefect DAGs
- Storage: Delta/Iceberg table management
- Data quality: Great Expectations suites and dbt tests

### 3. Configuration Files
- Orchestration: DAG definitions, schedules, retry policies
- dbt: models, sources, tests, project config
- Infrastructure: Docker Compose, K8s manifests, Terraform
- Environment: dev/staging/prod configs

### 4. Monitoring & Observability
- Metrics: execution time, records processed, quality scores
- Alerts: failures, performance degradation, data freshness
- Dashboards: Grafana/CloudWatch for pipeline health

### 5. Operations Guide
- Deployment procedures and rollback strategy
- Troubleshooting guide for common issues
- Scaling guide for increased volume
- Cost optimization strategies
- Disaster recovery and backup procedures

## Success Criteria

- Pipeline meets defined SLA (latency, throughput)
- Data quality checks pass with >99% success rate
- Automatic retry and alerting on failures
- Comprehensive monitoring shows health and performance
- Documentation enables team maintenance
- Cost optimization reduces infrastructure costs
- Schema evolution without downtime
- End-to-end data lineage tracked
