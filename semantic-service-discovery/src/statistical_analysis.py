import json
import math
import random
import csv
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parents[1]

SERVICES_PATH = BASE_DIR / "data" / "services" / "services.json"
QUERIES_PATH = BASE_DIR / "data" / "queries" / "queries.json"
TAXONOMY_PATH = BASE_DIR / "data" / "taxonomy" / "taxonomy_parents.json"

OUTPUT_DIR = BASE_DIR / "results" / "statistical_analysis"
QUERY_LEVEL_CSV = OUTPUT_DIR / "query_level_scores.csv"
SUMMARY_CSV = OUTPUT_DIR / "statistical_summary.csv"

random.seed(42)
np.random.seed(42)


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
        service.get("text_description", ""),
    ]

    return " ".join(parts)


def compute_keyword_scores(query_text, services):
    service_texts = [build_service_text(service) for service in services]
    corpus = [query_text] + service_texts

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    query_vector = tfidf_matrix[0:1]
    service_vectors = tfidf_matrix[1:]

    return cosine_similarity(query_vector, service_vectors).flatten()


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


def rank_keyword(query, services, top_k=10):
    keyword_scores = compute_keyword_scores(query["query_text"], services)

    ranked = sorted(
        zip(services, keyword_scores),
        key=lambda x: x[1],
        reverse=True,
    )

    return ranked[:top_k]


def rank_taxonomy_distance(query, services, top_k=10):
    query_concepts = query.get("expected_concepts", [])

    ranked = []

    for service in services:
        service_concepts = service.get("ontology_concepts", [])
        score = ontology_similarity(query_concepts, service_concepts)
        ranked.append((service, score))

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


def evaluate_query(query, services, method_name):
    eval_k = 5
    retrieval_k = 10

    if method_name == "keyword":
        results = rank_keyword(query, services, top_k=retrieval_k)
    elif method_name == "taxonomy_distance":
        results = rank_taxonomy_distance(query, services, top_k=retrieval_k)
    else:
        raise ValueError(f"Unknown method: {method_name}")

    retrieved_ids = [service["service_id"] for service, score in results]
    relevant_ids = get_relevant_services(query)

    precision_5 = precision_at_k(retrieved_ids, relevant_ids, eval_k)
    precision_10 = precision_at_k(retrieved_ids, relevant_ids, retrieval_k)
    recall_5 = recall_at_k(retrieved_ids, relevant_ids, eval_k)
    f1 = f1_score(precision_5, recall_5)
    ndcg_5 = ndcg_at_k(retrieved_ids, relevant_ids, eval_k)

    return {
        "precision_at_5": precision_5,
        "precision_at_10": precision_10,
        "recall_at_5": recall_5,
        "f1": f1,
        "ndcg_at_5": ndcg_5,
    }


def bootstrap_ci(differences, n_bootstrap=10000, confidence=0.95):
    differences = np.array(differences)
    bootstrap_means = []

    for _ in range(n_bootstrap):
        sample = np.random.choice(differences, size=len(differences), replace=True)
        bootstrap_means.append(np.mean(sample))

    lower_percentile = ((1 - confidence) / 2) * 100
    upper_percentile = (1 - ((1 - confidence) / 2)) * 100

    lower = np.percentile(bootstrap_means, lower_percentile)
    upper = np.percentile(bootstrap_means, upper_percentile)

    return lower, upper


def main():
    services = load_json(SERVICES_PATH)
    queries = load_json(QUERIES_PATH)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    query_level_rows = []

    keyword_f1_scores = []
    taxonomy_f1_scores = []

    keyword_ndcg_scores = []
    taxonomy_ndcg_scores = []

    for query in queries:
        keyword_scores = evaluate_query(query, services, method_name="keyword")
        taxonomy_scores = evaluate_query(query, services, method_name="taxonomy_distance")

        keyword_f1_scores.append(keyword_scores["f1"])
        taxonomy_f1_scores.append(taxonomy_scores["f1"])

        keyword_ndcg_scores.append(keyword_scores["ndcg_at_5"])
        taxonomy_ndcg_scores.append(taxonomy_scores["ndcg_at_5"])

        query_level_rows.append({
            "query_id": query["query_id"],
            "domain": query.get("domain", ""),
            "keyword_f1": keyword_scores["f1"],
            "taxonomy_f1": taxonomy_scores["f1"],
            "f1_difference": taxonomy_scores["f1"] - keyword_scores["f1"],
            "keyword_ndcg_at_5": keyword_scores["ndcg_at_5"],
            "taxonomy_ndcg_at_5": taxonomy_scores["ndcg_at_5"],
            "ndcg_difference": taxonomy_scores["ndcg_at_5"] - keyword_scores["ndcg_at_5"],
        })

    f1_differences = np.array(taxonomy_f1_scores) - np.array(keyword_f1_scores)
    ndcg_differences = np.array(taxonomy_ndcg_scores) - np.array(keyword_ndcg_scores)

    wilcoxon_f1 = wilcoxon(taxonomy_f1_scores, keyword_f1_scores, alternative="greater")
    wilcoxon_ndcg = wilcoxon(taxonomy_ndcg_scores, keyword_ndcg_scores, alternative="greater")

    f1_ci_lower, f1_ci_upper = bootstrap_ci(f1_differences)
    ndcg_ci_lower, ndcg_ci_upper = bootstrap_ci(ndcg_differences)

    summary = {
        "comparison": "taxonomy_distance_vs_keyword",
        "query_count": len(queries),
        "mean_keyword_f1": float(np.mean(keyword_f1_scores)),
        "mean_taxonomy_f1": float(np.mean(taxonomy_f1_scores)),
        "mean_f1_difference": float(np.mean(f1_differences)),
        "f1_bootstrap_ci_lower": float(f1_ci_lower),
        "f1_bootstrap_ci_upper": float(f1_ci_upper),
        "wilcoxon_f1_statistic": float(wilcoxon_f1.statistic),
        "wilcoxon_f1_p_value": float(wilcoxon_f1.pvalue),
        "mean_keyword_ndcg_at_5": float(np.mean(keyword_ndcg_scores)),
        "mean_taxonomy_ndcg_at_5": float(np.mean(taxonomy_ndcg_scores)),
        "mean_ndcg_difference": float(np.mean(ndcg_differences)),
        "ndcg_bootstrap_ci_lower": float(ndcg_ci_lower),
        "ndcg_bootstrap_ci_upper": float(ndcg_ci_upper),
        "wilcoxon_ndcg_statistic": float(wilcoxon_ndcg.statistic),
        "wilcoxon_ndcg_p_value": float(wilcoxon_ndcg.pvalue),
    }

    with open(QUERY_LEVEL_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "query_id",
                "domain",
                "keyword_f1",
                "taxonomy_f1",
                "f1_difference",
                "keyword_ndcg_at_5",
                "taxonomy_ndcg_at_5",
                "ndcg_difference",
            ],
        )
        writer.writeheader()
        writer.writerows(query_level_rows)

    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(summary.keys()))
        writer.writeheader()
        writer.writerow(summary)

    print("Statistical Analysis Completed")
    print("=" * 90)
    print(f"Comparison: {summary['comparison']}")
    print(f"Query count: {summary['query_count']}")

    print("\nF1-score comparison")
    print(f"Mean Keyword F1: {summary['mean_keyword_f1']:.4f}")
    print(f"Mean Taxonomy-Distance F1: {summary['mean_taxonomy_f1']:.4f}")
    print(f"Mean F1 Difference: {summary['mean_f1_difference']:.4f}")
    print(
        f"Bootstrap 95% CI for F1 Difference: "
        f"[{summary['f1_bootstrap_ci_lower']:.4f}, {summary['f1_bootstrap_ci_upper']:.4f}]"
    )
    print(f"Wilcoxon F1 statistic: {summary['wilcoxon_f1_statistic']:.4f}")
    print(f"Wilcoxon F1 p-value: {summary['wilcoxon_f1_p_value']:.8f}")

    print("\nnDCG@5 comparison")
    print(f"Mean Keyword nDCG@5: {summary['mean_keyword_ndcg_at_5']:.4f}")
    print(f"Mean Taxonomy-Distance nDCG@5: {summary['mean_taxonomy_ndcg_at_5']:.4f}")
    print(f"Mean nDCG@5 Difference: {summary['mean_ndcg_difference']:.4f}")
    print(
        f"Bootstrap 95% CI for nDCG@5 Difference: "
        f"[{summary['ndcg_bootstrap_ci_lower']:.4f}, {summary['ndcg_bootstrap_ci_upper']:.4f}]"
    )
    print(f"Wilcoxon nDCG@5 statistic: {summary['wilcoxon_ndcg_statistic']:.4f}")
    print(f"Wilcoxon nDCG@5 p-value: {summary['wilcoxon_ndcg_p_value']:.8f}")

    print("\nFiles saved:")
    print(f"Query-level scores: {QUERY_LEVEL_CSV}")
    print(f"Statistical summary: {SUMMARY_CSV}")


if __name__ == "__main__":
    main()