# Inquiro Improvements

This document outlines current and planned improvements to the Inquiro system.

## Recently Implemented

### Memory Optimization (June 2025)

**Problem:** The system crashed with large document collections (>1.5GB) on systems with 16GB RAM.

**Solution:** Implemented batch processing with configurable memory limits:
- Process one document at a time to minimize memory spikes
- Batch chunks into smaller groups for embedding generation
- Configurable memory limit with runtime monitoring
- Incremental database updates to reduce peak memory usage

**Benefits:**
- Handles much larger document collections on the same hardware
- Prevents out-of-memory crashes during embedding and indexing
- More efficient resource utilization
- Progress tracking and better error recovery

**Usage:**
```bash
python core/populate_database.py --optimized-memory --batch-size 500 --memory-limit 8000
```

### GPU Acceleration Support (June 2025)

**Problem:** CPU-only processing is slow for embedding generation with large document collections.

**Solution:** Added optional GPU acceleration:
- Configurable through environment variables or config.py
- Automatic fallback to CPU if GPU fails
- Performance monitoring and recommendations

**Benefits:**
- Significantly faster embedding generation
- Improved throughput for large document collections
- Better utilization of available hardware

**Usage:**
```bash
# Set via environment variable
export USE_GPU=true

# Or during configuration
python core/config.py
# Then select "yes" for GPU acceleration
```

## Planned Improvements

### Chunking Strategy Enhancements

**Problem:** Current fixed-size chunking can sometimes split important context.

**Planned Solution:**
- Semantic chunking based on document structure
- Paragraph and section-aware splitting
- Adaptive chunk size based on content complexity

### Multi-Vector Retrieval

**Problem:** Single vector per chunk limits retrieval precision.

**Planned Solution:**
- Multi-vector representation for each chunk
- Sentence-level indexing for fine-grained retrieval
- Hierarchical retrieval for improved context preservation

### Citation Generation

**Problem:** Source attribution is basic.

**Planned Solution:**
- Formal citation generation in academic formats
- Page and paragraph-level sourcing
- Direct quote extraction and highlighting

## Contribution Opportunities

Interested in contributing? These areas need help:

1. **Memory Profiling**: Help analyze memory usage patterns for further optimization
2. **PDF Annotation**: Implement in-document highlighting of source passages
3. **Custom Chunking Strategies**: Develop domain-specific chunking approaches
4. **Testing**: Develop benchmarks for system performance on different hardware

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get started.
