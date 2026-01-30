import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import time

# Shutdown signal file location
from agent.config import BASE_LOG_DIR, SHUTDOWN_SIGNAL_FILE

BASE_DIR = BASE_LOG_DIR

st.set_page_config(
    page_title="UniLogX Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ UniLogX – Advanced System Log Intelligence Dashboard")

LOGS_CACHE = {}
CACHE_TIME = 0

# =========================
# UTILITY FUNCTIONS
# =========================
def load_all_logs():
    """Load all JSON logs from the log directory"""
    all_logs = []
    
    if not os.path.exists(BASE_DIR):
        return pd.DataFrame()
    
    for root, _, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                log_entry = json.loads(line.strip())
                                if log_entry:
                                    all_logs.append(log_entry)
                            except json.JSONDecodeError:
                                continue
                except Exception as e:
                    st.warning(f"Error reading {file}: {str(e)}")
    
    if not all_logs:
        return pd.DataFrame()
    
    df = pd.DataFrame(all_logs)
    
    # Parse timestamp with format specification
    if 'timestamp' in df.columns:
        # Try ISO format first, then fallback to coercion
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601', errors='coerce')
        except:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df['date'] = df['timestamp'].dt.date
        df['hour'] = df['timestamp'].dt.hour
    
    return df

def get_log_stats(df):
    """Calculate log statistics"""
    if df.empty:
        return {
            'total_logs': 0,
            'critical_errors': 0,
            'warnings': 0,
            'info_count': 0,
            'categories': []
        }
    
    return {
        'total_logs': len(df),
        'critical_errors': len(df[df['level'].isin(['CRITICAL', 'ERROR'])]) if 'level' in df.columns else 0,
        'warnings': len(df[df['level'] == 'WARNING']) if 'level' in df.columns else 0,
        'info_count': len(df[df['level'] == 'INFO']) if 'level' in df.columns else 0,
        'categories': df['category'].unique().tolist() if 'category' in df.columns else []
    }

# =========================
# LOAD LOGS WITH CACHING
# =========================
st.sidebar.header("🔄 Controls")

col1, col2, col3 = st.sidebar.columns(3)
with col1:
    if st.button("🔄 Refresh"):
        st.rerun()

with col2:
    if st.button("⏱️ Auto Refresh"):
        time.sleep(2)
        st.rerun()

with col3:
    if st.button("🛑 Shutdown", key="stop_agent"):
        # Create shutdown signal file
        os.makedirs(os.path.dirname(SHUTDOWN_SIGNAL_FILE), exist_ok=True)
        with open(SHUTDOWN_SIGNAL_FILE, 'w') as f:
            f.write("shutdown")
        st.success("✅ Shutdown initiated!")
        st.info("Shutting down UniLogX agent and dashboard...")
        time.sleep(1)
        st.stop()  # Stop the dashboard immediately

st.sidebar.markdown("---")

# Load logs
df = load_all_logs()

if df.empty:
    st.warning("⚠️ No logs collected yet. Start the agent and wait a few seconds.")
    st.info("Logs will appear in JSONL format in the Log/ directory")
    st.stop()

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("📊 Filters")

# Date range filter
if 'timestamp' in df.columns and not df.empty:
    valid_timestamps = df['timestamp'].dropna()
    if not valid_timestamps.empty:
        min_date = valid_timestamps.min().date()
        max_date = valid_timestamps.max().date()
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="date_range"
        )
        df = df[(df['timestamp'].dt.date >= date_range[0]) & (df['timestamp'].dt.date <= date_range[1])]

# OS Type filter
if 'os_type' in df.columns:
    os_options = df['os_type'].unique().tolist()
    os_filter = st.sidebar.multiselect(
        "Operating System",
        options=os_options,
        default=os_options
    )
    df = df[df['os_type'].isin(os_filter)]

# Category filter
if 'category' in df.columns:
    cat_options = df['category'].unique().tolist()
    cat_filter = st.sidebar.multiselect(
        "Log Category",
        options=cat_options,
        default=cat_options
    )
    df = df[df['category'].isin(cat_filter)]

# Log Level filter
if 'level' in df.columns:
    level_options = df['level'].unique().tolist()
    level_filter = st.sidebar.multiselect(
        "Log Level",
        options=level_options,
        default=level_options
    )
    df = df[df['level'].isin(level_filter)]

# Search filter
search_term = st.sidebar.text_input("🔍 Search Logs")
if search_term:
    if 'message' in df.columns:
        df = df[df['message'].str.contains(search_term, case=False, na=False)]

st.sidebar.markdown("---")

# =========================
# METRICS SECTION
# =========================
stats = get_log_stats(df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📋 Total Logs", f"{stats['total_logs']:,}", delta=None)

with col2:
    st.metric("🔴 Errors", f"{stats['critical_errors']}", delta=None)

with col3:
    st.metric("⚠️ Warnings", f"{stats['warnings']}", delta=None)

with col4:
    st.metric("ℹ️ Info", f"{stats['info_count']}", delta=None)

st.markdown("---")

# =========================
# CHARTS SECTION
# =========================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Logs by Category")
    if 'category' in df.columns and not df.empty:
        category_counts = df['category'].value_counts()
        fig = px.bar(
            x=category_counts.index,
            y=category_counts.values,
            labels={'x': 'Category', 'y': 'Count'},
            color=category_counts.values,
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🔔 Logs by Level")
    if 'level' in df.columns and not df.empty:
        level_counts = df['level'].value_counts()
        colors = {
            'CRITICAL': '#FF0000',
            'ERROR': '#FF6B6B',
            'WARNING': '#FFA500',
            'INFO': '#4CAF50',
            'DEBUG': '#2196F3'
        }
        fig = px.pie(
            values=level_counts.values,
            names=level_counts.index,
            color=level_counts.index,
            color_discrete_map=colors
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

# =========================
# TIME SERIES ANALYSIS
# =========================
if 'timestamp' in df.columns and not df.empty:
    st.subheader("📈 Logs Over Time")
    
    # Filter out NaT values and check if we have valid timestamps
    df_valid = df[df['timestamp'].notna()].copy()
    
    if not df_valid.empty:
        try:
            # Group by hour
            df_hourly = df_valid.set_index('timestamp').resample('H').size()
            
            fig = px.line(
                x=df_hourly.index,
                y=df_hourly.values,
                labels={'x': 'Time', 'y': 'Log Count'},
                markers=True
            )
            fig.update_layout(height=350, hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate time-series chart: {str(e)}")
    else:
        st.info("No valid timestamp data available for time-series analysis")

# =========================
# OS DISTRIBUTION
# =========================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🖥️ Logs by Operating System")
    if 'os_type' in df.columns and not df.empty:
        os_counts = df['os_type'].value_counts()
        fig = px.bar(
            x=os_counts.index,
            y=os_counts.values,
            labels={'x': 'OS Type', 'y': 'Count'},
            color=os_counts.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📍 Logs by Host")
    if 'host' in df.columns and not df.empty:
        host_counts = df['host'].value_counts()
        fig = px.bar(
            y=host_counts.index,
            x=host_counts.values,
            labels={'x': 'Count', 'y': 'Host'},
            color=host_counts.values,
            color_continuous_scale='Teal',
            orientation='h'
        )
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# =========================
# TOP ERROR SOURCES
# =========================
if 'source' in df.columns and not df.empty:
    st.subheader("⚠️ Top Error Sources")
    error_df = df[df['level'].isin(['ERROR', 'CRITICAL'])]
    if not error_df.empty:
        error_sources = error_df['source'].value_counts().head(10)
        fig = px.bar(
            y=error_sources.index,
            x=error_sources.values,
            labels={'x': 'Count', 'y': 'Source'},
            color=error_sources.values,
            color_continuous_scale='Reds',
            orientation='h'
        )
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# =========================
# LOG TABLE
# =========================
st.markdown("---")
st.subheader("📋 Log Entries")

# Select columns to display
display_cols = ['timestamp', 'level', 'category', 'os_type', 'host', 'source', 'message']
display_cols = [col for col in display_cols if col in df.columns]

if display_cols:
    # Sort by timestamp descending
    if 'timestamp' in df.columns:
        df_display = df.sort_values('timestamp', ascending=False)
    else:
        df_display = df
    
    # Limit display to last 500 rows
    st.dataframe(
        df_display[display_cols].head(500),
        use_container_width=True,
        height=400
    )

# =========================
# EXPORT OPTIONS
# =========================
st.markdown("---")
st.subheader("📥 Export")

col1, col2, col3 = st.columns(3)

with col1:
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"unilogx_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

with col2:
    json_data = df.to_json(orient='records', date_format='iso')
    st.download_button(
        label="📥 Download JSON",
        data=json_data,
        file_name=f"unilogx_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

with col3:
    st.info("✅ Dashboard Ready")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>UniLogX Dashboard v2.0 | Advanced Log Analysis Platform</p>
    <p>Last Updated: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
