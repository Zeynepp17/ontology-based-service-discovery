# Error Analysis

This section analyzes the retrieval errors observed across the four evaluated approaches: Keyword-Based Baseline, Ontology Matching V1, Ontology Matching V2, and Hybrid Matching.

---

# Keyword-Based Baseline Errors

The keyword-based baseline relies entirely on TF-IDF and cosine similarity. Consequently, retrieval decisions are driven by lexical overlap rather than semantic understanding.

## Error Type 1: Lexical Similarity Without Semantic Understanding

### Example

Q017 – Book train transportation between cities

Expected:

* TrainTicketBookingService

Retrieved:

* MultiModalTransportPlannerService
* FlightReservationService
* TrainTicketBookingService

### Observation

The model ranked transportation-related services based on shared words such as "transportation" and "cities" rather than identifying the specific transportation mode requested.

### Reason

TF-IDF captures lexical similarity but lacks semantic awareness.

---

## Error Type 2: Same Keyword, Different Intent

### Example

Q021 – Reserve a ferry ticket

Expected:

* FerryTicketService

Retrieved:

* BusReservationService
* FerryTicketService

### Observation

Services sharing the keyword "ticket" received similar rankings despite representing different transportation modes.

### Reason

The model treats shared vocabulary as evidence of relevance without understanding service intent.

---

## Error Type 3: Domain Leakage

### Example

Q025 – Search for local restaurants in a travel destination

Retrieved:

* TravelRiskAssessmentService
* TourGuideBookingService

### Observation

Services from related travel contexts appeared despite not matching the intended restaurant recommendation functionality.

### Reason

Shared travel-related vocabulary influenced retrieval decisions.

---

## Error Type 4: Missing Semantic Relationships

### Example

Q030 – Plan a low budget vacation

Expected:

* BudgetTripPlannerService

Retrieved:

* BudgetAccommodationFinderService

### Observation

The model focused on the term "budget" rather than understanding the planning-related intent.

### Reason

Semantic relationships between concepts are not represented.

---

## Overall Findings for Keyword Baseline

Most errors originate from lexical ambiguity and the inability to capture semantic relationships. Although TF-IDF effectively identifies keyword overlap, it struggles when different services use similar vocabulary.

---

# Ontology Matching V1 Errors

Ontology Matching V1 introduces semantic awareness through ontology concepts but does not consider hierarchical distance between concepts.

## Error Type 1: Uniform Similarity Scores

### Examples

* Q001 – Affordable Accommodation Search
* Q002 – Luxury Hotel Search
* Q003 – Hostel Reservation

### Observation

Many accommodation services received identical ontology scores despite representing different subclasses.

### Reason

Ontology V1 only verifies ontology membership and does not distinguish between sibling concepts.

---

## Error Type 2: Lack of Ranking Discrimination

### Examples

* Q004 – Apartment Rental
* Q011 – Camping Reservation
* Q015 – Airport Transfer

### Observation

Correct services frequently failed to appear at the first position.

### Reason

Services under the same parent concept received identical similarity values.

---

## Error Type 3: Parent-Class Dominance

### Examples

* Q017 – Train Transportation
* Q018 – Public Transportation Routes
* Q019 – Private Driver Service

### Observation

Flight, train, bus and taxi services often appeared with the same ranking score.

### Reason

The algorithm identifies the correct domain but cannot differentiate transportation subclasses.

---

## Error Type 4: Semantic Overgeneralization

### Examples

* Q023 – City Tour
* Q025 – Restaurant Recommendation
* Q027 – Adventure Tourism Activity

### Observation

Most tourism services were considered equally relevant.

### Reason

Only high-level ontology membership was considered.

---

## Overall Findings for Ontology Matching V1

Ontology Matching V1 improves semantic understanding compared with the keyword baseline. However, the absence of ontology-distance information limits ranking quality and causes excessive score ties between related services.

---

# Ontology Matching V2 Errors

Ontology Matching V2 incorporates ontology-distance information into similarity computation.

## Improvement Over Ontology V1

### Examples

* Q004 – Apartment Rental
* Q011 – Camping Reservation
* Q015 – Airport Transfer
* Q016 – Car Rental

### Observation

Correct services were consistently ranked at the first position.

### Reason

Ontology-distance scoring differentiates subclasses from their parent concepts.

---

## Error Type 1: Sibling Concept Confusion

### Examples

* Q001 – Affordable Accommodation Search
* Q002 – Luxury Hotel Search

### Observation

Several hotel-related services still appeared near the top of the ranking.

Examples include:

* FamilyHotelSearchService
* PetFriendlyAccommodationService
* LastMinuteHotelBookingService

### Reason

These concepts remain semantically close within the ontology hierarchy.

---

## Error Type 2: Same-Domain Over-Retrieval

### Examples

* Q023 – City Tour
* Q025 – Restaurant Recommendation
* Q027 – Adventure Tourism Activity

### Observation

Tourism-related services frequently retrieved neighboring tourism concepts.

### Reason

Closely related subclasses still receive high semantic similarity scores.

---

## Error Type 3: Parent Concept Influence

### Examples

* Q015 – Airport Transfer
* Q017 – Train Transportation
* Q021 – Ferry Ticket

### Observation

Alternative transportation services remained highly ranked.

### Reason

Transportation subclasses inherit semantic similarity from the TransportationService parent concept.

---

## Overall Findings for Ontology Matching V2

Ontology-distance scoring significantly improves ranking quality. Most severe ranking issues observed in Ontology Matching V1 are eliminated, and retrieval performance improves substantially.

---

# Hybrid Matching Errors

The Hybrid Matching approach combines ontology similarity with TF-IDF-based lexical similarity.

Average F1 Score: 0.6192

## Error Type 1: Lexical Bias

### Example

Q007 – Pet Friendly Accommodation

Expected:

* PetFriendlyAccommodationService

Retrieved First:

* FamilyHotelSearchService

### Observation

A semantically related but incorrect service was ranked first.

### Reason

Lexical similarity boosted the ranking of a service sharing accommodation-related terminology.

---

## Error Type 2: Semantically Close Sibling Concepts

### Examples

* Q002 – Luxury Hotel Search
* Q023 – Guided City Tour
* Q032 – Vacation Recommendation

### Observation

Services from the same ontology branch frequently appeared together.

Examples include:

* FamilyHotelSearchService
* LastMinuteHotelBookingService
* TourGuideBookingService
* WeekendGetawayPlannerService

### Reason

Sibling concepts share strong semantic relationships.

---

## Error Type 3: Transportation Domain Ambiguity

### Examples

* Q017 – Train Transportation
* Q021 – Ferry Ticket

### Observation

Alternative transportation modes occasionally appeared in the ranking.

Examples include:

* FlightReservationService
* TaxiBookingService
* BusReservationService

### Reason

Transportation services share common ontology ancestors and similar textual descriptions.

---

## Error Type 4: Planning-Service Overlap

### Examples

* Q029 – Personalized Travel Itinerary
* Q031 – Route Optimization

### Observation

Multiple planning services appeared simultaneously in ranking results.

Examples include:

* GroupTravelPlannerService
* VacationRecommendationService
* WeekendGetawayPlannerService

### Reason

Planning concepts are strongly connected within the ontology structure.

---

## Overall Findings for Hybrid Matching

Hybrid Matching achieved the highest overall retrieval performance among all evaluated approaches. Most remaining errors occur between semantically related services rather than between unrelated domains.

---

# Additional Representative Examples

## Tourism Domain Example

Query:
Q025 – Search for local restaurants in a travel destination

Expected:

* RestaurantRecommendationService

Retrieved:

* RestaurantRecommendationService
* TourGuideBookingService
* LocalEventRecommendationService
* CulturalExperienceFinderService
* CityTourReservationService

### Observation

The correct service was ranked first, but semantically related tourism services also appeared in the ranking.

---

## Documentation Domain Example

Query:
Q034 – Apply for a travel visa

Expected:

* VisaApplicationService

Retrieved:

* VisaApplicationService
* EmbassyAppointmentService
* TravelDocumentVerificationService
* PassportRenewalService

### Observation

The target service was correctly identified, while other documentation services received high scores because of their close ontology relationships.

---

## Safety and Weather Domain Example

Query:
Q039 – Get emergency travel alerts for a destination

Expected:

* EmergencyTravelAlertService

Retrieved:

* EmergencyTravelAlertService
* TravelRiskAssessmentService
* WeatherForecastService

### Observation

The system maintained domain consistency and retrieved only safety-related services.

---

# Overall Error Analysis Summary

The error analysis reveals a clear progression across the evaluated approaches.

The Keyword-Based Baseline suffers primarily from lexical ambiguity and the inability to capture semantic relationships. Ontology Matching V1 introduces semantic awareness but struggles to distinguish between closely related concepts because all services within the same ontology branch receive similar scores.

Ontology Matching V2 significantly improves ranking quality through ontology-distance scoring, eliminating many of the ranking ambiguities observed in Ontology Matching V1. Finally, Hybrid Matching achieves the best overall performance by combining semantic similarity with lexical similarity.

Across all experiments, most remaining errors occur between semantically related sibling concepts within the same ontology branch rather than between unrelated domains. This indicates that the proposed ontology successfully separates major service categories while further improvements remain possible for fine-grained concept discrimination.
