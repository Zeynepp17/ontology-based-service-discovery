# Error Analysis

This section analyzes the retrieval errors observed across the evaluated approaches: Keyword-Based Baseline, Taxonomy-Based Matching V1, Taxonomy-Distance Matching V2, and Hybrid Matching with alpha = 0.6.

The previous version of the error analysis was based on the initial Travel-only dataset and used the terminology Ontology Matching V1 and Ontology Matching V2. In the revised study, the terminology was updated to Taxonomy-Based Matching V1 and Taxonomy-Distance Matching V2, and the analysis was adapted to the expanded Travel and E-commerce benchmark.

---

## Keyword-Based Baseline Errors

The keyword-based baseline relies entirely on TF-IDF and cosine similarity. Therefore, retrieval decisions are driven by lexical overlap between the query and service descriptions rather than concept-level semantic relationships.

### Error Type 1: Lexical Similarity Without Semantic Understanding

Keyword-based matching may retrieve services that share similar terms with the query but do not represent the intended service functionality.

For example, words such as booking, reservation, ticket, order, delivery, payment, or support may appear in several different service categories. A query related to a transportation service may therefore retrieve another travel service that contains similar vocabulary but satisfies a different user need. Similarly, in the E-commerce domain, payment, delivery, and order-related services may share overlapping terms even when their functional purposes are different.

### Error Type 2: Same Keyword, Different Intent

The same keyword may appear in services with different intentions. For instance, the word ticket may appear in train, bus, ferry, and customer-support services. Similarly, the word order may appear in order tracking, order cancellation, and payment confirmation services. Since TF-IDF does not model semantic intent, it may rank services based on shared vocabulary rather than actual functional relevance.

### Error Type 3: Missing Semantic Relationships

Keyword-based matching cannot identify semantic relationships between concepts if the query and service description use different words. For example, a query about accommodation may be semantically related to hotel, hostel, apartment rental, or villa rental services, even if the exact query terms are not repeated in the service description.

### Overall Findings for Keyword Baseline

Most errors in the keyword-based baseline originate from lexical ambiguity and the inability to capture semantic relationships. Although TF-IDF is useful as a simple and efficient baseline, it is limited when semantically related services use different terms or when different services share the same vocabulary.

---

## Taxonomy-Based Matching V1 Errors

Taxonomy-Based Matching V1 introduces semantic awareness through taxonomy concepts. It considers exact concept matches, parent-child relationships, common ancestor relationships, and unrelated concepts.

### Error Type 1: Similar Scores Within the Same Taxonomy Branch

Taxonomy-Based Matching V1 may assign similar scores to services located under the same parent concept. For example, HotelService, HostelService, ApartmentRentalService, and ResortHotelService are all related to AccommodationService. In the E-commerce domain, ProductSearchService and ProductRecommendationService are both related to ProductDiscoveryService.

### Error Type 2: Limited Ranking Discrimination

Because V1 focuses on whether concepts are semantically related, it may not always provide sufficient discrimination between closely related sibling concepts. This can cause multiple services within the same branch to receive similar scores.

### Error Type 3: Parent Concept Influence

Services under the same broad parent category may be treated as strongly related. For example, FlightService, TrainService, BusService, and AirportTransferService are all connected through TransportationService. Similarly, OrderTrackingService, OrderCancellationService, and CheckoutService are connected through OrderManagementService.

### Overall Findings for Taxonomy-Based Matching V1

Taxonomy-Based Matching V1 improves semantic understanding compared with the keyword baseline. However, because it does not explicitly model different levels of semantic distance, it may produce similar scores for closely related services under the same taxonomy branch.

---

## Taxonomy-Distance Matching V2 Errors

Taxonomy-Distance Matching V2 incorporates taxonomy-distance information into semantic similarity calculation. Closer concepts receive higher similarity scores, while more distant concepts receive lower scores.

### Improvement Over Taxonomy-Based Matching V1

Taxonomy-distance scoring provides a more expressive semantic matching mechanism because it distinguishes exact matches, close concepts, distant concepts, and unrelated concepts. This improves interpretability and makes the ranking process more explainable.

### Error Type 1: Fine-Grained Sibling Concept Confusion

Some remaining errors occur between semantically close sibling concepts. For example, different accommodation-related services may remain close in the ranking because they share the same parent concept. Similarly, product search and product recommendation services may remain close because both belong to the product discovery branch.

### Error Type 2: Same-Domain Over-Retrieval

Taxonomy-distance matching may retrieve neighboring services from the same domain because they are semantically close in the taxonomy hierarchy. For example, tourism-related services such as city tours, museum recommendations, restaurant recommendations, and event recommendations may all receive relatively high scores for tourism-related queries.

### Error Type 3: Strong Alignment with Taxonomy Labels

In the expanded benchmark dataset, Taxonomy-Based Matching V1 and Taxonomy-Distance Matching V2 produced the same aggregate performance. This suggests that the relevance labels are strongly aligned with the taxonomy hierarchy. While this supports semantic evaluation, it may reduce the observable difference between the two semantic matching variants.

### Overall Findings for Taxonomy-Distance Matching V2

Taxonomy-Distance Matching V2 substantially reduces the limitations of lexical matching by using concept-level semantic distance. Its remaining errors are mostly related to fine-grained distinctions between semantically close services rather than confusion between unrelated domains.

---

## Hybrid Matching Errors

Hybrid Matching combines taxonomy-distance based semantic similarity with TF-IDF based lexical similarity. In the fixed hybrid configuration, alpha was set to 0.6.

### Error Type 1: Lexical Noise

Hybrid Matching with alpha = 0.6 improved over the keyword-based baseline, but it did not outperform the taxonomy-based semantic methods. One reason is that the lexical component may introduce noise when service descriptions contain overlapping terms across different service categories.

### Error Type 2: Semantically Close Sibling Concepts

Like the taxonomy-based methods, the hybrid method may retrieve semantically close sibling concepts. For example, several accommodation services may appear together in Travel queries, or several product discovery services may appear together in E-commerce queries.

### Error Type 3: Parameter Sensitivity

The hybrid method is sensitive to the alpha parameter. Alpha sensitivity analysis showed that the best performance was obtained when alpha = 1.0, meaning that the semantic component alone produced the strongest result in the expanded benchmark dataset.

### Overall Findings for Hybrid Matching

Hybrid Matching with alpha = 0.6 improved over the keyword-based baseline but remained below the taxonomy-distance based method. This indicates that lexical similarity can provide useful evidence, but its contribution depends on the weighting parameter and the degree of lexical overlap in service descriptions.

---

## Overall Error Analysis Summary

The error analysis shows a clear difference between lexical and semantic retrieval behavior.

The Keyword-Based Baseline suffers primarily from lexical ambiguity and the inability to capture concept-level relationships. Taxonomy-Based Matching V1 improves semantic awareness by using taxonomy relationships, but it may assign similar scores to services under the same taxonomy branch. Taxonomy-Distance Matching V2 provides a more expressive and explainable semantic matching mechanism by using concept distance in the hierarchy.

Hybrid Matching with alpha = 0.6 improves over the keyword baseline but does not outperform the taxonomy-based semantic methods in the expanded benchmark dataset. The alpha sensitivity results show that taxonomy-distance based semantic similarity is the strongest component, while the lexical component may introduce noise when service descriptions share overlapping terms.

Across the evaluated methods, the remaining errors are mostly related to fine-grained distinctions between semantically close services rather than confusion between unrelated domains. This indicates that the taxonomy-based semantic hierarchy is effective for separating major service categories, while further improvements are needed for more realistic, ambiguous, and fine-grained service discovery scenarios.
