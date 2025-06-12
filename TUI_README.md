# Inquiro TUI - Professional Research Assistant Interface

A modern Terminal User Interface (TUI) for the Inquiro Research Assistant, designed for researchers who need efficient document-based question answering.

## Features

### 🔬 Professional Interface
- **Clean, minimalist design** focused on functionality
- **Split-panel layout** for optimal workflow
- **Real-time status indicators** for system state
- **Color-coded messaging** for clear communication

### 💬 Interactive Chat Zone
- **Natural language queries** about your documents
- **Real-time responses** with source attribution
- **Message history** with timestamps
- **Error handling** with helpful feedback
- **Auto-scrolling** chat area

### 📁 Document Context Manager
- **Live file listing** from your data directory
- **Database status monitoring** (Ready/Not Built)
- **One-click database operations** (build, clear, refresh)
- **Support for multiple formats** (PDF, TXT, MD)

## Quick Start

### 1. Install Dependencies
```powershell
pip install textual>=0.41.0
```

### 2. Add Your Documents
Place your PDF files in the `./data` directory:
```powershell
mkdir data
# Copy your PDF research papers to ./data/
```

### 3. Launch the TUI
```powershell
python textual_app.py
```

## Interface Overview

```
┌─────────────────────────────────┐ ┌────────────────────────┐
│ 🔬 Inquiro Research Assistant   │ │ 📁 Document Context    │
│                                 │ │                        │
│ 💬 Research Chat                │ │ Database Status:       │
│ ┌─────────────────────────────┐ │ │ ✅ Database Ready      │
│ │ Chat messages appear here   │ │ │                        │
│ │ with timestamps and color   │ │ │ Documents:             │
│ │ coding for easy reading     │ │ │ • paper1.pdf           │
│ │                             │ │ │ • paper2.pdf           │
│ └─────────────────────────────┘ │ │                        │
│                                 │ │ [📁 Refresh Files]     │
│ Ask a question... [Send]        │ │ [🔄 Populate Database] │
└─────────────────────────────────┘ │ [🗑️ Clear Database]    │
                                    └────────────────────────┘
```

## Usage Workflow

### 1. Check Database Status
- The right panel shows if your database is ready
- **✅ Database Ready**: You can start asking questions
- **❌ Database Not Built**: Click "🔄 Populate Database" first

### 2. Populate Database
- Click **"🔄 Populate Database"** to process your documents
- This creates searchable embeddings from your PDFs
- Progress messages appear in the chat area
- Wait for "✅ Database built successfully!" message

### 3. Ask Questions
- Type your question in the input field
- Press `Enter` or click **"Send"**
- The system searches your documents and provides answers
- Sources are automatically included with responses

### 4. Manage Documents
- **"📁 Refresh Files"**: Updates the file list
- **"🗑️ Clear Database"**: Removes the current database
- Add new PDFs to `./data` and refresh to include them

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit the application |
| `Ctrl+C` | Force quit |
| `F5` | Refresh file list and database status |
| `Enter` | Send message (when input is focused) |

## Message Types

The chat area uses color coding for clarity:

- **🔵 System**: Status updates and notifications
- **🟢 You**: Your questions and inputs
- **🟡 Assistant**: AI responses with source citations
- **🔴 Error**: Error messages and troubleshooting info

## Advanced Features

### Threading Support
- Long operations (database building, queries) run in background threads
- UI remains responsive during processing
- Real-time progress feedback

### Auto-scrolling
- Chat automatically scrolls to show latest messages
- Message history limited to last 50 entries for performance

### Error Recovery
- Graceful handling of missing dependencies
- Clear error messages with suggested solutions
- Automatic retry capabilities for transient failures

## Troubleshooting

### Common Issues

**"No database found" error:**
```
Solution: Click "🔄 Populate Database" in the right panel
```

**No documents shown:**
```
Solution: 
1. Add PDF files to ./data directory
2. Click "📁 Refresh Files"
```

**Query function not available:**
```
Solution: Ensure all dependencies are installed:
pip install -r requirements.txt
```

**UI appears broken:**
```
Solution: Ensure terminal supports Unicode and colors
Windows Terminal or PowerShell ISE recommended
```

### System Requirements

- **Python 3.8+**
- **Terminal with Unicode support**
- **Minimum 8GB RAM** (for embeddings)
- **Ollama installed** with required models

## Development

### Architecture
- **Textual framework** for TUI components
- **Reactive programming** for real-time updates
- **Threaded operations** for non-blocking I/O
- **Modular design** with clear separation of concerns

### Customization
The interface can be customized by modifying the CSS in `textual_app.py`:
- Colors and themes
- Layout proportions
- Component styling
- Animation effects

## Integration

### Backend Integration
The TUI seamlessly integrates with existing Inquiro components:
- `query_data.py` for question answering
- `populate_database.py` for database operations
- `get_embedding.py` for embeddings

### API Compatibility
All existing command-line interfaces remain functional:
```powershell
# Still works alongside TUI
python query_data.py "your question"
python populate_database.py --reset
```

## Performance Tips

1. **Terminal Performance**: Use Windows Terminal for best rendering
2. **Memory Usage**: Clear database periodically if processing many documents
3. **Response Time**: Ensure Ollama models are downloaded locally
4. **File Organization**: Keep data directory organized for faster scanning

---

*Built with [Textual](https://textual.textualize.io/) - Modern TUI framework for Python*
