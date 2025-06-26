# Optimal Configuration for 13900HX + 16GB RAM + RTX 4060 8GB

This guide provides optimal configuration settings for your specific hardware setup.

## System Overview
- **CPU**: Intel Core i9-13900HX (24 cores: 8P + 16E cores)
- **RAM**: 16GB total system memory
- **GPU**: RTX 4060 with 8GB VRAM (managed by Ollama server)
- **OS**: Windows

## Recommended Configuration Values

### Memory Management (Critical for 16GB Systems)
```bash
# Set memory limit to 70% of available RAM (leaving ~5GB for OS and other apps)
DEFAULT_MEMORY_LIMIT=11000  # 11GB in MB

# Alternative conservative setting (safer for multitasking)
DEFAULT_MEMORY_LIMIT=8000   # 8GB in MB
```

### Text Processing Optimization
```bash
# Optimized for balance of context quality and processing speed
CHUNK_SIZE=800             # Larger chunks for better context
CHUNK_OVERLAP=80           # 10% overlap for context continuity

# Alternative for memory-constrained scenarios
CHUNK_SIZE=600
CHUNK_OVERLAP=60
```

### Query Performance Tuning
```bash
# Retrieval settings optimized for quality
DEFAULT_K=7                # Retrieve 7 most relevant documents
DEFAULT_SCORE_THRESHOLD=0.4 # Lower threshold for better recall
DEFAULT_MAX_CONTEXT_LENGTH=6000  # Larger context for better answers
```

### Model Recommendations for RTX 4060 8GB
```bash
# Balanced models for 8GB VRAM (via Ollama)
OLLAMA_QUERY_MODEL="llama3.1:8b"  # Excellent quality, fits in 8GB
OLLAMA_EMBEDDING_MODEL="nomic-embed-text"  # Fast and efficient

# Alternative lighter model for faster responses
OLLAMA_QUERY_MODEL="llama3.1:7b"  # Slightly smaller, faster

# High-quality alternative (if you have good internet for download)
OLLAMA_QUERY_MODEL="qwen2.5:7b"   # Often better reasoning
```

## Setup Instructions

### 1. Environment Variables (Recommended Method)
Create a `.env` file in your Inquiro directory or set Windows environment variables:

```bash
# Memory and Performance
DEFAULT_MEMORY_LIMIT=11000
CHUNK_SIZE=800
CHUNK_OVERLAP=80

# Query Settings
DEFAULT_K=7
DEFAULT_SCORE_THRESHOLD=0.4
DEFAULT_MAX_CONTEXT_LENGTH=6000

# Models (adjust based on your preference)
OLLAMA_QUERY_MODEL=llama3.1:8b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

### 2. PowerShell Environment Setup
```powershell
# Set environment variables for current session
$env:DEFAULT_MEMORY_LIMIT="11000"
$env:CHUNK_SIZE="800"
$env:CHUNK_OVERLAP="80"
$env:DEFAULT_K="7"
$env:DEFAULT_SCORE_THRESHOLD="0.4"
$env:DEFAULT_MAX_CONTEXT_LENGTH="6000"
$env:OLLAMA_QUERY_MODEL="llama3.1:8b"
$env:OLLAMA_EMBEDDING_MODEL="nomic-embed-text"

# Run Inquiro configuration
python core/config.py
```

### 3. Persistent Windows Environment Variables
```powershell
# Set permanent environment variables (requires admin/restart)
[Environment]::SetEnvironmentVariable("DEFAULT_MEMORY_LIMIT", "11000", "User")
[Environment]::SetEnvironmentVariable("CHUNK_SIZE", "800", "User")
[Environment]::SetEnvironmentVariable("CHUNK_OVERLAP", "80", "User")
[Environment]::SetEnvironmentVariable("DEFAULT_K", "7", "User")
[Environment]::SetEnvironmentVariable("DEFAULT_SCORE_THRESHOLD", "0.4", "User")
[Environment]::SetEnvironmentVariable("DEFAULT_MAX_CONTEXT_LENGTH", "6000", "User")
[Environment]::SetEnvironmentVariable("OLLAMA_QUERY_MODEL", "llama3.1:8b", "User")
[Environment]::SetEnvironmentVariable("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text", "User")
```

## Performance Optimization Tips

### 1. Ollama Server Optimization
```bash
# Install recommended models
ollama pull llama3.1:8b
ollama pull nomic-embed-text

# Verify GPU utilization
ollama ps  # Check if models are running
```

### 2. Windows-Specific Optimizations
- **Enable Hardware-accelerated GPU scheduling**: Windows Settings > System > Display > Graphics Settings
- **Set high performance power mode** when processing large documents
- **Close unnecessary applications** during large ingestion tasks
- **Use SSD storage** for FAISS index and data directories if possible

### 3. Batch Processing Guidelines
For your 16GB system:
- **Small documents** (< 1000 pages): Process all at once
- **Medium documents** (1000-5000 pages): Batch size of 2000-3000 chunks
- **Large documents** (> 5000 pages): Batch size of 1500-2000 chunks
- **Monitor memory usage** and adjust batch sizes accordingly

### 4. Directory Setup (Optional)
```powershell
# Use faster storage if available
$env:INQUIRO_BASE_DIR="D:\inquiro"  # If D: is SSD
# or
$env:INQUIRO_BASE_DIR="C:\inquiro"  # Default
```

## Troubleshooting

### Memory Issues
If you encounter out-of-memory errors:
1. Reduce `DEFAULT_MEMORY_LIMIT` to 8000 (8GB)
2. Reduce `CHUNK_SIZE` to 600
3. Reduce `DEFAULT_K` to 5
4. Close other applications

### Performance Issues
If processing is slow:
1. Ensure Ollama is using GPU: `ollama ps`
2. Check Windows Task Manager for GPU utilization
3. Consider using lighter models like `llama3.1:7b`
4. Increase `CHUNK_SIZE` to reduce total chunks

### Model Loading Issues
```bash
# Check available models
ollama list

# Pull missing models
ollama pull llama3.1:8b
ollama pull nomic-embed-text

# Test model accessibility
ollama run llama3.1:8b "test"
```

## Monitoring System Performance

Use these commands to monitor your system during operation:

```powershell
# Monitor memory usage
Get-WmiObject -Class Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory

# Monitor GPU usage (if nvidia-smi available)
nvidia-smi

# Monitor Ollama processes
ollama ps
```

## Expected Performance

With the recommended configuration:
- **Document ingestion**: 100-500 pages/minute (depending on content)
- **Query response time**: 3-10 seconds for complex queries
- **Memory usage**: 8-11GB during heavy processing
- **GPU utilization**: 80-95% during model inference

This configuration balances performance and resource usage for your specific hardware setup.
