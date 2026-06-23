import json
import time
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parents[1]

SERVICES_PATH = BASE_DIR / "data" / "services" / "services.json"
QUERIES_PATH = BASE_DIR / "data" / "queries" / "queries.json"


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


def get_relevant_services(query):
    relevant = set()

    relevant.update(query.get("exact_match", []))
    relevant.update(query.get("plugin_match", []))
    relevant.update(query.get("partial_match", []))

    return relevant


def rank_services_keyword(query_text, services, top_k=10):
    service_texts = [build_service_text(service) for service in services]
    corpus = [query_text] + service_texts

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    query_vector = tfidf_matrix[0:1]
    service_vectors = tfidf_matrix[1:]

    similarities = cosine_similarity(query_vector, service_vectors).flatten()

    ranked = sorted(
        zip(services, similarities),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked[:top_k]


def precision_at_k(retrieved_ids, relevant_ids, k):
    top_k = retrieved_ids[:k]

    if k == 0:
        return 0.0

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
            dcg += relevance / (index if index == 1 else __import__("math").log2(index + 1))

    return dcg


def ndcg_at_k(retrieved_ids, relevant_ids, k):
    dcg = dcg_at_k(retrieved_ids, relevant_ids, k)

    ideal_hits = min(len(relevant_ids), k)
    ideal_ids = list(relevant_ids)[:ideal_hits]

    idcg = dcg_at_k(ideal_ids, relevant_ids, k)

    if idcg == 0:
        return 0.0

    return dcg / idcg


def main():
    services = load_json(SERVICES_PATH)
    queries = load_json(QUERIES_PATH)

    eval_k = 5
    retrieval_k = 10

    total_precision_5 = 0.0
    total_precision_10 = 0.0
    total_recall_5 = 0.0
    total_f1 = 0.0
    total_ndcg_5 = 0.0
    total_time = 0.0

    print("Keyword-Based Baseline Started")
    print(f"Loaded services: {len(services)}")
    print(f"Loaded queries: {len(queries)}")
    print("=" * 80)

    for query in queries:
        start_time = time.perf_counter()

        # Retrieve top-10 results so that both P@5 and P@10 can be calculated
        results = rank_services_keyword(
            query["query_text"],
            services,
            top_k=retrieval_k
        )

        elapsed_time = time.perf_counter() - start_time
        total_time += elapsed_time

        retrieved_ids = [service["service_id"] for service, score in results]
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

        print(f"Query ID: {query['query_id']}")
        print(f"Query: {query['query_text']}")
        print(f"Relevant services: {sorted(relevant_ids)}")
        print("Top-10 results:")

        for rank, (service, score) in enumerate(results, start=1):
            marker = "OK" if service["service_id"] in relevant_ids else "NO"
            print(
                f"{rank}. {service['service_id']} - "
                f"{service['service_name']} | Score: {score:.4f} | {marker}"
            )

        print(
            f"P@5: {precision_5:.4f} | "
            f"P@10: {precision_10:.4f} | "
            f"R@5: {recall_5:.4f} | "
            f"F1: {f1:.4f} | "
            f"nDCG@5: {ndcg_5:.4f} | "
            f"Time: {elapsed_time:.6f}s"
        )

        print("-" * 80)

    query_count = len(queries)

    print("\nSUMMARY")
    print("=" * 80)
    print(f"Average Precision@5: {total_precision_5 / query_count:.4f}")
    print(f"Average Precision@10: {total_precision_10 / query_count:.4f}")
    print(f"Average Recall@5: {total_recall_5 / query_count:.4f}")
    print(f"Average F1: {total_f1 / query_count:.4f}")
    print(f"Average nDCG@5: {total_ndcg_5 / query_count:.4f}")
    print(f"Average Query Time: {total_time / query_count:.6f}s")
if __name__ == "__main__":
      main()