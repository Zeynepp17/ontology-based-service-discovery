import json
import time
import math
import csv
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parents[1]

SERVICES_PATH = BASE_DIR / "data" / "services" / "services.json"
QUERIES_PATH = BASE_DIR / "data" / "queries" / "queries.json"
TAXONOMY_PATH = BASE_DIR / "data" / "taxonomy" / "taxonomy_parents.json"

OUTPUT_DIR = BASE_DIR / "results" / "sensitivity"
OUTPUT_CSV = OUTPUT_DIR / "alpha_sensitivity_results.csv"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


ONTOLOGY_PARENTS = load_json(TAXONOMY_PATH)


def build_service_text(service):
    parts = [
        service.get("service_name", ""),
        service.get("domain", ""),
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


def rank_services_hybrid(query, services, alpha, top_k=10):
    beta = 1 - alpha

    keyword_scores = compute_keyword_scores(query["query_text"], services)
    query_concepts = query.get("expected_concepts", [])

    ranked = []

    for index, service in enumerate(services):
        service_concepts = service.get("ontology_concepts", [])

        semantic_score = ontology_similarity(query_concepts, service_concepts)
        lexical_score = keyword_scores[index]

        hybrid_score = (alpha * semantic_score) + (beta * lexical_score)

        ranked.append((service, hybrid_score, semantic_score, lexical_score))

    ranked.sort(key=lambda x: x[1], reverse=True)

    return ranked[:top_k]


def evaluate_alpha(alpha, services, queries):
    eval_k = 5
    retrieval_k = 10

    total_precision_5 = 0.0
    total_precision_10 = 0.0
    total_recall_5 = 0.0
    total_f1 = 0.0
    total_ndcg_5 = 0.0
    total_time = 0.0

    for query in queries:
        start_time = time.perf_counter()

        results = rank_services_hybrid(
            query=query,
            services=services,
            alpha=alpha,
            top_k=retrieval_k
        )

        elapsed_time = time.perf_counter() - start_time
        total_time += elapsed_time

        retrieved_ids = [
            service["service_id"]
            for service, hybrid_score, semantic_score, lexical_score in results
        ]

        relevant_ids = get_relevant_services(query)

        precision_5 = precision_at_k(retrieved_ids, relevant_ids, eval_k)
        precision_10 = precision_at_k(retrieved_ids, relevant_ids, retrieval_k)
        recall_5 = recall_at_k(retrieved_ids, relevant_ids, eval_k)
        f1 = f1_score(precision_5, recall_5)
        ndcg_5 = ndcg_at_k(retrieved_ids, relevant_ids, eval_k)

        total_precision_5 += precision_5
        total_precision_10 += precision_10
        total_recall_5 += recall_5
        total_f1 += f1
        total_ndcg_5 += ndcg_5

    query_count = len(queries)

    return {
        "alpha": alpha,
        "beta": 1 - alpha,
        "precision_at_5": total_precision_5 / query_count,
        "precision_at_10": total_precision_10 / query_count,
        "recall_at_5": total_recall_5 / query_count,
        "f1": total_f1 / query_count,
        "ndcg_at_5": total_ndcg_5 / query_count,
        "avg_query_time": total_time / query_count,
    }


def main():
    services = load_json(SERVICES_PATH)
    queries = load_json(QUERIES_PATH)

    alpha_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    results = []

    print("Alpha Sensitivity Analysis Started")
    print(f"Loaded services: {len(services)}")
    print(f"Loaded queries: {len(queries)}")
    print("=" * 90)

    for alpha in alpha_values:
        result = evaluate_alpha(alpha, services, queries)
        results.append(result)

        print(
            f"alpha={result['alpha']:.1f} | "
            f"beta={result['beta']:.1f} | "
            f"P@5={result['precision_at_5']:.4f} | "
            f"P@10={result['precision_at_10']:.4f} | "
            f"R@5={result['recall_at_5']:.4f} | "
            f"F1={result['f1']:.4f} | "
            f"nDCG@5={result['ndcg_at_5']:.4f} | "
            f"Time={result['avg_query_time']:.6f}s"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "alpha",
                "beta",
                "precision_at_5",
                "precision_at_10",
                "recall_at_5",
                "f1",
                "ndcg_at_5",
                "avg_query_time",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    best_by_f1 = max(results, key=lambda x: x["f1"])
    best_by_ndcg = max(results, key=lambda x: x["ndcg_at_5"])

    print("=" * 90)
    print("BEST RESULT BY F1")
    print(
        f"alpha={best_by_f1['alpha']:.1f} | "
        f"F1={best_by_f1['f1']:.4f} | "
        f"P@5={best_by_f1['precision_at_5']:.4f} | "
        f"R@5={best_by_f1['recall_at_5']:.4f} | "
        f"nDCG@5={best_by_f1['ndcg_at_5']:.4f}"
    )

    print("BEST RESULT BY nDCG@5")
    print(
        f"alpha={best_by_ndcg['alpha']:.1f} | "
        f"nDCG@5={best_by_ndcg['ndcg_at_5']:.4f} | "
        f"P@5={best_by_ndcg['precision_at_5']:.4f} | "
        f"R@5={best_by_ndcg['recall_at_5']:.4f} | "
        f"F1={best_by_ndcg['f1']:.4f}"
    )

    print(f"CSV saved to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()