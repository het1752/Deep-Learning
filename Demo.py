# Full OpenVPN Monitoring Dashboard with Streamlit

import streamlit as st
import os
import re
import time
import psutil
from datetime import datetime

LOG_FILE = "/var/log/openvpn.log"  # Adjust if your log is in a different path

st.set_page_config(page_title="OpenVPN Dashboard", layout="wide")
st.title("OpenVPN Full Monitoring Dashboard")

# Read last N lines of the OpenVPN log
def tail_log(file_path, num_lines=200):
    try:
        with open(file_path, 'r') as f:
            return f.readlines()[-num_lines:]
    except FileNotFoundError:
        return ["Log file not found."]

# Parse connection and disconnection events
def parse_sessions(log_lines):
    sessions = []
    disconnects = []
    for line in log_lines:
        if "Peer Connection Initiated" in line:
            match = re.search(r'(\d{1,3}(?:\.\d{1,3}){3}):\d+.*CN=([\w\-]+)', line)
            if match:
                ip = match.group(1)
                cn = match.group(2)
                timestamp = line.split(' ')[0:2]
                sessions.append(("connect", cn, ip, " ".join(timestamp)))
        elif "Inactivity timeout" in line or "Connection reset" in line or "TLS Error" in line:
            match = re.search(r'CN=([\w\-]+)', line)
            if match:
                cn = match.group(1)
                timestamp = line.split(' ')[0:2]
                disconnects.append(("disconnect", cn, " ".join(timestamp), line.strip()))
    return sessions, disconnects

# Show full log
st.subheader("Recent OpenVPN Logs")
logs = tail_log(LOG_FILE)
st.text_area("Log Tail", value="".join(logs), height=250)

# Show session status
tabs = st.tabs(["Active Clients", "Disconnected Clients", "System & Tunnel Stats"])

sessions, disconnects = parse_sessions(logs)

# Active Clients Tab
with tabs[0]:
    st.subheader("Currently Connected Clients")
    if sessions:
        for s in sessions:
            st.success(f"Client: `{s[1]}` | IP: `{s[2]}` | Connected at: {s[3]}")
    else:
        st.info("No active clients detected in recent logs.")

# Disconnected Clients Tab
with tabs[1]:
    st.subheader("Recently Disconnected Clients")
    if disconnects:
        for d in disconnects:
            st.warning(f"Client: `{d[1]}` | Disconnected at: {d[2]}\nReason: {d[3]}")
    else:
        st.info("No disconnection events detected in recent logs.")

# System Stats Tab
with tabs[2]:
    st.subheader("System Resource Usage")
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    col1, col2 = st.columns(2)
    col1.metric("CPU Usage", f"{cpu}%")
    col2.metric("Memory Used", f"{mem.used // (1024**2)} MB / {mem.total // (1024**2)} MB")

    st.subheader("Tunnel Interface Traffic (tun0)")
    def get_interface_stats(interface='tun0'):
        try:
            with open("/proc/net/dev", 'r') as f:
                for line in f:
                    if interface in line:
                        data = line.split()
                        recv_bytes = int(data[1])
                        sent_bytes = int(data[9])
                        return recv_bytes, sent_bytes
        except:
            return 0, 0
        return 0, 0

    rx, tx = get_interface_stats()
    st.text(f"Received: {rx / 1024:.2f} KB | Sent: {tx / 1024:.2f} KB")

st.caption("Built for OpenVPN Monitoring")
