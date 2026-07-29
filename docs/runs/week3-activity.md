The request counts are stored only in process memory, so all collected metrics are lost whenever the application restarts,So the metrics is tracked once the application is started

when there is heavy concurrency, the counter may not always increase accurately because the dictionary is stored separately in each process and does not provide a shared atomic counter.