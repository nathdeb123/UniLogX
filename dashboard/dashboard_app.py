import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import threading
from collections import Counter
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.config import BASE_LOG_DIR, SHUTDOWN_SIGNAL_FILE, DASHBOARD_PORT, DASHBOARD_HOST

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class UniLogXDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("UniLogX – Advanced System Log Intelligence Dashboard")
        self.root.geometry("1600x900")
        
        # Styling
        self.bg_color = "#0a0a0a"
        self.primary_color = "#00d4ff"
        self.secondary_color = "#ff006e"
        self.warning_color = "#ffa500"
        self.success_color = "#00d946"
        self.error_color = "#ff0040"
        
        # Data cache
        self.all_logs = []
        self.filtered_logs = []
        self.cache_time = 0
        
        self.setup_ui()
        self.load_logs_async()
        
    def setup_ui(self):
        """Setup the main UI layout"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.bg_color)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        self.setup_header()
        
        # Main content area with sidebar
        content_frame = ctk.CTkFrame(self.main_frame, fg_color=self.bg_color)
        content_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        # Sidebar
        self.setup_sidebar(content_frame)
        
        # Main content
        self.setup_content(content_frame)
        
        # Status bar
        self.setup_status_bar()
        
    def setup_header(self):
        """Setup header with title and controls"""
        header = ctk.CTkFrame(self.main_frame, fg_color="#1a1a1a", corner_radius=10)
        header.pack(fill="x", padx=0, pady=(0, 10))
        
        title = ctk.CTkLabel(
            header,
            text="🛡️ UniLogX – Advanced System Log Intelligence Dashboard",
            font=("Segoe UI", 24, "bold"),
            text_color=self.primary_color
        )
        title.pack(padx=20, pady=10)
        
        # Control buttons
        button_frame = ctk.CTkFrame(header, fg_color="#1a1a1a")
        button_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        refresh_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Refresh",
            command=self.refresh_logs,
            fg_color=self.primary_color,
            text_color="black",
            width=100,
            height=35
        )
        refresh_btn.pack(side="left", padx=5)
        
        export_btn = ctk.CTkButton(
            button_frame,
            text="📥 Export CSV",
            command=self.export_csv,
            fg_color=self.success_color,
            text_color="black",
            width=120,
            height=35
        )
        export_btn.pack(side="left", padx=5)
        
        shutdown_btn = ctk.CTkButton(
            button_frame,
            text="🛑 Shutdown",
            command=self.shutdown_app,
            fg_color=self.error_color,
            text_color="white",
            width=100,
            height=35
        )
        shutdown_btn.pack(side="right", padx=5)
        
    def setup_sidebar(self, parent):
        """Setup sidebar with filters"""
        self.sidebar = ctk.CTkFrame(parent, fg_color="#1a1a1a", corner_radius=10, width=250)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        # Filters title
        filters_label = ctk.CTkLabel(
            self.sidebar,
            text="📊 Filters",
            font=("Segoe UI", 16, "bold"),
            text_color=self.primary_color
        )
        filters_label.pack(padx=15, pady=(15, 10))
        
        # OS Type filter
        ctk.CTkLabel(
            self.sidebar,
            text="OS Type:",
            font=("Segoe UI", 11, "bold"),
            text_color=self.primary_color
        ).pack(padx=15, pady=(10, 5), anchor="w")
        
        self.os_var = ctk.StringVar(value="all")
        self.os_menu = ctk.CTkComboBox(
            self.sidebar,
            variable=self.os_var,
            values=["all"],
            command=self.apply_filters
        )
        self.os_menu.pack(padx=15, pady=(0, 10), fill="x")
        
        # Log Level filter
        ctk.CTkLabel(
            self.sidebar,
            text="Log Level:",
            font=("Segoe UI", 11, "bold"),
            text_color=self.primary_color
        ).pack(padx=15, pady=(10, 5), anchor="w")
        
        self.level_var = ctk.StringVar(value="all")
        self.level_menu = ctk.CTkComboBox(
            self.sidebar,
            variable=self.level_var,
            values=["all"],
            command=self.apply_filters
        )
        self.level_menu.pack(padx=15, pady=(0, 10), fill="x")
        
        # Category filter
        ctk.CTkLabel(
            self.sidebar,
            text="Category:",
            font=("Segoe UI", 11, "bold"),
            text_color=self.primary_color
        ).pack(padx=15, pady=(10, 5), anchor="w")
        
        self.category_var = ctk.StringVar(value="all")
        self.category_menu = ctk.CTkComboBox(
            self.sidebar,
            variable=self.category_var,
            values=["all"],
            command=self.apply_filters
        )
        self.category_menu.pack(padx=15, pady=(0, 10), fill="x")
        
        # Search
        ctk.CTkLabel(
            self.sidebar,
            text="🔍 Search:",
            font=("Segoe UI", 11, "bold"),
            text_color=self.primary_color
        ).pack(padx=15, pady=(10, 5), anchor="w")
        
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self.sidebar,
            textvariable=self.search_var,
            placeholder_text="Search logs..."
        )
        self.search_entry.pack(padx=15, pady=(0, 10), fill="x")
        self.search_entry.bind("<KeyRelease>", lambda e: self.apply_filters())
        
        # Clear filters button
        clear_btn = ctk.CTkButton(
            self.sidebar,
            text="Clear Filters",
            command=self.clear_filters,
            fg_color="#333333",
            text_color=self.primary_color
        )
        clear_btn.pack(padx=15, pady=10, fill="x")
        
    def setup_content(self, parent):
        """Setup main content area"""
        self.content = ctk.CTkFrame(parent, fg_color="#1a1a1a", corner_radius=10)
        self.content.pack(side="left", fill="both", expand=True)
        
        # Metrics section
        self.setup_metrics(self.content)
        
        # Stats and table section
        stats_table_frame = ctk.CTkFrame(self.content, fg_color="#1a1a1a")
        stats_table_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Stats
        self.setup_stats(stats_table_frame)
        
        # Log table
        self.setup_log_table(stats_table_frame)
        
    def setup_metrics(self, parent):
        """Setup metrics display"""
        metrics_frame = ctk.CTkFrame(parent, fg_color="#1a1a1a")
        metrics_frame.pack(fill="x", padx=15, pady=15)
        
        # Create metric cards
        self.metric_cards = {}
        metrics = [
            ("📋 Total Logs", "total_logs", "0", self.primary_color),
            ("🔴 Errors", "errors", "0", self.error_color),
            ("⚠️ Warnings", "warnings", "0", self.warning_color),
            ("ℹ️ Info", "info", "0", self.success_color),
        ]
        
        for title, key, value, color in metrics:
            card = self.create_metric_card(metrics_frame, title, value, color)
            self.metric_cards[key] = card
            card.pack(side="left", fill="both", expand=True, padx=5)
    
    def create_metric_card(self, parent, title, value, color):
        """Create a metric card"""
        card = ctk.CTkFrame(parent, fg_color="#0f0f0f", corner_radius=10, border_width=2, border_color=color)
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 12, "bold"),
            text_color=color
        )
        title_label.pack(padx=15, pady=(10, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Segoe UI", 28, "bold"),
            text_color=color
        )
        value_label.pack(padx=15, pady=(0, 10))
        
        card.value_label = value_label
        return card
    
    def update_metric(self, key, value):
        """Update metric value"""
        if key in self.metric_cards:
            self.metric_cards[key].value_label.configure(text=str(value))
    
    def setup_stats(self, parent):
        """Setup statistics display"""
        stats_frame = ctk.CTkFrame(parent, fg_color="#0f0f0f", corner_radius=10, border_width=1, border_color="#333333")
        stats_frame.pack(fill="x", pady=(0, 15))
        
        stats_title = ctk.CTkLabel(
            stats_frame,
            text="📊 Log Statistics",
            font=("Segoe UI", 14, "bold"),
            text_color=self.primary_color
        )
        stats_title.pack(padx=15, pady=(10, 5), anchor="w")
        
        self.stats_text = ctk.CTkLabel(
            stats_frame,
            text="No data yet",
            font=("Segoe UI", 10),
            text_color="#888888",
            justify="left"
        )
        self.stats_text.pack(padx=15, pady=(0, 10), anchor="w")
        
    def setup_log_table(self, parent):
        """Setup log table"""
        table_frame = ctk.CTkFrame(parent, fg_color="#0f0f0f", corner_radius=10, border_width=1, border_color="#333333")
        table_frame.pack(fill="both", expand=True)
        
        table_title = ctk.CTkLabel(
            table_frame,
            text="📋 Recent Logs",
            font=("Segoe UI", 14, "bold"),
            text_color=self.primary_color
        )
        table_title.pack(padx=15, pady=(10, 10), anchor="w")
        
        # Create treeview for logs
        columns = ("Time", "Level", "Category", "OS", "Host", "Message")
        
        # Create frame for treeview
        tree_frame = ctk.CTkFrame(table_frame, fg_color="#0f0f0f")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Treeview with custom style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                       background="#1a1a1a",
                       foreground="#00d4ff",
                       fieldbackground="#1a1a1a",
                       font=("Segoe UI", 9))
        style.configure("Treeview.Heading",
                       background="#0f0f0f",
                       foreground="#00d4ff",
                       font=("Segoe UI", 10, "bold"))
        style.map('Treeview', background=[('selected', '#0066cc')])
        
        self.tree = ttk.Treeview(tree_frame, columns=columns, height=20, show="headings")
        
        for col in columns:
            self.tree.column(col, width=150, anchor="w")
            self.tree.heading(col, text=col)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def setup_status_bar(self):
        """Setup status bar"""
        status_frame = ctk.CTkFrame(self.main_frame, fg_color="#0a0a0a", height=30)
        status_frame.pack(fill="x", padx=0, pady=(10, 0))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready | Loading logs...",
            font=("Segoe UI", 10),
            text_color="#888888"
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
    def load_logs(self):
        """Load all logs from disk"""
        try:
            self.all_logs = []
            if not os.path.exists(BASE_LOG_DIR):
                return
            
            for root, _, files in os.walk(BASE_LOG_DIR):
                for file in files:
                    if file.endswith(".json"):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                for line in f:
                                    try:
                                        log_entry = json.loads(line.strip())
                                        if log_entry:
                                            self.all_logs.append(log_entry)
                                    except json.JSONDecodeError:
                                        continue
                        except Exception as e:
                            print(f"Error reading {file}: {str(e)}")
            
            self.update_ui()
            
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}")
    
    def load_logs_async(self):
        """Load logs in a separate thread"""
        thread = threading.Thread(target=self.load_logs, daemon=True)
        thread.start()
    
    def update_ui(self):
        """Update all UI elements"""
        # Update filters
        self.update_filter_options()
        
        # Apply current filters
        self.apply_filters()
        
        # Update status
        self.status_label.configure(
            text=f"Ready | {len(self.all_logs)} logs loaded | Last updated: {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def update_filter_options(self):
        """Update filter dropdown options"""
        if not self.all_logs:
            return
        
        df = pd.DataFrame(self.all_logs)
        
        # OS Types
        os_types = ["all"] + sorted(df['os_type'].unique().tolist()) if 'os_type' in df.columns else ["all"]
        self.os_menu.configure(values=os_types)
        
        # Log Levels
        levels = ["all"] + sorted(df['level'].unique().tolist()) if 'level' in df.columns else ["all"]
        self.level_menu.configure(values=levels)
        
        # Categories
        categories = ["all"] + sorted(df['category'].unique().tolist()) if 'category' in df.columns else ["all"]
        self.category_menu.configure(values=categories)
    
    def apply_filters(self):
        """Apply filters to logs"""
        if not self.all_logs:
            self.filtered_logs = []
            self.update_display()
            return
        
        df = pd.DataFrame(self.all_logs)
        
        # Apply filters
        if self.os_var.get() != "all":
            df = df[df['os_type'] == self.os_var.get()]
        
        if self.level_var.get() != "all":
            df = df[df['level'] == self.level_var.get()]
        
        if self.category_var.get() != "all":
            df = df[df['category'] == self.category_var.get()]
        
        search = self.search_var.get().lower()
        if search and 'message' in df.columns:
            df = df[df['message'].str.lower().str.contains(search, na=False)]
        
        self.filtered_logs = df.to_dict('records')
        self.update_display()
    
    def update_display(self):
        """Update table and metrics"""
        if not self.filtered_logs:
            # Update metrics to 0
            self.update_metric("total_logs", 0)
            self.update_metric("errors", 0)
            self.update_metric("warnings", 0)
            self.update_metric("info", 0)
            self.update_stats_text("")
            self.tree.delete(*self.tree.get_children())
            return
        
        df = pd.DataFrame(self.filtered_logs)
        
        # Update metrics
        self.update_metric("total_logs", len(df))
        
        errors = len(df[df['level'].isin(['ERROR', 'CRITICAL'])]) if 'level' in df.columns else 0
        self.update_metric("errors", errors)
        
        warnings = len(df[df['level'] == 'WARNING']) if 'level' in df.columns else 0
        self.update_metric("warnings", warnings)
        
        info = len(df[df['level'] == 'INFO']) if 'level' in df.columns else 0
        self.update_metric("info", info)
        
        # Update stats
        if 'os_type' in df.columns:
            os_counts = df['os_type'].value_counts().to_dict()
            stats_text = "OS Distribution: " + ", ".join([f"{k}: {v}" for k, v in list(os_counts.items())[:3]])
        else:
            stats_text = ""
        
        self.update_stats_text(stats_text)
        
        # Update table
        self.tree.delete(*self.tree.get_children())
        
        # Sort by timestamp descending if available
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp', ascending=False)
        
        # Display last 100 logs
        for idx, row in df.head(100).iterrows():
            timestamp = str(row.get('timestamp', ''))[:19]
            level = row.get('level', '')
            category = row.get('category', '')
            os_type = row.get('os_type', '')
            host = row.get('host', '')
            message = str(row.get('message', ''))[:50]
            
            # Color based on level
            tags = []
            if level == 'ERROR':
                tags = ['error']
            elif level == 'WARNING':
                tags = ['warning']
            elif level == 'CRITICAL':
                tags = ['critical']
            
            self.tree.insert("", "end", values=(timestamp, level, category, os_type, host, message), tags=tags)
        
        # Configure tag colors
        self.tree.tag_configure('error', foreground='#ff6b6b')
        self.tree.tag_configure('warning', foreground='#ffa500')
        self.tree.tag_configure('critical', foreground='#ff0040')
    
    def update_stats_text(self, text):
        """Update stats text"""
        self.stats_text.configure(text=text if text else "No statistics available")
    
    def clear_filters(self):
        """Clear all filters"""
        self.os_var.set("all")
        self.level_var.set("all")
        self.category_var.set("all")
        self.search_var.set("")
        self.apply_filters()
    
    def refresh_logs(self):
        """Refresh logs"""
        self.status_label.configure(text="Refreshing logs...")
        self.load_logs_async()
    
    def export_csv(self):
        """Export logs to CSV"""
        if not self.filtered_logs:
            messagebox.showwarning("Export", "No logs to export")
            return
        
        try:
            df = pd.DataFrame(self.filtered_logs)
            filename = f"unilogx_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            messagebox.showinfo("Export", f"Logs exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting logs: {str(e)}")
    
    def shutdown_app(self):
        """Shutdown the application"""
        if messagebox.askyesno("Shutdown", "Are you sure you want to shutdown UniLogX?"):
            try:
                os.makedirs(os.path.dirname(SHUTDOWN_SIGNAL_FILE), exist_ok=True)
                with open(SHUTDOWN_SIGNAL_FILE, 'w') as f:
                    f.write("shutdown")
                messagebox.showinfo("Shutdown", "Shutdown signal sent")
                self.root.after(1000, self.root.quit)
            except Exception as e:
                messagebox.showerror("Error", f"Error shutting down: {str(e)}")

def run_dashboard():
    """Run the dashboard"""
    root = ctk.CTk()
    app = UniLogXDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    run_dashboard()
