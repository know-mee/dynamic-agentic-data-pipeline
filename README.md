# dynamic-agentic-data-pipeline
# Metadata-Driven Dynamic ETL Pipeline Framework

A highly scalable, configuration-driven ETL (Extract, Transform, Load) orchestration engine built in Python. This framework decouples core pipeline logic from business configurations, allowing you to onboard new files, schemas, and target data warehouses completely via metadata updates—with zero modification to the underlying codebase.

Designed with data security, throughput, and performance in mind, this architecture is fully optimized to serve as a high-speed, structured data foundation for private, local Agentic AI (via Ollama).

---

## 🚀 Key Architecture Highlights

* **100% Configuration-Driven (Zero-Code Scaling):** All pipeline behaviors—including FTP remote paths, file wildcard patterns, destination DDL schemas, and deduplication criteria—are managed entirely through an externalized JSON control matrix.
* **In-Memory Streaming (Zero Disk Overheads):** Bypasses local disk storage by pulling matching file assets via remote network streams straight into RAM memory buffers (`io.BytesIO`), maximizing I/O execution speeds.
* **Dynamic Target Isolation (Multi-Thread Safe):** Automatically provisions individual runtime staging environments for each execution loop using dynamic timestamps and cryptographic execution tokens, eliminating multi-threaded race conditions or accidental data overwrites.
* **Dynamic Constraint Resolution:** Evaluates schema characteristics at runtime to dynamically append conditional clauses (`ON CONFLICT (key) DO NOTHING`), providing graceful, resilient row handling across variable business schemas.
* **Local AI Integration Ready:** By transforming messy, unstructured source data into indexed relational staging rows *before* it interfaces with an LLM, it allows lightweight, private local models (e.g., Llama-3-8B via Ollama) to query database catalogs instantaneously, reducing token costs and reducing latency from minutes to milliseconds.

---

## 🛠️ Technology Stack & Matrix

* **Orchestrator Core:** Python 3.x (Utilizing `argparse` for runtime job flags)
* **Extraction Gateway:** `ftplib` + `fnmatch` (Unix shell-style filename pattern matching)
* **Memory Buffer Layer:** `io.BytesIO` + `io.TextIOWrapper` 
* **Database Driver & Engine:** PostgreSQL + `psycopg2` (Utilizing `psycopg2.sql` to block SQL injection vulnerabilities, and `execute_values` for high-volume batch loading)
* **AI Orchestration Target:** Ollama (Local private LLM execution layer)

---

## 📋 Operational Workflow

1. **Initialization:** The main orchestrator evaluates runtime arguments and fetches the master job list array from the configuration matrix.
2. **Extraction:** The network engine connects to the remote source directory, isolates candidate files, and streams raw text rows cleanly into memory structures.
3. **DDL Compilation:** The framework reads generic schema blueprints, dynamically interpolates placeholder fields with isolated runtime staging identifiers, and registers the database layout.
4. **Resilient Load:** The loader pushes data sets into the database in microsecond batch blocks while silently processing unique database constraints via your defined metadata conflict keys.
