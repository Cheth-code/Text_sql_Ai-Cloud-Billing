# Technical Note: Metadata Extraction Logic

The semantic metadata layer (`semantic_metadata.json`) is the core of this project and was built using a three-phase process as required by the assignment.

### 1. Phase A: Data Profiling
First, I ran the `profile_data.py` script against the live SQLite database (`cloud_costs.db`). This script performed "query probing" to extract key statistics for important columns:

* **Sample Values:** 5 random, non-null values.
* **Null Percentage:** The percentage of rows where the column was NULL.
* **Distinct Values:** The total count of unique values.

This gave me a clear, data-driven understanding of the table contents and confirmed our mock data was correctly loaded with daily timestamps.

### 2. Phase B: Metadata Enrichment
I used the public documentation links provided in the assignment (FinOps FOCUS, AWS, and Azure) to find the official, human-readable descriptions for key columns like `EffectiveCost`, `UsageAmount`, `ServiceName`, and `MeterCategory`.

### 3. Phase C: Semantic Construction
I combined the profiling data from Phase A and the descriptions from Phase B into the final `semantic_metadata.json` file.

The most important part of this step was adding the **`expert_guidance`** object to each column. This was the critical step to "teach" the LLM how to correctly query the data. This guidance included:

* Telling the LLM to use `substr(BillingPeriodStart, 1, 10)` for daily trends and to *avoid* `strftime()`.
* Guiding it to use `WHERE UsageType LIKE '%BoxUsage%'` to correctly identify EC2 instance types, filtering out other "EC2" costs like EBS or Data Transfer.
* Informing it to `Always use SUM(EffectiveCost)` for all cost analysis.
* Instructing it to use `MeterCategory = 'Virtual Machines'` to identify "compute" cost on Azure.

This semantic file provides the "richness" that allows the LLM to generate correct and reliable queries that go far beyond basic schema knowledge.
