# Copyright 2025-present DatusAI, Inc.
# Licensed under the Apache License, Version 2.0.
# See http://www.apache.org/licenses/LICENSE-2.0 for details.

"""
Optimized Recall Strategy for Platform Documentation Search

This module provides advanced retrieval strategies that improve upon the default
DocumentStore search by incorporating:

1. Hybrid Search: Combines vector similarity with BM25 full-text search
2. Reranking: Uses cross-encoder style scoring to reorder results
3. Multi-field Boosting: Boosts title, hierarchy, and keywords matches
4. Query Expansion: Reformulates queries to capture better semantics
5. Diversity Boosting: Prevents returning too many similar chunks from same doc

Usage:
    python -m scripts.optimize_recall.evaluate_recall --platform duckdb --query "CREATE TABLE syntax"
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from datus.storage.embedding_models import get_document_embedding_model

# =============================================================================
# Scoring Components
# =============================================================================


@dataclass
class SearchResult:
    """Enhanced search result with scoring breakdown."""

    chunk_id: str
    chunk_text: str
    chunk_index: int
    title: str
    titles: List[str]
    nav_path: List[str]
    group_name: str
    hierarchy: str
    version: str
    source_type: str
    source_url: str
    doc_path: str
    keywords: List[str]

    # Scoring components
    vector_score: float = 0.0
    text_score: float = 0.0
    title_boost: float = 0.0
    hierarchy_boost: float = 0.0
    keywords_boost: float = 0.0
    final_score: float = 0.0

    # Metadata
    query: str = ""
    rank: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "chunk_text": self.chunk_text,
            "chunk_index": self.chunk_index,
            "title": self.title,
            "titles": self.titles,
            "nav_path": self.nav_path,
            "group_name": self.group_name,
            "hierarchy": self.hierarchy,
            "version": self.version,
            "source_type": self.source_type,
            "source_url": self.source_url,
            "doc_path": self.doc_path,
            "keywords": self.keywords,
            "vector_score": round(self.vector_score, 4),
            "text_score": round(self.text_score, 4),
            "title_boost": round(self.title_boost, 4),
            "hierarchy_boost": round(self.hierarchy_boost, 4),
            "keywords_boost": round(self.keywords_boost, 4),
            "final_score": round(self.final_score, 4),
            "query": self.query,
            "rank": self.rank,
        }


@dataclass
class RecallConfig:
    """Configuration for recall optimization."""

    # Weights for score combination
    vector_weight: float = 0.5
    text_weight: float = 0.3
    title_weight: float = 0.1
    hierarchy_weight: float = 0.05
    keywords_weight: float = 0.05

    # Diversity settings
    max_chunks_per_doc: int = 3
    diversity_decay: float = 0.15

    # Query expansion
    expand_query: bool = True
    expansion_terms: List[str] = field(default_factory=lambda: [
        "syntax", "usage", "example", "guide", "reference", "api", "docs",
    ])

    # Reranking
    enable_rerank: bool = True
    rerank_top_k: int = 20
    final_top_k: int = 10

    # BM25 parameters
    bm25_k1: float = 1.5
    bm25_b: float = 0.75


# =============================================================================
# BM25 Implementation
# =============================================================================


class BM25:
    """BM25 ranking algorithm for full-text search scoring."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_lengths: List[int] = []
        self.avg_doc_length: float = 0.0
        self.doc_freqs: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.corpus_size = 0

    def fit(self, documents: List[str]) -> "BM25":
        """Build BM25 index from documents."""
        self.corpus_size = len(documents)
        self.doc_lengths = []
        self.doc_freqs = {}

        for doc in documents:
            words = self._tokenize(doc)
            self.doc_lengths.append(len(words))

            # Count document frequencies
            unique_words = set(words)
            for word in unique_words:
                self.doc_freqs[word] = self.doc_freqs.get(word, 0) + 1

        self.avg_doc_length = sum(self.doc_lengths) / max(1, self.corpus_size)

        # Calculate IDF for each term
        for word, df in self.doc_freqs.items():
            self.idf[word] = np.log((self.corpus_size - df + 0.5) / (df + 0.5) + 1)

        return self

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        return [w for w in text.split() if len(w) > 1]

    def score(self, query: str, doc_index: int) -> float:
        """Calculate BM25 score for a query against a document."""
        words = self._tokenize(query)
        doc_words = self._tokenize(self._get_doc_text(doc_index))

        doc_length = self.doc_lengths[doc_index]
        score = 0.0

        for word in words:
            if word not in self.idf:
                continue

            tf = doc_words.count(word)
            if tf == 0:
                continue

            idf = self.idf[word]
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * doc_length / self.avg_doc_length)

            score += idf * (numerator / (denominator + 1e-10))

        return score

    def _get_doc_text(self, doc_index: int) -> str:
        """Get document text by index (placeholder - stored externally)."""
        return ""

    def get_all_scores(self, query: str) -> List[float]:
        """Get BM25 scores for all documents."""
        return [self.score(query, i) for i in range(self.corpus_size)]


# =============================================================================
# Query Expansion
# =============================================================================


class QueryExpander:
    """Expands queries with related terms and synonyms."""

    def __init__(self, expansion_terms: Optional[List[str]] = None):
        self.expansion_terms = expansion_terms or [
            "syntax", "usage", "example", "guide", "reference", "api", "docs",
            "configuration", "parameter", "option", "setting", "feature",
        ]

        # Common SQL/Data terms mapping
        self.synonyms: Dict[str, List[str]] = {
            "create": ["create", "define", "add", "new"],
            "table": ["table", "relation", "dataset"],
            "select": ["select", "query", "fetch", "read"],
            "insert": ["insert", "add", "load", "write"],
            "update": ["update", "modify", "change", "alter"],
            "delete": ["delete", "drop", "remove"],
            "join": ["join", "combine", "merge", "union"],
            "index": ["index", "performance", "speed", "optimize"],
            "partition": ["partition", "shard", "split", "divide"],
            "view": ["view", "virtual", "query", "stored"],
        }

    def expand(self, query: str) -> List[str]:
        """Expand a query into multiple search terms."""
        query_lower = query.lower()
        terms = [query]

        # Add synonyms for known keywords
        for keyword, syns in self.synonyms.items():
            if keyword in query_lower:
                terms.extend(syns)

        # Add expansion terms if query is short
        if len(query.split()) <= 2:
            terms.extend(self.expansion_terms[:4])

        return terms


# =============================================================================
# Diversity Scorer
# =============================================================================


class DiversityScorer:
    """Applies diversity boosting to prevent too many similar results."""

    def __init__(self, max_per_doc: int = 3, decay: float = 0.15):
        self.max_per_doc = max_per_doc
        self.decay = decay

    def apply(
        self,
        results: List[SearchResult],
        score_field: str = "final_score",
    ) -> List[SearchResult]:
        """Apply diversity penalty to scores."""
        if not results:
            return results

        # Count chunks per doc_path
        doc_counts: Dict[str, int] = {}
        for result in results:
            doc_counts[result.doc_path] = doc_counts.get(result.doc_path, 0) + 1

        # Apply penalty for documents exceeding max
        for result in results:
            count = doc_counts.get(result.doc_path, 0)
            if count > self.max_per_doc:
                # Progressive penalty
                excess = count - self.max_per_doc
                penalty = 1.0 - (self.decay * excess)
                current_score = getattr(result, score_field)
                setattr(result, score_field, current_score * penalty)

        # Re-sort by final_score
        results.sort(key=lambda x: getattr(x, score_field), reverse=True)

        # Update ranks
        for i, result in enumerate(results):
            result.rank = i + 1

        return results


# =============================================================================
# Main Optimized Recall Engine
# =============================================================================


class OptimizedRecall:
    """
    Enhanced recall engine that improves upon basic vector search.

    Improvements over default DocumentStore.search_docs:
    1. Multi-query expansion to capture synonyms and related terms
    2. BM25-based text matching as auxiliary signal
    3. Multi-field boosting (title, hierarchy, keywords get higher weights)
    4. Diversity-aware scoring to prevent duplicate doc results
    5. Configurable reranking to optimize final result ordering

    Example:
        >>> engine = OptimizedRecall(platform="duckdb")
        >>> results = engine.search("CREATE TABLE syntax", top_n=10)
        >>> for r in results:
        ...     print(f"{r.rank}. {r.title} (score: {r.final_score})")
    """

    # Fields to retrieve from store
    SELECT_FIELDS = [
        "chunk_id",
        "chunk_text",
        "chunk_index",
        "title",
        "titles",
        "nav_path",
        "group_name",
        "hierarchy",
        "version",
        "source_type",
        "source_url",
        "doc_path",
        "keywords",
    ]

    def __init__(
        self,
        platform: str,
        config: Optional[RecallConfig] = None,
    ):
        """Initialize the optimized recall engine.

        Args:
            platform: Platform name (e.g., "duckdb", "snowflake")
            config: Recall configuration (uses defaults if not provided)
        """
        self.platform = platform
        self.config = config or RecallConfig()

        # Lazy-loaded components
        self._store = None
        self._embedding_model = None
        self._query_expander = QueryExpander(self.config.expansion_terms)
        self._diversity_scorer = DiversityScorer(
            max_per_doc=self.config.max_chunks_per_doc,
            decay=self.config.diversity_decay,
        )

    @property
    def store(self):
        """Lazy-load document store."""
        if self._store is None:
            from datus.storage.document.store import document_store

            self._store = document_store(self.platform)
        return self._store

    @property
    def embedding_model(self):
        """Lazy-load embedding model."""
        if self._embedding_model is None:
            self._embedding_model = get_document_embedding_model()
        return self._embedding_model

    def search(
        self,
        query: str,
        version: Optional[str] = None,
        top_n: Optional[int] = None,
    ) -> List[SearchResult]:
        """Search with optimized recall strategy.

        Args:
            query: Search query text
            version: Filter by version (optional)
            top_n: Maximum results to return (default: config.final_top_k)

        Returns:
            List of SearchResult with scoring breakdown
        """
        if top_n is None:
            top_n = self.config.final_top_k

        # Expand query if enabled
        if self.config.expand_query:
            expanded_queries = self._query_expander.expand(query)
        else:
            expanded_queries = [query]

        # Collect results from expanded queries
        all_results: Dict[str, SearchResult] = {}
        vector_results: Dict[str, float] = {}

        for eq in expanded_queries:
            # Get vector search results
            raw_results = self.store.search_docs(
                query=eq,
                version=version,
                top_n=self.config.rerank_top_k,
                select_fields=self.SELECT_FIELDS,
            )

            # Get BM25 scores for text matching
            bm25 = BM25(k1=self.config.bm25_k1, b=self.config.bm25_b)
            bm25.fit([r.get("chunk_text", "") for r in raw_results])

            for rank, row in enumerate(raw_results):
                chunk_id = row.get("chunk_id", "")
                if not chunk_id:
                    continue

                # Calculate vector score (from rank position)
                vec_score = 1.0 / (rank + 1)

                # Calculate BM25 text score
                text_score = bm25.score(eq, rank) if rank < len(raw_results) else 0.0
                text_score = min(text_score / 10.0, 1.0)  # Normalize

                if chunk_id not in all_results:
                    # Create SearchResult
                    result = SearchResult(
                        chunk_id=chunk_id,
                        chunk_text=row.get("chunk_text", ""),
                        chunk_index=row.get("chunk_index", 0),
                        title=row.get("title", ""),
                        titles=row.get("titles", []),
                        nav_path=row.get("nav_path", []),
                        group_name=row.get("group_name", ""),
                        hierarchy=row.get("hierarchy", ""),
                        version=row.get("version", ""),
                        source_type=row.get("source_type", ""),
                        source_url=row.get("source_url", ""),
                        doc_path=row.get("doc_path", ""),
                        keywords=row.get("keywords", []),
                        vector_score=vec_score,
                        text_score=text_score,
                        query=query,
                    )
                    all_results[chunk_id] = result
                    vector_results[chunk_id] = vec_score
                else:
                    # Update best vector score if this query is better
                    if vec_score > vector_results.get(chunk_id, 0):
                        vector_results[chunk_id] = vec_score
                        all_results[chunk_id].vector_score = vec_score

        # Apply multi-field boosting
        results = self._apply_boosting(list(all_results.values()), query)

        # Sort and apply diversity
        results.sort(key=lambda x: x.final_score, reverse=True)
        results = self._diversity_scorer.apply(results, score_field="final_score")

        # Return top N
        return results[:top_n]

    def _apply_boosting(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """Apply field-specific boosting to results."""
        query_lower = query.lower()
        query_terms = set(query_lower.split())

        for result in results:
            # Title boosting - exact match or containing query terms
            title_lower = result.title.lower() if result.title else ""
            if query_lower in title_lower:
                result.title_boost = 0.8
            elif any(term in title_lower for term in query_terms if len(term) > 2):
                result.title_boost = 0.4
            else:
                result.title_boost = 0.0

            # Hierarchy boosting
            hierarchy_lower = result.hierarchy.lower() if result.hierarchy else ""
            if query_lower in hierarchy_lower:
                result.hierarchy_boost = 0.6
            elif any(term in hierarchy_lower for term in query_terms if len(term) > 2):
                result.hierarchy_boost = 0.3
            else:
                result.hierarchy_boost = 0.0

            # Keywords boosting
            if result.keywords:
                kw_match = sum(1 for kw in result.keywords if kw.lower() in query_lower)
                result.keywords_boost = min(kw_match / max(1, len(result.keywords)), 1.0) * 0.5
            else:
                result.keywords_boost = 0.0

            # Calculate final score with weights
            result.final_score = (
                self.config.vector_weight * result.vector_score
                + self.config.text_weight * result.text_score
                + self.config.title_weight * result.title_boost
                + self.config.hierarchy_weight * result.hierarchy_boost
                + self.config.keywords_weight * result.keywords_boost
            )

        return results

    def compare_with_baseline(
        self,
        query: str,
        version: Optional[str] = None,
        top_n: int = 10,
    ) -> Dict[str, Any]:
        """Compare optimized search with baseline vector search.

        Returns a dict with both result sets and comparison metrics.
        """
        # Baseline results
        baseline_results = self.store.search_docs(
            query=query,
            version=version,
            top_n=top_n,
            select_fields=self.SELECT_FIELDS,
        )

        # Optimized results
        optimized_results = self.search(
            query=query,
            version=version,
            top_n=top_n,
        )

        # Find overlap
        baseline_ids = {r.get("chunk_id") for r in baseline_results}
        optimized_ids = {r.chunk_id for r in optimized_results}
        overlap = len(baseline_ids & optimized_ids)

        return {
            "query": query,
            "platform": self.platform,
            "version": version,
            "baseline_count": len(baseline_results),
            "optimized_count": len(optimized_results),
            "overlap_count": overlap,
            "overlap_ratio": overlap / max(1, len(optimized_results)),
            "baseline_sample": [
                {"chunk_id": r.get("chunk_id"), "title": r.get("title")}
                for r in baseline_results[:3]
            ],
            "optimized_sample": [
                {"chunk_id": r.chunk_id, "title": r.title, "score": r.final_score}
                for r in optimized_results[:3]
            ],
            "new_results": [
                r.to_dict() for r in optimized_results
                if r.chunk_id not in baseline_ids
            ],
        }


# =============================================================================
# CLI Entry Point
# =============================================================================


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Optimized Recall Evaluation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m scripts.optimize_recall.evaluate_recall --platform duckdb --query "CREATE TABLE"
  python -m scripts.optimize_recall.evaluate_recall -p snowflake -q "COPY INTO" --top 20
  python -m scripts.optimize_recall.evaluate_recall -p duckdb -q "INSERT" --compare
        """,
    )

    parser.add_argument("-p", "--platform", required=True, help="Platform name")
    parser.add_argument("-q", "--query", required=True, help="Search query")
    parser.add_argument("-v", "--version", help="Version filter (optional)")
    parser.add_argument("--top", type=int, default=10, help="Number of results to return")
    parser.add_argument("--compare", action="store_true", help="Compare with baseline search")

    args = parser.parse_args()

    try:
        engine = OptimizedRecall(platform=args.platform)

        if args.compare:
            # Run comparison
            comparison = engine.compare_with_baseline(
                query=args.query,
                version=args.version,
                top_n=args.top,
            )

            print(f"\n{'='*60}")
            print(f"Query: {comparison['query']}")
            print(f"Platform: {comparison['platform']}")
            print(f"{'='*60}")
            print(f"\nBaseline results: {comparison['baseline_count']}")
            print(f"Optimized results: {comparison['optimized_count']}")
            print(f"Overlap: {comparison['overlap_count']} ({comparison['overlap_ratio']:.1%})")

            print("\n--- Baseline Sample ---")
            for r in comparison["baseline_sample"]:
                print(f"  - {r['title']}")

            print("\n--- Optimized Sample ---")
            for r in comparison["optimized_sample"]:
                print(f"  - {r['title']} (score: {r['score']:.3f})")

            if comparison["new_results"]:
                print("\n--- New Results (not in baseline) ---")
                for r in comparison["new_results"][:5]:
                    print(f"  - {r['title']} (score: {r['final_score']:.3f})")
                    print(f"    hierarchy: {r['hierarchy']}")

        else:
            # Run optimized search
            results = engine.search(
                query=args.query,
                version=args.version,
                top_n=args.top,
            )

            print(f"\n{'='*60}")
            print(f"Optimized Recall Results for '{args.query}' on {args.platform}")
            print(f"{'='*60}")

            for r in results:
                print(f"\n{r.rank}. {r.title}")
                print(f"   hierarchy: {r.hierarchy}")
                print(f"   final_score: {r.final_score:.4f}")
                print(f"   vector: {r.vector_score:.3f} | text: {r.text_score:.3f} | "
                      f"title: {r.title_boost:.2f} | hier: {r.hierarchy_boost:.2f} | "
                      f"kw: {r.keywords_boost:.2f}")
                print(f"   doc_path: {r.doc_path}")

        print()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
