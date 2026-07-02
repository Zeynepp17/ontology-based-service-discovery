# Taxonomy-Distance Based Semantic Service Discovery

This repository contains the source code, dataset, experimental results, and analysis files for a taxonomy-distance based semantic service discovery framework across multiple service domains.

The project evaluates service discovery methods that retrieve and rank relevant services for a given user query by using textual similarity, taxonomy-based semantic relationships, taxonomy-distance scoring, and hybrid semantic-lexical matching.

The revised study focuses on explainable semantic service discovery using structured JSON metadata and hierarchical taxonomy relationships. It does not claim to implement a complete OWL-S, RDF, SPARQL, SHACL, or reasoning-based Semantic Web service infrastructure. Instead, it uses a taxonomy-based semantic hierarchy to represent service concepts and calculate explainable concept-level similarity scores.

---

## Project Scope

The project aims to evaluate and compare the following service discovery strategies:

- Keyword-based service discovery
- Taxonomy-based semantic matching
- Taxonomy-distance based semantic matching
- Hybrid semantic-lexical matching
- Alpha sensitivity analysis
- Distance-score sensitivity analysis
- Statistical significance analysis

The main purpose of the study is to examine whether taxonomy-based and taxonomy-distance based semantic similarity can improve service discovery performance beyond lexical similarity alone.

---

## Dataset

The expanded benchmark dataset consists of:

- 300 service descriptions
- 180 user queries
- 2 service domains: Travel and E-commerce
- Relevance labels: exact match, plugin match, partial match, and irrelevant match

The dataset was constructed as a controlled benchmark dataset to evaluate service discovery methods under clearly defined semantic relationships and relevance labels.

---

## Service Dataset

Each service is represented using structured metadata fields:

- Service ID
- Service name
- Domain
- Category
- Inputs
- Outputs
- Preconditions
- Effects
- Taxonomy concepts
- Text description

The service metadata is used by both lexical and semantic matching methods. Textual fields are used for TF-IDF based lexical similarity, while taxonomy concepts are used for taxonomy-based and taxonomy-distance based semantic matching.

---

## Query Dataset

Each query contains:

- Query ID
- Natural language query text
- Expected taxonomy concepts
- Exact match labels
- Plugin match labels
- Partial match labels
- Irrelevant labels

During evaluation, exact match, plugin match, and partial match services are considered relevant. Irrelevant services are excluded from the relevant set.

---

## Domains

The dataset covers two service domains.

### Travel Domain

The Travel domain includes service categories such as:

- Accommodation Services
- Transportation Services
- Tourism Services
- Planning Services
- Documentation Services
- Insurance and Payment Services
- Safety and Weather Services

Example Travel services include:

- HotelBookingService
- AirportTransferService
- FlightReservationService
- VisaApplicationService
- TravelInsuranceService
- WeatherForecastService

### E-commerce Domain

The E-commerce domain includes service categories such as:

- Product Discovery Services
- Order Management Services
- Payment Services
- Delivery Services
- Return and Refund Services
- Customer Support Services
- Inventory Services

Example E-commerce services include:

- ProductSearchService
- ProductRecommendationService
- OrderTrackingService
- OnlinePaymentService
- ShipmentTrackingService
- RefundRequestService
- CustomerTicketService
- StockAvailabilityService

---

## Implemented Methods

### 1. Keyword-Based Baseline

The keyword-based baseline uses TF-IDF vectorization and cosine similarity to rank services according to textual similarity.

For each service, structured metadata fields are combined into a single text representation. The user query and service texts are then converted into TF-IDF vectors, and cosine similarity is used to calculate lexical similarity.

This method is simple and computationally efficient, but it cannot capture semantic relationships between service concepts.

---

### 2. Taxonomy-Based Matching V1

Taxonomy-Based Matching V1 uses taxonomy concepts and direct semantic relationships between query concepts and service concepts.

The method considers the following relationship types:

- Exact concept match
- Parent-child relationship
- Common ancestor relationship
- Unrelated concepts

This method improves over lexical matching by using concept-level relationships. However, it may assign similar scores to services located under the same taxonomy branch.

---

### 3. Taxonomy-Distance Matching V2

Taxonomy-Distance Matching V2 extends Taxonomy-Based Matching V1 by considering the distance between concepts in the taxonomy hierarchy.

Closer concepts receive higher similarity scores, while more distant concepts receive lower scores.

The default taxonomy-distance scoring scheme is:

| Relationship Type | Similarity Score |
|---|---:|
| Exact concept match | 1.0 |
| One-level distance | 0.8 |
| Two-level distance | 0.6 |
| Three-level distance | 0.4 |
| More distant concepts | 0.2 |
| Unrelated concepts | 0.0 |

These scores were initially defined as heuristic distance-based similarity values. Distance-score sensitivity analysis was conducted to evaluate whether the method depends strongly on this specific scoring scheme.

---

### 4. Hybrid Matching

Hybrid Matching combines taxonomy-distance based semantic similarity with TF-IDF based lexical similarity.

The hybrid score is calculated as:

```text
Score = α × SemanticSim + (1 − α) × LexicalSim
```

where:

- `SemanticSim` is the taxonomy-distance based semantic similarity score.
- `LexicalSim` is the TF-IDF based lexical similarity score.
- `α` controls the contribution of semantic similarity.

The initial hybrid configuration used:

```text
α = 0.6
```

However, alpha sensitivity analysis was conducted by testing α values from 0.0 to 1.0 with increments of 0.1.

---

## Evaluation Metrics

The following evaluation metrics are used:

- Precision@5
- Precision@10
- Recall@5
- F1-score
- nDCG@5
- Average query execution time

Precision@5 and Precision@10 measure the proportion of relevant services among the top retrieved results. Recall@5 measures how many relevant services are retrieved within the top five results. F1-score provides a balanced measure of precision and recall. nDCG@5 evaluates ranking quality by giving higher importance to relevant services appearing at higher positions.

---

## Main Experimental Results

The taxonomy-based and taxonomy-distance based semantic methods achieved the strongest performance on the expanded benchmark dataset.

| Method | Precision@5 | Precision@10 | Recall@5 | F1-score | nDCG@5 |
|---|---:|---:|---:|---:|---:|
| Keyword-Based Baseline | 0.4911 | 0.2711 | 0.3381 | 0.4001 | 0.6166 |
| Taxonomy-Based Matching V1 | 0.9867 | 0.7167 | 0.6853 | 0.8083 | 0.9858 |
| Taxonomy-Distance Matching V2 | 0.9867 | 0.7167 | 0.6853 | 0.8083 | 0.9858 |
| Hybrid Matching α=0.6 | 0.6122 | 0.4389 | 0.4225 | 0.4996 | 0.7115 |
| Optimized Hybrid α=1.0 | 0.9867 | 0.7167 | 0.6853 | 0.8083 | 0.9858 |

The results show that the keyword-based baseline achieved the lowest overall performance. Taxonomy-Based Matching V1 and Taxonomy-Distance Matching V2 substantially improved retrieval effectiveness by using concept-level semantic relationships.

Hybrid Matching with α=0.6 improved over the keyword-based baseline but did not outperform the taxonomy-based semantic methods. Alpha sensitivity analysis showed that the best performance was obtained when α=1.0.

---

## Alpha Sensitivity Analysis

Alpha sensitivity analysis was conducted to examine the effect of the semantic-lexical weighting parameter in the hybrid formula.

The α value was tested from 0.0 to 1.0 with increments of 0.1.

Summary of findings:

- α=0.0 corresponds to lexical-only matching.
- α=1.0 corresponds to semantic-only taxonomy-distance matching.
- Performance generally improved as α increased.
- The best performance was obtained when α=1.0.
- This indicates that taxonomy-distance based semantic similarity was the strongest component in the expanded benchmark dataset.

Best result:

```text
α = 1.0
F1-score = 0.8083
nDCG@5 = 0.9858
```

---

## Distance-Score Sensitivity Analysis

Distance-score sensitivity analysis was conducted to evaluate whether the taxonomy-distance based method depends strongly on the selected similarity score values.

The following scoring schemes were evaluated:

- Current
- Strict
- Soft
- Steep
- Binary-related

The current, strict, soft, and steep schemes produced the same retrieval performance. This indicates that the method is not highly sensitive to the exact numerical values as long as closer concepts receive higher similarity scores than more distant concepts.

However, the binary-related scheme caused a clear performance decrease because it assigns the same similarity value to all related non-exact concepts. This shows that preserving hierarchical distance information is important for effective service ranking.

---

## Statistical Analysis

Statistical significance was evaluated using:

- Wilcoxon signed-rank test
- Bootstrap confidence intervals

The taxonomy-distance based method was compared with the keyword-based baseline.

| Metric | Keyword Baseline | Taxonomy-Distance Method | Mean Difference | Bootstrap 95% CI | Wilcoxon p-value |
|---|---:|---:|---:|---:|---:|
| F1-score | 0.4001 | 0.8083 | 0.4081 | [0.3872, 0.4280] | p < 0.001 |
| nDCG@5 | 0.6172 | 0.9858 | 0.3686 | [0.3464, 0.3897] | p < 0.001 |

The results show that the improvement of the taxonomy-distance based method over the keyword-based baseline is statistically significant.

---

## Project Structure

```text
data/
  services/
    services.json
  queries/
    queries.json
  taxonomy/
    taxonomy_parents.json

docs/
  paper_draft.md

results/
  dataset_validation_summary.json
  sensitivity/
    alpha_sensitivity_results.csv
    distance_score_sensitivity_results.csv
  statistical_analysis/
    query_level_scores.csv
    statistical_summary.csv

src/
  generate_large_dataset_v2.py
  keyword_baseline.py
  ontology_matching.py
  ontology_matching_v2.py
  hybrid_matching.py
  alpha_sensitivity.py
  distance_score_sensitivity.py
  statistical_analysis.py
```

---

## Source Code Description

### Dataset Generation

```text
src/generate_large_dataset_v2.py
```

Generates the expanded benchmark dataset with 300 services and 180 queries across Travel and E-commerce domains.

### Keyword Baseline

```text
src/keyword_baseline.py
```

Implements TF-IDF and cosine similarity based lexical service discovery.

### Taxonomy-Based Matching V1

```text
src/ontology_matching.py
```

Implements taxonomy-based semantic matching using exact match, parent-child relationship, common ancestor relationship, and unrelated concept checks.

### Taxonomy-Distance Matching V2

```text
src/ontology_matching_v2.py
```

Implements taxonomy-distance based semantic matching by assigning similarity scores according to concept distance in the taxonomy hierarchy.

### Hybrid Matching

```text
src/hybrid_matching.py
```

Combines taxonomy-distance based semantic similarity with TF-IDF based lexical similarity.

### Alpha Sensitivity Analysis

```text
src/alpha_sensitivity.py
```

Tests different α values from 0.0 to 1.0 and reports performance changes.

### Distance-Score Sensitivity Analysis

```text
src/distance_score_sensitivity.py
```

Tests alternative taxonomy-distance scoring schemes.

### Statistical Analysis

```text
src/statistical_analysis.py
```

Calculates query-level scores, Wilcoxon signed-rank test results, and bootstrap confidence intervals.

---

## Note on Terminology and File Naming

Some source code files retain their original names:

```text
ontology_matching.py
ontology_matching_v2.py
```

In the revised paper, these methods are referred to as:

```text
Taxonomy-Based Matching V1
Taxonomy-Distance Matching V2
```

The terminology was updated because the implementation uses a taxonomy-based semantic hierarchy rather than a complete OWL/RDF/SPARQL-based ontology infrastructure.

---

## How to Run the Experiments

Run the following commands from the project root directory.

### 1. Generate or validate the expanded dataset

```bash
python src/generate_large_dataset_v2.py
```

### 2. Run the keyword baseline

```bash
python src/keyword_baseline.py
```

### 3. Run taxonomy-based matching V1

```bash
python src/ontology_matching.py
```

### 4. Run taxonomy-distance matching V2

```bash
python src/ontology_matching_v2.py
```

### 5. Run hybrid matching

```bash
python src/hybrid_matching.py
```

### 6. Run alpha sensitivity analysis

```bash
python src/alpha_sensitivity.py
```

### 7. Run distance-score sensitivity analysis

```bash
python src/distance_score_sensitivity.py
```

### 8. Run statistical analysis

```bash
python src/statistical_analysis.py
```

---

## Technologies

The project uses:

- Python
- JSON
- TF-IDF
- Cosine similarity
- Taxonomy-based semantic matching
- Taxonomy-distance scoring
- Wilcoxon signed-rank test
- Bootstrap confidence intervals

Main Python libraries:

- pandas
- numpy
- scikit-learn
- scipy
- matplotlib

---

## Main Contribution

The main contribution of this project is the design and empirical evaluation of an explainable taxonomy-distance based semantic service discovery framework across two service domains.

The project does not claim to introduce a completely new hybrid semantic service discovery paradigm. Instead, it focuses on:

- Structured JSON-based service representation
- Taxonomy-based semantic hierarchy
- Explainable taxonomy-distance scoring
- Multi-domain evaluation
- Alpha sensitivity analysis
- Distance-score sensitivity analysis
- Statistical significance testing

This provides a practical and explainable alternative for service discovery scenarios where full Semantic Web service standards such as OWL-S or SAWSDL are not available.

---

## Repository

The source code, dataset, and experimental results are available in this repository.
