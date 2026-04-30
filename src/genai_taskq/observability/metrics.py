from prometheus_client import Counter, Histogram

submit_counter = Counter("gtq_submit_total", "Number of submitted tasks")
dequeue_counter = Counter("gtq_dequeue_total", "Number of dequeued tasks")
provider_latency = Histogram("gtq_provider_latency_seconds", "Provider latency seconds")
