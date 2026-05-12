import json
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
        service["service_name"],
        " ".join(service["inputs"]),
        " ".join(service["outputs"]),
        " ".join(service["preconditions"]),
        " ".join(service["effects"]),
        " ".join(service["ontology_concepts"]),
        service["text_description"]
    ]
    return " ".join(parts)


def rank_services_keyword(query_text, services, top_k=5):
    service_texts = [build_service_text(service) for service in services]
    corpus = [query_text] + service_texts

    vectorizer = TfidfVectorizer()
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


def main():
    services = load_json(SERVICES_PATH)
    queries = load_json(QUERIES_PATH)

    for query in queries:
        print("=" * 80)
        print(f"Query ID: {query['query_id']}")
        print(f"Query: {query['query_text']}")
        print("-" * 80)

        results = rank_services_keyword(query["query_text"], services, top_k=5)

        for rank, (service, score) in enumerate(results, start=1):
            print(
                f"{rank}. {service['service_id']} - "
                f"{service['service_name']} | Score: {score:.4f}"
            )


if __name__ == "__main__":
    print("Scrip Started")
    main()