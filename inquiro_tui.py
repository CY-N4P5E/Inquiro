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
from core.config import FAISS_PATH, DATA_PATH

# Import our backend functions
try:
    from core.query_data import query_rag
    from core.populate_database import main as populate_main, clear_database
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
        context_zone = self.app.query_one(ContextManagerZone)
        chat = self.app.query_one(ChatZone)
        chat.add_system_message("📁 Attempting to open file explorer...")
        context_zone.open_file_explorer()

    @on(Button.Pressed, "#add-path-btn") 
    def add_path_action(self):
        """Show input for manual path entry."""
        self.dismiss()
        context_zone = self.app.query_one(ContextManagerZone)
        chat = self.app.query_one(ChatZone)
        chat.add_system_message("📝 Opening path input dialog...")
        context_zone.show_path_input()

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
        path = self.query_one("#path-input", Input).value.strip()
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
                    self.app.call_from_thread(self.add_assistant_message, response)
                else:
                    self.app.call_from_thread(self.add_error_message, "Query function not available")
            except Exception as e:
                self.app.call_from_thread(self.add_error_message, f"Query failed: {str(e)}")
        
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
            Button("🧪 Test File Mgmt", id="test-files", variant="warning"),
            classes="button-group"
        )

    def refresh_file_list(self):
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
        if os.path.exists(FAISS_PATH) and os.path.exists(os.path.join(FAISS_PATH, 'index.faiss')):
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
                    self.app.call_from_thread(self.update_database_status)
                    self.app.call_from_thread(chat.add_system_message, "✅ Database built successfully!")
                else:
                    self.app.call_from_thread(chat.add_error_message, "Populate function not available")
            except Exception as e:
                self.app.call_from_thread(chat.add_error_message, f"Database build failed: {str(e)}")
        
        threading.Thread(target=run_populate, daemon=True).start()

    @on(Button.Pressed, "#clear-db")
    def clear_database_action(self):
        def run_clear():
            try:
                if clear_database:
                    clear_database()
                    self.app.call_from_thread(self.update_database_status)
                    self.app.call_from_thread(
                        self.app.query_one(ChatZone).add_system_message, 
                        "🗑️ Database cleared successfully"
                    )
                else:
                    self.app.call_from_thread(
                        self.app.query_one(ChatZone).add_error_message, 
                        "Clear function not available"
                    )
            except Exception as e:
                self.app.call_from_thread(
                    self.app.query_one(ChatZone).add_error_message, 
                    f"Clear failed: {str(e)}"
                )
        
        threading.Thread(target=run_clear, daemon=True).start()
        
    @on(Button.Pressed, "#manage-files")
    def manage_files_action(self):
        """Open file management dialog."""
        self.app.push_screen(FileManagerScreen())
        
    @on(Button.Pressed, "#test-files")
    def test_files_action(self):
        """Run file management tests."""
        self.add_test_files()

    def open_file_explorer(self):
        """Open Windows file explorer to select files."""
        chat = self.app.query_one(ChatZone)
        chat.add_system_message("🔍 Opening file explorer...")
        
        def run_file_dialog():
            try:
                # Try PowerShell approach first
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
                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
                )
                # Debug output for troubleshooting
                chat.add_system_message(f"[DEBUG] File dialog return code: {result.returncode}")
                chat.add_system_message(f"[DEBUG] File dialog stdout: {result.stdout}")
                chat.add_system_message(f"[DEBUG] File dialog stderr: {result.stderr}")
                if result.returncode == 0 and result.stdout.strip():
                    files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
                    if files:
                        self.app.call_from_thread(self.copy_files_to_data, files)
                    else:
                        self.app.call_from_thread(chat.add_system_message, "No files selected")
                else:
                    # Fallback: suggest manual path entry
                    self.app.call_from_thread(chat.add_error_message, f"File dialog failed. Use 'Add Files by Path' instead. STDERR: {result.stderr}")
            except Exception as e:
                self.app.call_from_thread(chat.add_error_message, f"File explorer error: {str(e)}. Use 'Add Files by Path' instead.")
        
        threading.Thread(target=run_file_dialog, daemon=True).start()

    def show_path_input(self):
        """Show input dialog for manual path entry."""
        chat = self.app.query_one(ChatZone)
        chat.add_system_message("💬 Enter file path in the dialog that appears...")
        
        def handle_path_result(path):
            if path and path.strip():
                chat.add_system_message(f"📝 Processing path: {path}")
                self.add_file_by_path(path.strip())
            else:
                chat.add_system_message("❌ No path provided")
        
        self.app.push_screen(PathInputScreen(), handle_path_result)

    def show_file_removal(self):
        """Show file selection dialog for removal."""
        chat = self.app.query_one(ChatZone)
        if not self.files:
            chat.add_error_message("❌ No files to remove")
            return
            
        chat.add_system_message("🗑️ Opening file removal dialog...")
        
        def handle_removal_result(selected_files):
            if selected_files:
                chat.add_system_message(f"🗑️ Removing {len(selected_files)} files...")
                self.remove_files(selected_files)
            else:
                chat.add_system_message("❌ No files selected for removal")
        
        self.app.push_screen(FileRemovalScreen(self.files), handle_removal_result)

    def copy_files_to_data(self, file_paths):
        """Copy selected files to the data directory."""
        chat = self.app.query_one(ChatZone)
        data_dir = DATA_PATH
        chat.add_system_message(f"[DEBUG] copy_files_to_data called with: {file_paths}")
        chat.add_system_message(f"📁 Processing {len(file_paths)} file(s)...")
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        successful = 0
        failed = 0
        for file_path in file_paths:
            try:
                chat.add_system_message(f"[DEBUG] Processing file: {file_path}")
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    destination = os.path.join(data_dir, filename)
                    # Check if file already exists
                    if os.path.exists(destination):
                        chat.add_system_message(f"⚠️ File already exists: {filename}")
                        continue
                    # Validate file type
                    if not filename.lower().endswith(('.pdf', '.txt', '.md')):
                        chat.add_error_message(f"❌ Unsupported file type: {filename}")
                        failed += 1
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
        chat.add_system_message(f"[DEBUG] copy_files_to_data finished. Successful: {successful}, Failed: {failed}")
        if successful > 0:
            chat.add_system_message(f"🎉 Successfully added {successful} file(s)!")
            chat.add_system_message("💡 Remember to rebuild the database to include new files")
        if failed > 0:
            chat.add_error_message(f"❌ Failed to add {failed} file(s)")

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
        data_dir = DATA_PATH
        
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

    def add_test_files(self):
        """Add some test functionality to verify file management works."""
        chat = self.app.query_one(ChatZone)
        chat.add_system_message("🧪 Testing file management functionality...")
        
        # Test 1: Check if data directory exists
        if os.path.exists(DATA_PATH):
            chat.add_system_message(f"✅ Data directory found: {DATA_PATH}")
        else:
            chat.add_system_message(f"⚠️ Creating data directory: {DATA_PATH}")
            try:
                os.makedirs(DATA_PATH, exist_ok=True)
                chat.add_system_message("✅ Data directory created successfully")
            except Exception as e:
                chat.add_error_message(f"❌ Failed to create data directory: {e}")
                return
        
        # Test 2: List current files
        try:
            files = os.listdir(DATA_PATH)
            pdf_files = [f for f in files if f.endswith('.pdf')]
            chat.add_system_message(f"📄 Found {len(pdf_files)} PDF files in data directory")
            for pdf in pdf_files[:3]:  # Show first 3
                chat.add_system_message(f"  • {pdf}")
        except Exception as e:
            chat.add_error_message(f"❌ Error listing files: {e}")

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

    # @on(Button.Pressed)
    # def debug_button_press(self, event: Button.Pressed) -> None:
    #     # Add a system message for any button press in the app
    #     try:
    #         chat = self.query_one(ChatZone)
    #         chat.add_system_message(f"[DEBUG] Button pressed: {event.button.id}")
    #     except Exception as e:
    #         print(f"[DEBUG] Button pressed: {getattr(event.button, 'id', None)} (ChatZone not found: {e})")


if __name__ == "__main__":
    app = InquiroTUI()
    app.run()