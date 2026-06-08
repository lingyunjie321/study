"""
RAG + Milvus Vector Search Tool
================================
Standalone RAG (Retrieval-Augmented Generation) tool with Milvus vector database
backend. Designed as an additional agent tool compatible with the AEARPO/ARAEPO
framework.

Follows the project's BaseTool interface pattern:
  - name / trigger_tag properties
  - execute(content, **kwargs) -> str

Architecture:
  Document -> TextSplitter -> Embedding -> Milvus Collection
  Query    -> Embedding -> Milvus Search -> Rerank -> Context
  Context  + LLM -> Answer

Dependencies (optional, graceful degradation):
  pip install pymilvus sentence-transformers

Usage:
  # Standalone test (no Milvus server required)
  python scripts/rag_milvus_tool.py --demo

  # With Milvus server
  python scripts/rag_milvus_tool.py --milvus-host localhost --milvus-port 19530

  # As importable module
  from scripts.rag_milvus_tool import RAGMilvusTool, build_knowledge_base
"""

import hashlib
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("rag_milvus")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class RAGConfig:
    """RAG pipeline configuration."""
    # Embedding
    embedding_model: str = "all-MiniLM-L6-v2"  # sentence-transformers model
    embedding_dim: int = 384                    # output dim of above model
    embedding_device: str = "cpu"

    # Chunking
    chunk_size: int = 512        # max chars per chunk
    chunk_overlap: int = 64      # overlap between adjacent chunks

    # Milvus
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    collection_name: str = "rag_knowledge_base"
    index_type: str = "IVF_FLAT"   # or "HNSW"
    metric_type: str = "COSINE"
    nlist: int = 128               # IVF cluster count

    # Retrieval
    top_k: int = 5                 # number of chunks to retrieve
    score_threshold: float = 0.3   # minimum similarity score

    # Cache
    cache_enabled: bool = True
    cache_max_size: int = 10000    # max cached queries

    # Fallback (when no real Milvus)
    use_inmemory_fallback: bool = True


# ---------------------------------------------------------------------------
# Text Splitter
# ---------------------------------------------------------------------------

class RecursiveTextSplitter:
    """
    Splits text by natural boundaries (paragraph -> sentence -> word)
    with configurable chunk size and overlap. Implements the same logic
    as LangChain's RecursiveCharacterTextSplitter.
    """

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64,
                 separators: Optional[List[str]] = None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", "。", ". ", " ", ""]

    def split(self, text: str) -> List[str]:
        return self._split_recursive(text, self.separators)

    def _split_recursive(self, text: str, separators: List[str]) -> List[str]:
        if not text.strip():
            return []

        sep = separators[0]
        remaining = separators[1:] if len(separators) > 1 else [""]

        if sep == "":
            # Character-level split
            return self._merge_chunks(list(text))

        splits = text.split(sep)
        chunks = []
        for split in splits:
            if len(split) <= self.chunk_size:
                if split.strip():
                    chunks.append(split)
            elif remaining:
                chunks.extend(self._split_recursive(split, remaining))
            else:
                # Force split by chunk_size
                chunks.extend(self._merge_chunks(list(split)))
        return chunks

    def _merge_chunks(self, pieces: List[str]) -> List[str]:
        """Merge small pieces into chunks with overlap."""
        if not pieces:
            return []
        chunks = []
        current = ""
        for piece in pieces:
            if len(current) + len(piece) <= self.chunk_size:
                current += piece
            else:
                if current:
                    chunks.append(current)
                # Keep overlap portion
                if self.chunk_overlap > 0 and current:
                    overlap_start = max(0, len(current) - self.chunk_overlap)
                    current = current[overlap_start:] + piece
                else:
                    current = piece
        if current:
            chunks.append(current)
        return chunks


# ---------------------------------------------------------------------------
# Embedding Engine
# ---------------------------------------------------------------------------

class EmbeddingEngine:
    """
    Wraps sentence-transformers for text embedding. Falls back to a
    deterministic hash-based pseudo-embedding if the package is unavailable,
    allowing the tool to demonstrate functionality without real embeddings.
    """

    def __init__(self, config: RAGConfig):
        self.config = config
        self._real_model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self._real_model = SentenceTransformer(
                config.embedding_model, device=config.embedding_device
            )
            logger.info(f"Loaded embedding model: {config.embedding_model}")
        except ImportError:
            logger.warning(
                "sentence-transformers not installed. "
                "Using hash-based fallback embeddings (for demo only)."
            )
            self._real_model = None
        except Exception as e:
            logger.warning(f"Failed to load embedding model: {e}. Using fallback.")
            self._real_model = None

    def encode(self, texts: List[str]) -> List[List[float]]:
        """Encode texts into embedding vectors."""
        if self._real_model is not None:
            embeddings = self._real_model.encode(
                texts, normalize_embeddings=True, show_progress_bar=False
            )
            return embeddings.tolist()

        # Fallback: deterministic pseudo-embedding using hash
        return [self._pseudo_embed(t) for t in texts]

    def _pseudo_embed(self, text: str) -> List[float]:
        """
        Generate a deterministic pseudo-embedding vector using token hashing.
        NOT for production use - only for offline demonstration.
        Uses a mix of n-gram hashing to simulate some semantic locality.
        """
        dim = self.config.embedding_dim
        vec = [0.0] * dim

        # Unigram features
        tokens = re.findall(r'\w+', text.lower())
        for token in tokens:
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            for offset in range(4):
                idx = (h + offset * 7919) % dim
                vec[idx] += 1.0

        # Bigram features for local order sensitivity
        for i in range(len(tokens) - 1):
            bigram = tokens[i] + "_" + tokens[i + 1]
            h = int(hashlib.md5(bigram.encode()).hexdigest(), 16)
            idx = h % dim
            vec[idx] += 0.5

        # L2 normalize
        norm = sum(v * v for v in vec) ** 0.5
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec


# ---------------------------------------------------------------------------
# Milvus Store
# ---------------------------------------------------------------------------

class MilvusStore:
    """
    Milvus vector database wrapper. Manages collection lifecycle,
    insertion, and similarity search.

    When Milvus server is unavailable, falls back to in-memory
    brute-force search (production usage requires a real Milvus deployment).
    """

    def __init__(self, config: RAGConfig):
        self.config = config
        self._collection = None
        self._connected = False
        # In-memory fallback storage
        self._inmemory_vectors: List[List[float]] = []
        self._inmemory_metadata: List[Dict[str, Any]] = []
        self._connect()

    def _connect(self):
        try:
            from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, \
                connections, utility

            connections.connect(
                alias="default",
                host=self.config.milvus_host,
                port=self.config.milvus_port,
                timeout=10,
            )
            self._connected = True
            logger.info(
                f"Connected to Milvus at "
                f"{self.config.milvus_host}:{self.config.milvus_port}"
            )

            # Create collection if not exists
            if not utility.has_collection(self.config.collection_name):
                fields = [
                    FieldSchema(name="id", dtype=DataType.INT64,
                                is_primary=True, auto_id=True),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR,
                                dim=self.config.embedding_dim),
                    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=1024),
                    FieldSchema(name="chunk_idx", dtype=DataType.INT64),
                ]
                schema = CollectionSchema(fields, description="RAG Knowledge Base")
                self._collection = Collection(name=self.config.collection_name, schema=schema)

                # Build index
                index_params = {
                    "metric_type": self.config.metric_type,
                    "index_type": self.config.index_type,
                    "params": {"nlist": self.config.nlist},
                }
                self._collection.create_index(
                    field_name="embedding", index_params=index_params
                )
                logger.info(f"Created collection: {self.config.collection_name}")
            else:
                self._collection = Collection(name=self.config.collection_name)

            self._collection.load()
        except ImportError:
            if self.config.use_inmemory_fallback:
                logger.warning(
                    "pymilvus not installed. Using in-memory fallback store."
                )
            else:
                raise
        except Exception as e:
            if self.config.use_inmemory_fallback:
                logger.warning(f"Milvus connection failed ({e}). Using in-memory fallback.")
            else:
                raise

    def insert(self, embeddings: List[List[float]],
               texts: List[str], sources: Optional[List[str]] = None) -> List[int]:
        """Insert vectors with text metadata. Returns internal IDs."""
        sources = sources or [""] * len(texts)
        ids = []

        if self._connected and self._collection is not None:
            from pymilvus import DataType
            entities = [
                embeddings,
                texts,
                sources,
                list(range(len(texts))),
            ]
            result = self._collection.insert(entities)
            ids = result.primary_keys
            self._collection.flush()

        # Also update in-memory fallback
        start_idx = len(self._inmemory_vectors)
        for i, (emb, txt, src) in enumerate(zip(embeddings, texts, sources)):
            self._inmemory_vectors.append(emb)
            self._inmemory_metadata.append({
                "text": txt,
                "source": src,
                "chunk_idx": len(self._inmemory_vectors),
            })
            ids.append(start_idx + i)

        return ids

    def search(self, query_embedding: List[float], top_k: int = 5,
               score_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Search for similar chunks.
        Returns list of {text, source, score}.
        """
        if self._connected and self._collection is not None:
            search_params = {
                "metric_type": self.config.metric_type,
                "params": {"nprobe": min(16, self.config.nlist)},
            }
            results = self._collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=["text", "source"],
            )
            hits = []
            for result in results[0]:
                if result.score >= score_threshold:
                    hits.append({
                        "text": result.entity.get("text", ""),
                        "source": result.entity.get("source", ""),
                        "score": float(result.score),
                    })
            return hits

        # In-memory brute-force search
        hits = []
        for i, vec in enumerate(self._inmemory_vectors):
            score = self._cosine_similarity(query_embedding, vec)
            if score >= score_threshold:
                meta = self._inmemory_metadata[i]
                hits.append({
                    "text": meta["text"],
                    "source": meta["source"],
                    "score": score,
                })
        hits.sort(key=lambda x: x["score"], reverse=True)
        return hits[:top_k]

    def count(self) -> int:
        if self._connected and self._collection is not None:
            return self._collection.num_entities
        return len(self._inmemory_vectors)

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norma = sum(x * x for x in a) ** 0.5
        normb = sum(x * x for x in b) ** 0.5
        if norma == 0 or normb == 0:
            return 0.0
        return dot / (norma * normb)


# ---------------------------------------------------------------------------
# LRU Query Cache
# ---------------------------------------------------------------------------

class QueryCache:
    """
    Simple LRU cache for query results. Keyed by (query_text, top_k).
    Avoids redundant embedding + search on repeated queries.
    """

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._cache: Dict[str, Tuple[List[Dict], float]] = {}  # key -> (results, timestamp)
        self._access_order: List[str] = []

    def get(self, query: str, top_k: int) -> Optional[List[Dict]]:
        key = self._make_key(query, top_k)
        if key in self._cache:
            # Move to end (most recently used)
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key][0]
        return None

    def put(self, query: str, top_k: int, results: List[Dict]):
        key = self._make_key(query, top_k)
        if key in self._cache:
            self._access_order.remove(key)
        elif len(self._cache) >= self.max_size:
            oldest = self._access_order.pop(0)
            del self._cache[oldest]
        self._cache[key] = (results, time.time())
        self._access_order.append(key)

    def clear(self):
        self._cache.clear()
        self._access_order.clear()

    @staticmethod
    def _make_key(query: str, top_k: int) -> str:
        return f"{hashlib.md5(query.encode()).hexdigest()}_{top_k}"


# ---------------------------------------------------------------------------
# Main Tool Class
# ---------------------------------------------------------------------------

class RAGMilvusTool:
    """
    Retrieval-Augmented Generation tool backed by Milvus vector database.

    Compatible with the project's tool ecosystem. Supports:
      - Building a knowledge base from documents
      - Querying with semantic search
      - Caching for repeated queries
      - Graceful fallback when Milvus is unavailable

    Example:
        tool = RAGMilvusTool(RAGConfig())
        tool.ingest_documents(["docs/paper.pdf", "docs/report.txt"])
        results = tool.query("What is entropy-balanced RL?")
    """

    def __init__(self, config: Optional[RAGConfig] = None):
        self.config = config or RAGConfig()
        self.splitter = RecursiveTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
        )
        self.embedder = EmbeddingEngine(self.config)
        self.store = MilvusStore(self.config)
        self.cache = QueryCache(max_size=self.config.cache_max_size) \
            if self.config.cache_enabled else None

        # For BaseTool compatibility
        self.name = "rag_search"
        self.trigger_tag = "rag_search"

    # ---- Document Ingestion ----

    def ingest_text(self, text: str, source: str = "") -> int:
        """Ingest a text string into the knowledge base. Returns chunk count."""
        chunks = self.splitter.split(text)
        if not chunks:
            return 0

        embeddings = self.embedder.encode(chunks)
        sources = [source] * len(chunks)
        self.store.insert(embeddings, chunks, sources)
        logger.info(f"Ingested {len(chunks)} chunks from: {source or '<text>'}")
        return len(chunks)

    def ingest_documents(self, file_paths: List[str]) -> Dict[str, int]:
        """Ingest files into the knowledge base. Returns {path: chunk_count}."""
        results = {}
        for path in file_paths:
            try:
                text = self._read_file(path)
                if text:
                    results[path] = self.ingest_text(text, source=os.path.basename(path))
                else:
                    results[path] = 0
                    logger.warning(f"Empty or unreadable file: {path}")
            except Exception as e:
                logger.error(f"Failed to ingest {path}: {e}")
                results[path] = 0
        return results

    # ---- Query ----

    def query(self, query_text: str, top_k: Optional[int] = None,
              score_threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute a RAG query.

        Returns:
            {
                "query": str,
                "results": [{"text": str, "source": str, "score": float}],
                "total_hits": int,
                "elapsed_ms": float,
            }
        """
        top_k = top_k or self.config.top_k
        score_threshold = score_threshold or self.config.score_threshold

        # Check cache
        if self.cache:
            cached = self.cache.get(query_text, top_k)
            if cached is not None:
                return {
                    "query": query_text,
                    "results": cached,
                    "total_hits": len(cached),
                    "elapsed_ms": 0.0,
                    "cached": True,
                }

        t0 = time.perf_counter()
        query_emb = self.embedder.encode([query_text])[0]
        results = self.store.search(query_emb, top_k=top_k,
                                     score_threshold=score_threshold)
        elapsed = (time.perf_counter() - t0) * 1000

        output = {
            "query": query_text,
            "results": results,
            "total_hits": len(results),
            "elapsed_ms": round(elapsed, 2),
            "cached": False,
        }

        # Update cache
        if self.cache:
            self.cache.put(query_text, top_k, results)

        return output

    # ---- Execute (BaseTool-compatible interface) ----

    def execute(self, content: str, **kwargs) -> str:
        """
        Execute a RAG query and return formatted context.

        This matches the BaseTool.execute signature expected by the project's
        ToolExecutor. The content parameter contains the search query.

        Args:
            content: The search query string.
            **kwargs: Additional parameters (top_k, score_threshold).

        Returns:
            JSON string with retrieved context.
        """
        params = self._parse_params(content, kwargs)
        result = self.query(
            query_text=params["query"],
            top_k=params.get("top_k"),
            score_threshold=params.get("score_threshold"),
        )
        return self._format_result(result)

    def _parse_params(self, content: str, kwargs: dict) -> dict:
        """Parse query parameters from content string and kwargs."""
        params = {"query": content.strip()}
        if "top_k" in kwargs:
            params["top_k"] = int(kwargs["top_k"])
        if "score_threshold" in kwargs:
            params["score_threshold"] = float(kwargs["score_threshold"])
        return params

    def _format_result(self, result: Dict[str, Any]) -> str:
        """Format query results as a JSON string for the agent."""
        return json.dumps(result, ensure_ascii=False, indent=2)

    # ---- Helpers ----

    @staticmethod
    def _read_file(path: str) -> Optional[str]:
        """Read text from a file, handling common formats."""
        if not os.path.exists(path):
            return None

        _, ext = os.path.splitext(path)
        ext = ext.lower()

        if ext == ".pdf":
            try:
                import PyPDF2
                with open(path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    return "\n".join(
                        page.extract_text() or "" for page in reader.pages
                    )
            except ImportError:
                logger.warning("PyPDF2 not installed. Cannot read PDF.")
                return None
            except Exception as e:
                logger.error(f"PDF read error: {e}")
                return None

        # Plain text files
        for encoding in ["utf-8", "gbk", "latin-1"]:
            try:
                with open(path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        return None

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "collection_name": self.config.collection_name,
            "total_vectors": self.store.count(),
            "embedding_dim": self.config.embedding_dim,
            "milvus_connected": self.store._connected,
            "cache_enabled": self.cache is not None,
        }


# ---------------------------------------------------------------------------
# Convenience: Build Knowledge Base
# ---------------------------------------------------------------------------

def build_knowledge_base(documents: List[str],
                         config: Optional[RAGConfig] = None) -> RAGMilvusTool:
    """
    Convenience function to build a RAG knowledge base from documents.

    Args:
        documents: List of file paths or text strings.
        config: Optional RAGConfig. Uses defaults if not provided.

    Returns:
        Initialized RAGMilvusTool with ingested documents.
    """
    config = config or RAGConfig()
    tool = RAGMilvusTool(config)

    files = [d for d in documents if os.path.exists(d)]
    texts = [d for d in documents if not os.path.exists(d)]

    if files:
        tool.ingest_documents(files)
    for text in texts:
        if text.strip():
            tool.ingest_text(text)

    logger.info(f"Knowledge base built: {tool.store.count()} vectors")
    return tool


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def run_demo():
    """Demonstrate RAG pipeline with sample knowledge base (no external deps)."""
    print("=" * 60)
    print("  RAG + Milvus Tool — Demonstration")
    print("=" * 60)

    config = RAGConfig(chunk_size=256, chunk_overlap=32)
    tool = RAGMilvusTool(config)

    # Build a small knowledge base
    documents = [
        (
            "AEARPO (Agentic Entropy-Balanced Reinforcement Optimization) "
            "is a reinforcement learning algorithm for LLM agents. It monitors "
            "entropy around tool-use tokens during rollout and adaptively branches "
            "sampling for high-uncertainty tool-call rounds. Key hyperparameters "
            "include branch_probability, beam_size, and entropy_weight. "
            "On GAIA benchmark, Qwen3-14B + AEARPO achieved 61.2% accuracy."
        ),
        (
            "Milvus is an open-source vector database designed for similarity search "
            "over large-scale embedding vectors. It supports multiple index types "
            "including IVF_FLAT, IVF_PQ, HNSW, and DiskANN. Milvus 2.x uses a "
            "cloud-native architecture with separated compute and storage. "
            "Key concepts include Collections (analogous to tables), Partitions, "
            "and Entities (rows with vector fields)."
        ),
        (
            "RAG (Retrieval-Augmented Generation) combines information retrieval "
            "with text generation. The pipeline typically involves: 1) Document "
            "chunking, 2) Embedding generation, 3) Vector storage, 4) Query-time "
            "retrieval, and 5) Context-augmented generation. RAG reduces hallucination "
            "by grounding LLM outputs in retrieved evidence."
        ),
        (
            "GRPO (Group Relative Policy Optimization) removes the Critic/Value "
            "network from PPO and computes advantages via group-wise reward "
            "normalization. For each prompt, multiple responses are sampled, "
            "and the advantage is (reward - group_mean) / group_std. This halves "
            "the model parameters and speeds up training."
        ),
        (
            "A test harness is a collection of software and test data configured "
            "to test a program unit by running it under varying conditions and "
            "monitoring its behavior and outputs. Key components include: test "
            "fixture setup, test execution, result assertion, and teardown. "
            "In ML systems, test harnesses validate data pipelines, model "
            "inference correctness, and training loop integrity."
        ),
        (
            "Agent skills are composable capabilities that extend an LLM agent's "
            "function repertoire. Each skill defines a trigger condition, an "
            "execution interface, and an output format. Skills can be chained: "
            "the output of a search skill feeds into a summarization skill, "
            "which feeds into a report-generation skill. Skill registries manage "
            "discovery, versioning, and dependency resolution."
        ),
    ]

    print(f"\nIngesting {len(documents)} documents...")
    for i, doc in enumerate(documents):
        title = doc.split(".")[0][:60]
        n = tool.ingest_text(doc, source=f"doc_{i}")
        print(f"  [{i}] {title}... -> {n} chunks")

    print(f"\nTotal vectors in store: {tool.store.count()}")

    # Run queries
    queries = [
        "How does AEARPO use entropy for agent training?",
        "What is Milvus and what index types does it support?",
        "Explain RAG pipeline architecture",
        "How does GRPO compute advantages without a Critic?",
        "What are agent skills and how are they composed?",
    ]

    print("\n" + "-" * 60)
    print("  Semantic Search Results")
    print("-" * 60)

    for query in queries:
        print(f"\nQuery: {query}")
        result = tool.query(query, top_k=2)

        for i, hit in enumerate(result["results"]):
            preview = hit["text"][:120].replace("\n", " ")
            print(f"  [{i}] score={hit['score']:.4f} | {preview}...")

        if not result["results"]:
            print("  (no results above threshold)")

    print(f"\nStats: {json.dumps(tool.stats, indent=2)}")
    print("\nDemo complete. Tool is ready for integration.")


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="RAG + Milvus Vector Search Tool"
    )
    parser.add_argument("--demo", action="store_true",
                        help="Run demonstration with sample data")
    parser.add_argument("--milvus-host", default="localhost",
                        help="Milvus server host (default: localhost)")
    parser.add_argument("--milvus-port", type=int, default=19530,
                        help="Milvus server port (default: 19530)")
    parser.add_argument("--ingest", nargs="+", metavar="FILE",
                        help="Ingest documents into the knowledge base")
    parser.add_argument("--query", type=str,
                        help="Run a single query against the knowledge base")
    parser.add_argument("--top-k", type=int, default=5,
                        help="Number of results per query (default: 5)")

    args = parser.parse_args()

    config = RAGConfig(
        milvus_host=args.milvus_host,
        milvus_port=args.milvus_port,
    )

    if args.demo:
        run_demo()
    else:
        tool = RAGMilvusTool(config)

        if args.ingest:
            tool.ingest_documents(args.ingest)

        if args.query:
            result = tool.query(args.query, top_k=args.top_k)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        if not args.ingest and not args.query:
            parser.print_help()
