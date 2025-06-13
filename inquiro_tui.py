from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static, Input, ProgressBar, Label, SelectionList
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.reactive import reactive
from textual.screen import Screen, ModalScreen
from textual.message import Message
from textual import on
import os
import asyncio
import subprocess
import sys
from datetime import datetime
import threading
import shutil
from config import FAISS_PATH, DATA_PATH

# Import our backend functions
try:
    from query_data import query_rag
    from populate_database import main as populate_main, clear_database
except ImportError as e:
    print(f"Warning: Could not import backend functions: {e}")
    query_rag = None
    populate_main = None

class FileManagerScreen(ModalScreen):
    """Modal screen for file management operations."""
    
    def compose(self) -> ComposeResult:
        with Container(id="file-manager-dialog"):
            yield Static("📁 File Management", classes="dialog-title")
            yield Static("Select an action:", classes="dialog-subtitle")
            yield Vertical(
                Button("📥 Add Files from Explorer", id="add-files-btn", variant="primary"),
                Button("📤 Add Files by Path", id="add-path-btn", variant="default"),
                Button("🗑️ Remove Selected Files", id="remove-files-btn", variant="error"),
                Button("❌ Cancel", id="cancel-btn", variant="default"),
                classes="dialog-buttons"
            )

    @on(Button.Pressed, "#add-files-btn")
    def add_files_action(self):
        """Open Windows file explorer to select files."""
        self.dismiss()
        self.app.query_one(ContextManagerZone).open_file_explorer()

    @on(Button.Pressed, "#add-path-btn") 
    def add_path_action(self):
        """Show input for manual path entry."""
        self.dismiss()
        self.app.query_one(ContextManagerZone).show_path_input()

    @on(Button.Pressed, "#remove-files-btn")
    def remove_files_action(self):
        """Show file selection for removal."""
        self.dismiss()
        self.app.query_one(ContextManagerZone).show_file_removal()

    @on(Button.Pressed, "#cancel-btn")
    def cancel_action(self):
        self.dismiss()

class FileRemovalScreen(ModalScreen):
    """Modal screen for selecting files to remove."""
    
    def __init__(self, files):
        super().__init__()
        self.files = files
    
    def compose(self) -> ComposeResult:
        with Container(id="file-removal-dialog"):
            yield Static("🗑️ Remove Files", classes="dialog-title")
            yield Static("Select files to remove:", classes="dialog-subtitle")
            
            # Create selection list of files
            options = [(file, file) for file in self.files]
            self.file_selection = SelectionList(*options, id="file-selection")
            yield self.file_selection
            
            yield Horizontal(
                Button("Remove Selected", id="confirm-remove-btn", variant="error"),
                Button("Cancel", id="cancel-remove-btn", variant="default"),
                classes="dialog-buttons"
            )

    @on(Button.Pressed, "#confirm-remove-btn")
    def confirm_remove_action(self):
        selected_files = [self.files[i] for i in self.file_selection.selected]
        self.dismiss(selected_files)

    @on(Button.Pressed, "#cancel-remove-btn")
    def cancel_remove_action(self):
        self.dismiss(None)

class PathInputScreen(ModalScreen):
    """Modal screen for manual path input."""
    
    def compose(self) -> ComposeResult:
        with Container(id="path-input-dialog"):
            yield Static("📤 Add File by Path", classes="dialog-title")
            yield Static("Enter the full path to the file:", classes="dialog-subtitle")
            yield Input(placeholder="C:\\path\\to\\your\\file.pdf", id="path-input")
            yield Horizontal(
                Button("Add File", id="confirm-path-btn", variant="primary"),
                Button("Cancel", id="cancel-path-btn", variant="default"),
                classes="dialog-buttons"
            )

    @on(Button.Pressed, "#confirm-path-btn")
    def confirm_path_action(self):
        path = self.query_one("#path-input").value.strip()
        self.dismiss(path if path else None)

    @on(Button.Pressed, "#cancel-path-btn")
    def cancel_path_action(self):
        self.dismiss(None)

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
        if not os.path.exists(FAISS_PATH):
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
            Button("📂 Manage Files", id="manage-files", variant="success"),
            Button("🔄 Populate Database", id="populate-db", variant="primary"),
            Button("🗑️ Clear Database", id="clear-db", variant="error"),
            classes="button-group"
        )    def refresh_file_list(self):
        """Update the file list from the data directory."""
        if os.path.exists(DATA_PATH):
            all_files = os.listdir(DATA_PATH)
            self.files = [f for f in all_files if f.endswith(('.pdf', '.txt', '.md'))]
        else:
            self.files = []
        
        if self.files:
            file_display = "\n".join([f"• {f}" for f in self.files])
        else:
            file_display = f"No documents found in {DATA_PATH}"
        
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
        
        threading.Thread(target=run_clear, daemon=True).start()    @on(Button.Pressed, "#manage-files")
    def manage_files_action(self):
        """Open file management dialog."""
        self.app.push_screen(FileManagerScreen())

    def open_file_explorer(self):
        """Open Windows file explorer to select files."""
        try:
            # Use PowerShell to open file dialog for Windows
            chat = self.app.query_one(ChatZone)
            chat.add_system_message("🔍 Opening file explorer...")
            
            def run_file_dialog():
                try:
                    # PowerShell script to open file dialog
                    ps_script = '''
Add-Type -AssemblyName System.Windows.Forms;
$dialog = New-Object System.Windows.Forms.OpenFileDialog;
$dialog.Filter = "Document files (*.pdf;*.txt;*.md)|*.pdf;*.txt;*.md|All files (*.*)|*.*";
$dialog.Multiselect = $true;
$dialog.Title = "Select documents to add to Inquiro";
if ($dialog.ShowDialog() -eq "OK") {
    $dialog.FileNames
}
'''
                    result = subprocess.run(
                        ["powershell", "-Command", ps_script],
                        capture_output=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    if result.returncode == 0 and result.stdout.strip():
                        files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
                        if files:
                            self.call_from_thread(self.copy_files_to_data, files)
                        else:
                            self.call_from_thread(chat.add_system_message, "No files selected")
                    else:
                        self.call_from_thread(chat.add_system_message, "File selection cancelled")
                except Exception as e:
                    self.call_from_thread(chat.add_error_message, f"File explorer error: {str(e)}")
            
            threading.Thread(target=run_file_dialog, daemon=True).start()
            
        except Exception as e:
            self.app.query_one(ChatZone).add_error_message(f"Could not open file explorer: {str(e)}")

    def show_path_input(self):
        """Show input dialog for manual path entry."""
        def handle_path_result(path):
            if path:
                self.add_file_by_path(path)
        
        self.app.push_screen(PathInputScreen(), handle_path_result)

    def show_file_removal(self):
        """Show file selection dialog for removal."""
        if not self.files:
            self.app.query_one(ChatZone).add_error_message("No files to remove")
            return
            
        def handle_removal_result(selected_files):
            if selected_files:
                self.remove_files(selected_files)
        
        self.app.push_screen(FileRemovalScreen(self.files), handle_removal_result)

    def copy_files_to_data(self, file_paths):
        """Copy selected files to the data directory."""
        chat = self.app.query_one(ChatZone)
        data_dir = os.path.join(os.getcwd(), "data")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        successful = 0
        failed = 0
        
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    destination = os.path.join(data_dir, filename)
                    
                    # Check if file already exists
                    if os.path.exists(destination):
                        chat.add_system_message(f"⚠️ File already exists: {filename}")
                        continue
                    
                    # Copy the file
                    shutil.copy2(file_path, destination)
                    chat.add_system_message(f"✅ Added: {filename}")
                    successful += 1
                else:
                    chat.add_error_message(f"❌ File not found: {file_path}")
                    failed += 1
            except Exception as e:
                chat.add_error_message(f"❌ Failed to copy {os.path.basename(file_path)}: {str(e)}")
                failed += 1
        
        # Update file list and show summary
        self.refresh_file_list()
        if successful > 0:
            chat.add_system_message(f"📁 Added {successful} file(s) successfully")
        if failed > 0:
            chat.add_error_message(f"Failed to add {failed} file(s)")

    def add_file_by_path(self, file_path):
        """Add a single file by path."""
        chat = self.app.query_one(ChatZone)
        
        if not file_path:
            chat.add_error_message("No file path provided")
            return
        
        # Validate file exists and has correct extension
        if not os.path.exists(file_path):
            chat.add_error_message(f"File not found: {file_path}")
            return
        
        if not file_path.lower().endswith(('.pdf', '.txt', '.md')):
            chat.add_error_message("Only PDF, TXT, and MD files are supported")
            return
        
        self.copy_files_to_data([file_path])

    def remove_files(self, filenames):
        """Remove selected files from the data directory."""
        chat = self.app.query_one(ChatZone)
        data_dir = os.path.join(os.getcwd(), "data")
        
        successful = 0
        failed = 0
        
        for filename in filenames:
            try:
                file_path = os.path.join(data_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    chat.add_system_message(f"🗑️ Removed: {filename}")
                    successful += 1
                else:
                    chat.add_error_message(f"❌ File not found: {filename}")
                    failed += 1
            except Exception as e:
                chat.add_error_message(f"❌ Failed to remove {filename}: {str(e)}")
                failed += 1
        
        # Update file list and show summary
        self.refresh_file_list()
        if successful > 0:
            chat.add_system_message(f"🗑️ Removed {successful} file(s) successfully")
            # Suggest rebuilding database if files were removed
            if successful > 0:
                chat.add_system_message("💡 Consider rebuilding the database after removing files")
        if failed > 0:
            chat.add_error_message(f"Failed to remove {failed} file(s)")

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
    
    /* Modal dialog styling */
    #file-manager-dialog, #file-removal-dialog, #path-input-dialog {
        width: 60;
        height: auto;
        border: thick $primary;
        background: $surface;
        margin: 2;
        padding: 2;
    }
    
    .dialog-title {
        text-style: bold;
        text-align: center;
        background: $primary 20%;
        padding: 1;
        margin-bottom: 1;
    }
    
    .dialog-subtitle {
        text-align: center;
        margin-bottom: 1;
    }
    
    .dialog-buttons {
        margin-top: 1;
    }
    
    .dialog-buttons Button {
        width: 100%;
        margin-bottom: 1;
    }
    
    #file-selection {
        height: 10;
        border: solid $surface;
        margin-bottom: 1;
    }
    
    #path-input {
        width: 100%;
        margin-bottom: 1;
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
