import streamlit as st

def inject_css():
    st.markdown("""
    <style>
    .main .block-container {max-width: 1400px; padding-top: 1.2rem;}
    .hero {
        padding: 28px 32px; border-radius: 18px;
        background: linear-gradient(135deg,#111827,#1e293b);
        color: white; margin-bottom: 20px;
    }
    .hero h1 {margin:0 0 6px 0; font-size: 2.15rem;}
    .hero p {margin:0;color:#cbd5e1;}
    .card {
        padding: 18px; border: 1px solid rgba(128,128,128,.2);
        border-radius: 14px; margin-bottom: 12px;
        background: rgba(128,128,128,.035);
    }
    .metric {
        padding: 18px; border-radius: 14px;
        border:1px solid rgba(128,128,128,.2);
        background: rgba(128,128,128,.035);
    }
    .badge {display:inline-block;padding:4px 9px;border-radius:999px;font-size:.75rem;
        border:1px solid rgba(128,128,128,.25); margin-right:4px;}
    .muted {color:#64748b;font-size:.88rem;}
    code {border-radius:5px;}
    .doc-title {font-size:1.35rem;font-weight:700;margin-bottom:5px;}
    .sidebar-note {font-size:.8rem;color:#64748b;}
    </style>
    """, unsafe_allow_html=True)

def badge(text):
    st.markdown(f'<span class="badge">{text}</span>', unsafe_allow_html=True)
