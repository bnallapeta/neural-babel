from prometheus_client import Counter, Histogram, Gauge


# Request metrics
TRANSLATION_REQUESTS = Counter(
    "translation_requests_total",
    "Total number of translation requests",
    ["source_lang", "target_lang"]
)

TRANSLATION_ERRORS = Counter(
    "translation_errors_total",
    "Total number of translation errors",
    ["type", "stage"]
)

TRANSLATION_LATENCY = Histogram(
    "translation_latency_seconds",
    "Translation request latency in seconds",
    ["source_lang", "target_lang"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0)
)

# Service metrics
SERVICE_REQUESTS = Counter(
    "service_requests_total",
    "Total number of service requests",
    ["service", "operation"]
)

SERVICE_ERRORS = Counter(
    "service_errors_total",
    "Total number of service errors",
    ["service", "operation", "error_type"]
)

SERVICE_LATENCY = Histogram(
    "service_latency_seconds",
    "Service request latency in seconds",
    ["service", "operation"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0)
)

# Pipeline metrics
PIPELINE_STAGE_LATENCY = Histogram(
    "pipeline_stage_latency_seconds",
    "Pipeline stage latency in seconds",
    ["stage"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0)
)

PIPELINE_COMPLETION_RATE = Counter(
    "pipeline_completion_total",
    "Total number of pipeline completions",
    ["status"]  # "success" or "failure"
)

# System metrics
SYSTEM_MEMORY_USAGE = Gauge(
    "system_memory_usage_bytes",
    "Memory usage in bytes"
)

SYSTEM_CPU_USAGE = Gauge(
    "system_cpu_usage_percent",
    "CPU usage in percent"
)

# Cache metrics
CACHE_HITS = Counter(
    "cache_hits_total",
    "Total number of cache hits"
)

CACHE_MISSES = Counter(
    "cache_misses_total",
    "Total number of cache misses"
)

CACHE_SIZE = Gauge(
    "cache_size_bytes",
    "Cache size in bytes"
)
