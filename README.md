# colony

A Python package for creating a graph of asyncronous processing units on a single machine.

Data can flow between nodes in a reactive or passive manner.

# Example Use Cases

 - Downloading multiple web-based resources on multiple threads (overcoming the I/O bound nature of Internet downloads)
  with results sent to a single thread for processing (to reduce cpu context-switching).
 - Using live price updates from multiple stocks to calculate synthetic prices.

