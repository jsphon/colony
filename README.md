# colony

A Python package for creating a network of (possibly asyncronous) processing units (nodes) on a single machine.

Data can flow between nodes in a reactive or passive manner.

# Example Use Cases

 - Downloading multiple web-based resources on multiple threads (overcoming the I/O bound nature of Internet downloads)
  with results sent to a single thread for processing, to prevent cpu-overload.
 - Handling live price updates from multiple stocks, with results used to calculate synthetic prices.

