"""Manual check of EmbeddingService with a real model on sentences of varying similarity.

Run from code/backend: python -m tests.test_embedding_service
"""

import os

from app.embedding.service import get_embedding_service

os.environ["QDAT_EMBEDDING_MODEL"] = "minilm"

SENTENCES = [
    "I felt really anxious about starting my new job.",
    "Starting a new position made me nervous and stressed.",
    "The manager was supportive and answered all my questions.",
    "My supervisor helped me whenever I had a problem.",
    "The commute to the office takes over an hour each day.",
    "Traffic on the way to work is exhausting.",
    "I love cooking pasta on weekends with my family.",
    "Sunday dinners with relatives are my favorite tradition.",
    "The quarterly budget report is due on Friday.",
    "I feel nervous about working.",
]
QUERY = "feeling nervous about work"

service = get_embedding_service()
vectors = service.embed_text_units(SENTENCES)
query = service.embed_query(QUERY)

print(f"vector length: {len(vectors[0])}\n")
print(f"Query: {QUERY!r}\nSimilarity to each sentence (1.0 = identical meaning):")
scores = [sum(a * b for a, b in zip(query, v)) for v in vectors]
for score, sentence in sorted(zip(scores, SENTENCES), reverse=True):
    print(f"  {score:.3f}  {sentence}")

print("\nSimilarity between sentence pairs:")
for i, j in [(0, 1), (2, 3), (4, 5), (6, 7), (0, 6), (4, 9), (8, 9)]:
    sim = sum(a * b for a, b in zip(vectors[i], vectors[j]))
    print(f"  {sim:.3f}  [{i}] vs [{j}]")
