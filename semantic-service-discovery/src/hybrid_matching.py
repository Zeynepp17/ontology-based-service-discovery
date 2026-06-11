import json
import time
import math
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parents[1]

SERVICES_PATH = BASE_DIR / "data" / "services" / "services.json"
QUERIES_PATH = BASE_DIR / "data" / "queries" / "queries.json"


ALPHA = 0.6  # ontology weight
BETA = 0.4   # keyword weight


ONTOLOGY_PARENTS = {
    "LuxuryHotelService": "HotelService",
    "BudgetHotelService": "HotelService",
    "ResortHotelService": "HotelService",

    "HotelService": "AccommodationService",
    "HostelService": "AccommodationService",
    "ApartmentRentalService": "AccommodationService",
    "VillaRentalService": "AccommodationService",
    "CampingService": "AccommodationService",

    "DomesticFlightService": "FlightService",
    "InternationalFlightService": "FlightService",
    "FlightService": "TransportationService",
    "TrainService": "TransportationService",
    "BusService": "TransportationService",
    "TaxiService": "TransportationService",
    "AirportTransferService": "TransportationService",
    "CarRentalService": "TransportationService",
    "BikeRentalService": "TransportationService",
    "FerryService": "TransportationService",
    "PublicTransportService": "TransportationService",

    "TourGuideService": "TourismService",
    "MuseumRecommendationService": "TourismService",
    "HistoricalPlaceService": "TourismService",
    "CityTourService": "TourismService",
    "EventRecommendationService": "TourismService",
    "RestaurantRecommendationService": "TourismService",
    "AdventureActivityService": "TourismService",
    "CulturalExperienceService": "TourismService",
    "TouristAttractionService": "TourismService",

    "TripPlannerService": "PlanningService",
    "BudgetPlannerService": "PlanningService",
    "RouteOptimizationService": "PlanningService",
    "VacationRecommendationService": "PlanningService",
    "SchedulePlannerService": "PlanningService",

    "VisaApplicationService": "DocumentationService",
    "PassportRenewalService": "DocumentationService",
    "EmbassyAppointmentService": "DocumentationService",
    "TravelDocumentVerificationService": "DocumentationService",

    "TravelInsuranceService": "InsuranceAndPaymentService",
    "BookingCancellationService": "InsuranceAndPaymentService",
    "RefundService": "InsuranceAndPaymentService",
    "CurrencyExchangeService": "InsuranceAndPaymentService",
    "InternationalPaymentService": "InsuranceAndPaymentService",

    "WeatherForecastService": "SafetyAndWeatherService",
    "EmergencyTravelAlertService": "SafetyAndWeatherService",
    "TravelRiskAssessmentService": "SafetyAndWeatherService",

    "AccommodationService": "TravelService",
    "TransportationService": "TravelService",
    "TourismService": "TravelService",
    "PlanningService": "TravelService",
    "DocumentationService": "TravelService",
    "InsuranceAndPaymentService": "TravelService",
    "SafetyAndWeatherService": "TravelService",
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_service_text(service):
    parts = [
        service.get("service_name", ""),
        service.get("category", ""),
        " ".join(service.get("inputs", [])),
        " ".join(service.get("outputs", [])),
        " ".join(service.get("preconditions", [])),
        " ".join(service.get("effects", [])),
        " ".join(service.get("ontology_concepts", [])),
        service.get("text_description", "")
    ]

    return " ".join(parts)


def compute_keyword_scores(query_text, services):
    service_texts = [build_service_text(service) for service in services]
    corpus = [query_text] + service_texts

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    query_vector = tfidf_matrix[0:1]
    service_vectors = tfidf_matrix[1:]

    similarities = cosine_similarity(query_vector, service_vectors).flatten()

    return similarities


def get_ancestors(concept):
    ancestors = []
    current = concept

    while current in ONTOLOGY_PARENTS:
        parent = ONTOLOGY_PARENTS[current]
        ancestors.append(parent)
        current = parent

    return ancestors


def concept_distance(concept_a, concept_b):
    if concept_a == concept_b:
        return 0

    ancestors_a = [concept_a] + get_ancestors(concept_a)
    ancestors_b = [concept_b] + get_ancestors(concept_b)

    min_distance = None

    for index_a, ancestor_a in enumerate(ancestors_a):
        for index_b, ancestor_b in enumerate(ancestors_b):
            if ancestor_a == ancestor_b:
                distance = index_a + index_b

                if min_distance is None or distance < min_distance:
                    min_distance = distance

    return min_distance


def concept_similarity(query_concept, service_concept):
    distance = concept_distance(query_concept, service_concept)

    if distance is None:
        return 0.0

    if distance == 0:
        return 1.0

    if distance == 1:
        return 0.8

    if distance == 2:
        return 0.6

    if distance == 3:
        return 0.4

    return 0.2


def ontology_similarity(query_concepts, service_concepts):
    scores = []

    for query_concept in query_concepts:
        best_score_for_query_concept = 0.0

        for service_concept in service_concepts:
            score = concept_similarity(query_concept, service_concept)
            best_score_for_query_concept = max(best_score_for_query_concept, score)

        scores.append(best_score_for_query_concept)

    if not scores:
        return 0.0

    return sum(scores) / len(scores)


def rank_services_hybrid(query, services, top_k=5):
    keyword_scores = compute_keyword_scores(query["query_text"], services)
    query_concepts = query.get("expected_concepts", [])

    ranked = []

    for index, service in enumerate(services):
        service_concepts = service.get("ontology_concepts", [])

        ontology_score = ontology_similarity(query_concepts, service_concepts)
        keyword_score = keyword_scores[index]

        hybrid_score = (ALPHA * ontology_score) + (BETA * keyword_score)

        ranked.append((service, hybrid_score, ontology_score, keyword_score))

    ranked.sort(key=lambda x: x[1], reverse=True)

    return ranked[:top_k]


def get_relevant_services(query):
    relevant = set()
    relevant.update(query.get("exact_match", []))
    relevant.update(query.get("plugin_match", []))
    relevant.update(query.get("partial_match", []))
    return relevant


def precision_at_k(retrieved_ids, relevant_ids, k):
    top_k = retrieved_ids[:k]
    hit_count = len(set(top_k) & relevant_ids)
    return hit_count / k


def recall_at_k(retrieved_ids, relevant_ids, k):
    top_k = retrieved_ids[:k]

    if not relevant_ids:
        return 0.0

    hit_count = len(set(top_k) & relevant_ids)
    return hit_count / len(relevant_ids)


def f1_score(precision, recall):
    if precision + recall == 0:
        return 0.0

    return 2 * precision * recall / (precision + recall)


def dcg_at_k(retrieved_ids, relevant_ids, k):
    dcg = 0.0

    for index, service_id in enumerate(retrieved_ids[:k], start=1):
        relevance = 1 if service_id in relevant_ids else 0

        if relevance > 0:
            dcg += relevance / math.log2(index + 1)

    return dcg


def ndcg_at_k(retrieved_ids, relevant_ids, k):
    dcg = dcg_at_k(retrieved_ids, relevant_ids, k)

    ideal_hits = min(len(relevant_ids), k)
    ideal_retrieved = list(relevant_ids)[:ideal_hits]

    idcg = dcg_at_k(ideal_retrieved, relevant_ids, k)

    if idcg == 0:
        return 0.0

    return dcg / idcg


def main():
    services = load_json(SERVICES_PATH)
    queries = load_json(QUERIES_PATH)

    k = 5

    total_precision = 0.0
    total_recall = 0.0
    total_f1 = 0.0
    total_ndcg = 0.0
    total_time = 0.0

    print("Hybrid Matching Started")
    print(f"Alpha ontology weight: {ALPHA}")
    print(f"Beta keyword weight: {BETA}")
    print(f"Loaded services: {len(services)}")
    print(f"Loaded queries: {len(queries)}")
    print("=" * 80)

    for query in queries:
        start_time = time.perf_counter()

        results = rank_services_hybrid(query, services, top_k=k)

        elapsed_time = time.perf_counter() - start_time
        total_time += elapsed_time

        retrieved_ids = [service["service_id"] for service, hybrid_score, ontology_score, keyword_score in results]
        relevant_ids = get_relevant_services(query)

        precision = precision_at_k(retrieved_ids, relevant_ids, k)
        recall = recall_at_k(retrieved_ids, relevant_ids, k)
        f1 = f1_score(precision, recall)
        ndcg = ndcg_at_k(retrieved_ids, relevant_ids, k)

        total_precision += precision
        total_recall += recall
        total_f1 += f1
        total_ndcg += ndcg

        print(f"Query ID: {query['query_id']}")
        print(f"Query: {query['query_text']}")
        print(f"Expected concepts: {query.get('expected_concepts', [])}")
        print(f"Relevant services: {sorted(relevant_ids)}")
        print("Top-5 results:")

        for rank, (service, hybrid_score, ontology_score, keyword_score) in enumerate(results, start=1):
            marker = "OK" if service["service_id"] in relevant_ids else "NO"

            print(
                f"{rank}. {service['service_id']} - "
                f"{service['service_name']} | "
                f"Hybrid Score: {hybrid_score:.4f} | "
                f"Ontology: {ontology_score:.4f} | "
                f"Keyword: {keyword_score:.4f} | "
                f"{marker}"
            )

        print(
            f"P@5: {precision:.4f} | "
            f"R@5: {recall:.4f} | "
            f"F1: {f1:.4f} | "
            f"nDCG@5: {ndcg:.4f} | "
            f"Time: {elapsed_time:.6f}s"
        )

        print("-" * 80)

    query_count = len(queries)

    print("\nSUMMARY")
    print("=" * 80)
    print(f"Average Precision@5: {total_precision / query_count:.4f}")
    print(f"Average Recall@5: {total_recall / query_count:.4f}")
    print(f"Average F1: {total_f1 / query_count:.4f}")
    print(f"Average nDCG@5: {total_ndcg / query_count:.4f}")
    print(f"Average Query Time: {total_time / query_count:.6f}s")


if __name__ == "__main__":
    main()