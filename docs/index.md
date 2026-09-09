> **Historical documentation:** the paid notebook runner is retired. See [current methodology](methodology.md) and [repository README](../ReadME.md) for the supported workflow and corrected token/scoring claims.

# FTAAT Documentation Hub

Welcome to the documentation for the Fixed Token Abstract Attention Test (FTAAT) benchmark. The project evaluates large language models on an abstract key–value memorisation task while tightly controlling token usage. Use the guides below to understand the benchmark design, run experiments, integrate providers, and analyse results.

## 📚 Documentation map

- [Benchmark design](benchmark_design.md)
- [Experiment pipeline](pipeline.md)
- [Provider integrations](providers.md)
- [Notebooks guide](notebooks.md)
- [Results and data management](results_management.md)

## Why token-consistent benchmarking?

FTAAT creates synthetic key→value pairs constructed from single-token symbols. By controlling both the number of facts ($N$) and the length of each key/value sequence ($K$), the benchmark separates two difficulty axes:

1. **Memory load** — how many distinct associations the model must recall (increasing $N$).
2. **Key complexity** — how many tokens must be matched per association (increasing $K$).

Because the same symbol inventory is used to build prompts and references, the experiments expose a clean failure curve that is not confounded by variations in tokenisation.

Each detailed guide links back to the Python modules, scripts, and notebooks that implement these ideas. Start with the [benchmark design](benchmark_design.md) to understand the underlying theory, then follow the [pipeline walkthrough](pipeline.md) to run your own evaluations.
