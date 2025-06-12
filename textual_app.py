from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static, Input, ProgressBar, Label, SelectionList
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.reactive import reactive
from textual.screen import Screen
from textual.message import Message
from textual import on
import os
import asyncio
import subprocess
import sys
from datetime import datetime
import threading

# Import our backend functions
try:
    from query_data import query_rag
    from populate_database import main as populate_main, clear_database
except ImportError as e:
    print(f"Warning: Could not import backend functions: {e}")
    query_rag = None
    populate_main = None

class ChatZone(Vertical):
    messages = reactive([])

    def compose(self) -> ComposeResult:
        yield Static("💬 Research Chat", classes="section-title")
        self.message_area = Static("", classes="chat-messages", id="messages")
        yield ScrollableContainer(self.message_area, id="chat-scroll")
        yield Horizontal(
            Input(placeholder="Ask a question about your documents...", id="chat-input"),
            Button("Send", id="send-btn", variant="primary"),
            classes="input-row"
        )

    def on_mount(self):
        self.add_system_message("Welcome! Load documents and ask questions to get started.")

    def add_system_message(self, message: str):
        timestamp = datetime.now().strftime("%H:%M")
        self.messages.append(f"[dim]{timestamp}[/dim] [blue]System:[/blue] {message}")
        self.update_messages()

    def add_user_message(self, message: str):
        timestamp = datetime.now().strftime("%H:%M")
        self.messages.append(f"[dim]{timestamp}[/dim] [green]You:[/green] {message}")
        self.update_messages()

    def add_assistant_message(self, message: str):
        timestamp = datetime.now().strftime("%H:%M")
        self.messages.append(f"[dim]{timestamp}[/dim] [yellow]Assistant:[/yellow] {message}")
        self.update_messages()

    def add_error_message(self, message: str):
        timestamp = datetime.now().strftime("%H:%M")
        self.messages.append(f"[dim]{timestamp}[/dim] [red]Error:[/red] {message}")
        self.update_messages()

    @on(Input.Submitted, "#chat-input")
    @on(Button.Pressed, "#send-btn")
    async def send_message(self, event):
        input_widget = self.query_one("#chat-input", Input)
        msg = input_widget.value.strip()
        if not msg:
            return
        
        input_widget.value = ""
        self.add_user_message(msg)
        
        # Check if database exists
        if not os.path.exists("faiss_index"):
            self.add_error_message("No database found. Please populate the database first.")
            return
        
        # Show thinking message
        self.add_system_message("🔍 Searching documents...")
        
        # Run query in thread to avoid blocking UI
        def run_query():
            try:
                if query_rag:
                    response = query_rag(msg)
                    self.call_from_thread(self.add_assistant_message, response)
                else:
                    self.call_from_thread(self.add_error_message, "Query function not available")
            except Exception as e:
                self.call_from_thread(self.add_error_message, f"Query failed: {str(e)}")
        
        threading.Thread(target=run_query, daemon=True).start()

    def update_messages(self):
        content = "\n".join(self.messages[-50:])  # Keep last 50 messages
        self.message_area.update(content)
        # Auto-scroll to bottom
        self.query_one("#chat-scroll").scroll_end(animate=False)

class ContextManagerZone(Vertical):
    files = reactive([])
    database_status = reactive("Unknown")

    def on_mount(self):
        self.refresh_file_list()
        self.update_database_status()

    def compose(self) -> ComposeResult:
        yield Static("📁 Document Context", classes="section-title")
        
        # Database status
        yield Static("Database Status:", classes="label")
        self.status_display = Static("", id="db-status")
        yield self.status_display
        
        # File list
        yield Static("Documents:", classes="label")
        self.file_list = Static("", classes="file-list", id="file-display")
        yield ScrollableContainer(self.file_list, id="file-scroll")
        
        # Action buttons
        yield Vertical(
            Button("📁 Refresh Files", id="refresh-files", variant="default"),
            Button("🔄 Populate Database", id="populate-db", variant="primary"),
            Button("🗑️ Clear Database", id="clear-db", variant="error"),
            classes="button-group"
        )

    def refresh_file_list(self):
        """Update the file list from the data directory."""
        data_dir = os.path.join(os.getcwd(), "data")
        if os.path.exists(data_dir):
            all_files = os.listdir(data_dir)
            self.files = [f for f in all_files if f.endswith(('.pdf', '.txt', '.md'))]
        else:
            self.files = []
        
        if self.files:
            file_display = "\n".join([f"• {f}" for f in self.files])
        else:
            file_display = "No documents found in ./data directory"
        
        self.file_list.update(file_display)

    def update_database_status(self):
        """Check and update database status."""
        if os.path.exists("faiss_index") and os.path.exists("faiss_index/index.faiss"):
            self.database_status = "✅ Ready"
            status_text = "[green]✅ Database Ready[/green]"
        else:
            self.database_status = "❌ Not Built"
            status_text = "[red]❌ Database Not Built[/red]"
        
        self.status_display.update(status_text)

    @on(Button.Pressed, "#refresh-files")
    def refresh_files_action(self):
        self.refresh_file_list()
        self.app.query_one(ChatZone).add_system_message("File list refreshed")

    @on(Button.Pressed, "#populate-db")
    def populate_database_action(self):
        if not self.files:
            self.app.query_one(ChatZone).add_error_message("No documents found. Add PDF files to ./data directory")
            return
        
        chat = self.app.query_one(ChatZone)
        chat.add_system_message("🔄 Building database... This may take a moment.")
        
        def run_populate():
            try:
                if populate_main:
                    # Run the populate function
                    populate_main()
                    self.call_from_thread(self.update_database_status)
                    self.call_from_thread(chat.add_system_message, "✅ Database built successfully!")
                else:
                    self.call_from_thread(chat.add_error_message, "Populate function not available")
            except Exception as e:
                self.call_from_thread(chat.add_error_message, f"Database build failed: {str(e)}")
        
        threading.Thread(target=run_populate, daemon=True).start()

    @on(Button.Pressed, "#clear-db")
    def clear_database_action(self):
        def run_clear():
            try:
                if clear_database:
                    clear_database()
                    self.call_from_thread(self.update_database_status)
                    self.call_from_thread(
                        self.app.query_one(ChatZone).add_system_message, 
                        "🗑️ Database cleared successfully"
                    )
                else:
                    self.call_from_thread(
                        self.app.query_one(ChatZone).add_error_message, 
                        "Clear function not available"
                    )
            except Exception as e:
                self.call_from_thread(
                    self.app.query_one(ChatZone).add_error_message, 
                    f"Clear failed: {str(e)}"
                )
        
        threading.Thread(target=run_clear, daemon=True).start()

class InquiroTUI(App):
    """Professional TUI for the Inquiro Research Assistant."""
    
    CSS = """
    /* Main layout */
    #main-horizontal {
        height: 100%;
    }
    
    #center-zone {
        width: 2fr;
        margin: 1;
        border: solid $primary;
    }
    
    #context-zone {
        width: 1fr;
        margin: 1;
        border: solid $secondary;
    }
    
    /* Chat styling */
    .section-title {
        text-style: bold;
        background: $primary 20%;
        padding: 1;
        margin-bottom: 1;
    }
    
    #chat-scroll {
        height: 1fr;
        border: solid $surface;
        margin-bottom: 1;
    }
    
    .chat-messages {
        padding: 1;
    }
    
    .input-row {
        height: 3;
    }
    
    .input-row Input {
        width: 1fr;
        margin-right: 1;
    }
    
    /* Context panel styling */
    .label {
        text-style: bold;
        margin-top: 1;
        margin-bottom: 0;
    }
    
    #file-scroll {
        height: 6;
        border: solid $surface;
        margin-bottom: 1;
    }
    
    .file-list {
        padding: 1;
    }
    
    .button-group {
        margin-top: 1;
    }
    
    .button-group Button {
        width: 100%;
        margin-bottom: 1;
    }
    
    #db-status {
        margin-bottom: 1;
        padding: 1;
        border: solid $surface;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("f5", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        """Build the main application layout."""
        yield Header(show_clock=True)
        yield Horizontal(
            Vertical(
                Static("🔬 Inquiro Research Assistant", classes="section-title"),
                ChatZone(),
                id="center-zone"
            ),
            ContextManagerZone(id="context-zone"),
            id="main-horizontal"
        )
        yield Footer()

    def action_refresh(self):
        """Refresh the file list and database status."""
        context_zone = self.query_one(ContextManagerZone)
        context_zone.refresh_file_list()
        context_zone.update_database_status()
        self.query_one(ChatZone).add_system_message("Interface refreshed")

if __name__ == "__main__":
    app = InquiroTUI()
    app.run()
