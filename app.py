import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime, date

# MUST be first Streamlit command
st.set_page_config(
    page_title="Home Healthcare Analytics",
    page_icon="🏥",
    layout="wide"
)

from config import Config
from data_processor import DataProcessor
from fee_calculator import FeeCalculator
from data_storage import DataStorage
from client_service_manager import ClientServiceManager
from utils import export_to_csv, format_currency
from database import init_db
from db_service import DatabaseService

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize database on first run
@st.cache_resource
def initialize_database():
    """Initialize database tables and seed data"""
    init_db()
    return True

# Initialize database
initialize_database()

# Initialize session state
if 'data_storage' not in st.session_state:
    st.session_state.data_storage = DataStorage()
if 'fee_calculator' not in st.session_state:
    st.session_state.fee_calculator = FeeCalculator()
if 'client_service_manager' not in st.session_state:
    st.session_state.client_service_manager = ClientServiceManager()
if 'db_service' not in st.session_state:
    st.session_state.db_service = DatabaseService()
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None
if 'manual_entries' not in st.session_state:
    st.session_state.manual_entries = []
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Comprehensive Neumorphism UI Design System
st.markdown("""
<style>
    /* ===== GLOBAL NEUMORPHIC FOUNDATION ===== */
    
    /* Global body and html background */
    html, body {
        background-color: #E0E5EC !important;
    }
    
    /* Document body background */
    body {
        background: #E0E5EC !important;
    }
    
    /* Main app background */
    .main .block-container {
        background-color: #E0E5EC !important;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Streamlit main content area */
    .stApp {
        background-color: #E0E5EC !important;
    }
    
    /* Root element background */
    #root {
        background-color: #E0E5EC !important;
    }
    
    /* Root variables for consistency */
    :root {
        --bg-color: #E0E5EC;
        --primary-color: #F9F9FB;
        --accent-color: #6C63FF;
        --shadow-color: #A3B1C6;
        --highlight-color: #FFFFFF;
        --text-primary: #4A5568;
        --text-secondary: #6B7280;
        --text-accent: #6C63FF;
    }
    
    /* ===== NEUMORPHIC BASE STYLES ===== */
    
    .neumorphic-base {
        background: var(--primary-color);
        border-radius: 20px;
        box-shadow: 
            9px 9px 16px var(--shadow-color),
            -9px -9px 16px var(--highlight-color);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: none;
    }
    
    .neumorphic-pressed {
        background: var(--primary-color);
        border-radius: 20px;
        box-shadow: 
            inset 6px 6px 12px var(--shadow-color),
            inset -6px -6px 12px var(--highlight-color);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .neumorphic-card {
        background: var(--primary-color);
        border-radius: 24px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 
            12px 12px 24px var(--shadow-color),
            -12px -12px 24px var(--highlight-color);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .neumorphic-card:hover {
        transform: translateY(-2px);
        box-shadow: 
            15px 15px 30px var(--shadow-color),
            -15px -15px 30px var(--highlight-color);
    }
    
    /* ===== SIDEBAR NEUMORPHIC STYLING ===== */
    
    .css-1d391kg {
        background-color: var(--bg-color) !important;
        border-right: none !important;
    }
    
    .stSidebar > div {
        background-color: var(--bg-color) !important;
        padding: 1rem;
    }
    
    .stRadio > div {
        background: var(--primary-color);
        border-radius: 20px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 
            8px 8px 16px var(--shadow-color),
            -8px -8px 16px var(--highlight-color);
    }
    
    .stRadio > div > label {
        color: var(--text-primary) !important;
        font-weight: 500;
        padding: 12px 20px;
        border-radius: 14px;
        margin: 4px 0;
        transition: all 0.3s ease;
        display: block;
    }
    
    .stRadio > div > label:hover {
        background: var(--primary-color);
        box-shadow: 
            inset 4px 4px 8px var(--shadow-color),
            inset -4px -4px 8px var(--highlight-color);
        transform: scale(0.98);
    }
    
    /* ===== NEUMORPHIC BUTTONS ===== */
    
    .stButton > button {
        background: var(--primary-color) !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 12px 24px !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        box-shadow: 
            8px 8px 16px var(--shadow-color),
            -8px -8px 16px var(--highlight-color) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        transform: translateZ(0);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 
            10px 10px 20px var(--shadow-color),
            -10px -10px 20px var(--highlight-color) !important;
        color: var(--accent-color) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
        box-shadow: 
            inset 4px 4px 8px var(--shadow-color),
            inset -4px -4px 8px var(--highlight-color) !important;
    }
    
    /* Primary button accent */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-color), #5A52CC) !important;
        color: white !important;
        box-shadow: 
            8px 8px 16px rgba(108, 99, 255, 0.3),
            -8px -8px 16px var(--highlight-color) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        box-shadow: 
            10px 10px 20px rgba(108, 99, 255, 0.4),
            -10px -10px 20px var(--highlight-color) !important;
        transform: translateY(-2px) !important;
    }
    
    /* ===== NEUMORPHIC INPUT FIELDS ===== */
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input,
    .stTimeInput > div > div > input {
        background: var(--primary-color) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        box-shadow: 
            inset 4px 4px 8px var(--shadow-color),
            inset -4px -4px 8px var(--highlight-color) !important;
        color: var(--text-primary) !important;
        transition: all 0.3s ease !important;
    }
    
    /* Specific number input styling */
    div[data-testid="stNumberInputContainer"],
    div[data-testid="stNumberInputContainer"] > div,
    [data-testid="stNumberInputField"] {
        background: var(--primary-color) !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 
            inset 4px 4px 8px var(--shadow-color),
            inset -4px -4px 8px var(--highlight-color) !important;
        color: var(--text-primary) !important;
        transition: all 0.3s ease !important;
    }
    
    /* Specific date input styling */
    [data-testid="stDateInputField"],
    .stDateInput > div > div,
    .stDateInput input {
        background: var(--primary-color) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        box-shadow: 
            inset 4px 4px 8px var(--shadow-color),
            inset -4px -4px 8px var(--highlight-color) !important;
        color: var(--text-primary) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    [data-testid="stNumberInputField"]:focus,
    [data-testid="stDateInputField"]:focus {
        box-shadow: 
            inset 6px 6px 12px var(--shadow-color),
            inset -6px -6px 12px var(--highlight-color),
            0 0 0 3px rgba(108, 99, 255, 0.1) !important;
        outline: none !important;
    }
    
    /* ===== NEUMORPHIC SELECT BOXES ===== */
    
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: var(--primary-color) !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 
            inset 4px 4px 8px var(--shadow-color),
            inset -4px -4px 8px var(--highlight-color) !important;
    }
    
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div > div {
        color: var(--text-primary) !important;
        padding: 12px 16px !important;
    }
    
    /* ===== NEUMORPHIC METRICS ===== */
    
    .metric-card {
        background: var(--primary-color);
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        box-shadow: 
            10px 10px 20px var(--shadow-color),
            -10px -10px 20px var(--highlight-color);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin: 15px 0;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 
            12px 12px 24px var(--shadow-color),
            -12px -12px 24px var(--highlight-color);
    }
    
    .metric-value {
        font-size: 2.5em;
        font-weight: 700;
        color: var(--accent-color);
        margin-bottom: 8px;
        text-shadow: 2px 2px 4px rgba(108, 99, 255, 0.1);
    }
    
    .metric-label {
        color: var(--text-secondary);
        font-size: 1em;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* ===== NEUMORPHIC SERVICE CARDS ===== */
    
    .service-card {
        background: var(--primary-color);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 
            10px 10px 20px var(--shadow-color),
            -10px -10px 20px var(--highlight-color);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-left: 4px solid transparent;
    }
    
    .service-card.high-priority {
        border-left: 4px solid #FF6B6B;
        background: linear-gradient(135deg, var(--primary-color), #FFF5F5);
    }
    
    .service-card.medium-priority {
        border-left: 4px solid #FFB946;
        background: linear-gradient(135deg, var(--primary-color), #FFFBF0);
    }
    
    .service-card.low-priority {
        border-left: 4px solid #51CF66;
        background: linear-gradient(135deg, var(--primary-color), #F0FFF4);
    }
    
    .service-card:hover {
        transform: translateY(-3px);
        box-shadow: 
            12px 12px 24px var(--shadow-color),
            -12px -12px 24px var(--highlight-color);
    }
    
    /* ===== NEUMORPHIC PROGRESS BARS ===== */
    
    .progress-container {
        background: var(--primary-color);
        border-radius: 15px;
        padding: 4px;
        box-shadow: 
            inset 3px 3px 6px var(--shadow-color),
            inset -3px -3px 6px var(--highlight-color);
        margin: 15px 0;
    }
    
    .progress-bar {
        height: 12px;
        background: linear-gradient(90deg, var(--accent-color), #8B7EFF);
        border-radius: 12px;
        transition: width 1.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            2px 2px 4px rgba(108, 99, 255, 0.3),
            -1px -1px 2px rgba(255, 255, 255, 0.8);
    }
    
    /* ===== NEUMORPHIC TABLES ===== */
    
    .dataframe {
        background: var(--primary-color) !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 
            8px 8px 16px var(--shadow-color),
            -8px -8px 16px var(--highlight-color) !important;
        transition: all 0.3s ease !important;
        margin: 20px 0 !important;
    }
    
    .dataframe:hover {
        transform: translateY(-1px);
        box-shadow: 
            10px 10px 20px var(--shadow-color),
            -10px -10px 20px var(--highlight-color) !important;
    }
    
    .dataframe th {
        background: linear-gradient(135deg, var(--primary-color), #F0F0F0) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        padding: 15px !important;
        border: none !important;
    }
    
    .dataframe td {
        color: var(--text-primary) !important;
        padding: 12px !important;
        border: none !important;
        border-bottom: 1px solid rgba(163, 177, 198, 0.1) !important;
    }
    
    /* ===== NEUMORPHIC HEADINGS ===== */
    
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: var(--text-primary) !important;
        text-shadow: 
            2px 2px 4px rgba(255, 255, 255, 0.8),
            -1px -1px 2px rgba(163, 177, 198, 0.3) !important;
        font-weight: 700 !important;
        margin: 20px 0 15px 0 !important;
    }
    
    /* ===== NEUMORPHIC LOADING ANIMATIONS ===== */
    
    .healthcare-loader {
        background: var(--primary-color);
        border-radius: 24px;
        padding: 40px;
        text-align: center;
        box-shadow: 
            12px 12px 24px var(--shadow-color),
            -12px -12px 24px var(--highlight-color);
        margin: 30px 0;
    }
    
    .pulse-heart {
        font-size: 3em;
        color: #FF6B6B;
        animation: heartbeat 1.5s ease-in-out infinite;
        margin-bottom: 20px;
        filter: drop-shadow(2px 2px 4px rgba(255, 107, 107, 0.3));
    }
    
    .spinning-cross {
        font-size: 2.5em;
        color: var(--accent-color);
        animation: spin 2s linear infinite;
        margin-bottom: 20px;
        filter: drop-shadow(2px 2px 4px rgba(108, 99, 255, 0.3));
    }
    
    .loading-text {
        font-size: 1.3em;
        color: var(--text-primary);
        font-weight: 600;
        margin-top: 20px;
        text-shadow: 
            1px 1px 2px rgba(255, 255, 255, 0.8),
            -1px -1px 2px rgba(163, 177, 198, 0.3);
    }
    
    .loading-subtitle {
        font-size: 1em;
        color: var(--text-secondary);
        margin-top: 10px;
        font-weight: 400;
    }
    
    /* ===== ANIMATIONS ===== */
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes heartbeat {
        0% { transform: scale(1); }
        25% { transform: scale(1.2); }
        50% { transform: scale(1); }
        75% { transform: scale(1.15); }
        100% { transform: scale(1); }
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-15px); }
        60% { transform: translateY(-7px); }
    }
    
    @keyframes wave {
        0% { transform: rotate(0deg); }
        25% { transform: rotate(10deg); }
        50% { transform: rotate(0deg); }
        75% { transform: rotate(-10deg); }
        100% { transform: rotate(0deg); }
    }
    
    /* ===== NEUMORPHIC CONTAINERS ===== */
    
    .neumorphic-container {
        background: var(--primary-color);
        border-radius: 24px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 
            12px 12px 24px var(--shadow-color),
            -12px -12px 24px var(--highlight-color);
    }
    
    .neumorphic-section {
        background: var(--primary-color);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 
            8px 8px 16px var(--shadow-color),
            -8px -8px 16px var(--highlight-color);
    }
    
    /* ===== RESPONSIVE DESIGN ===== */
    
    @media (max-width: 768px) {
        .neumorphic-card, .neumorphic-container {
            padding: 20px;
            margin: 15px 0;
        }
        
        .metric-card {
            padding: 20px;
            margin: 10px 0;
        }
        
        .service-card {
            padding: 20px;
            margin: 10px 0;
        }
    }
    
    /* ===== NEUMORPHIC EXPANDERS ===== */
    
    /* Main expander container - strongest specificity */
    div[data-testid="stExpander"],
    .stExpander,
    .stExpander > div:first-child {
        background: var(--primary-color) !important;
        border: none !important;
        border-radius: 16px !important;
        box-shadow: 
            8px 8px 16px var(--shadow-color),
            -8px -8px 16px var(--highlight-color) !important;
        margin: 15px 0 !important;
        overflow: hidden !important;
    }
    
    /* Expander header/summary - multiple selectors for higher specificity */
    div[data-testid="stExpander"] summary,
    .stExpander summary,
    .stExpander details summary,
    div[data-testid="stExpander"] > div > details > summary {
        background: var(--primary-color) !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 16px 20px !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 
            6px 6px 12px var(--shadow-color),
            -6px -6px 12px var(--highlight-color) !important;
        margin: 0 !important;
    }
    
    /* Expander header hover state */
    div[data-testid="stExpander"] summary:hover,
    .stExpander summary:hover,
    .stExpander details summary:hover {
        background: linear-gradient(135deg, var(--primary-color), #F0F0F0) !important;
        transform: translateY(-1px) !important;
        box-shadow: 
            8px 8px 16px var(--shadow-color),
            -8px -8px 16px var(--highlight-color) !important;
    }
    
    /* Expander content area when expanded */
    div[data-testid="stExpander"] > div:last-child,
    .stExpander > div:last-child,
    .stExpander details > div:last-child {
        background: var(--primary-color) !important;
        border: none !important;
        border-radius: 0px 0px 16px 16px !important;
        padding: 20px !important;
        margin: 0 !important;
        box-shadow: 
            inset 2px 2px 4px var(--shadow-color),
            inset -2px -2px 4px var(--highlight-color) !important;
    }
    
    /* Expander details element */
    div[data-testid="stExpander"] details,
    .stExpander details {
        background: var(--primary-color) !important;
        border: none !important;
        border-radius: 16px !important;
        box-shadow: 
            8px 8px 16px var(--shadow-color),
            -8px -8px 16px var(--highlight-color) !important;
        margin: 0 !important;
    }
    
    /* Force shadow on all expander children */
    .stExpander,
    .stExpander > *,
    div[data-testid="stExpander"],
    div[data-testid="stExpander"] > * {
        box-shadow: 
            8px 8px 16px var(--shadow-color),
            -8px -8px 16px var(--highlight-color) !important;
    }
    
    /* ===== STREAMLIT COMPONENT OVERRIDES ===== */
    
    .stApp > header {
        background: transparent !important;
    }
    
    .stMarkdown {
        color: var(--text-primary) !important;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, #F0FFF4, var(--primary-color)) !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 
            6px 6px 12px var(--shadow-color),
            -6px -6px 12px var(--highlight-color) !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #FFF5F5, var(--primary-color)) !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 
            6px 6px 12px var(--shadow-color),
            -6px -6px 12px var(--highlight-color) !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #FFFBF0, var(--primary-color)) !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 
            6px 6px 12px var(--shadow-color),
            -6px -6px 12px var(--highlight-color) !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #F0F8FF, var(--primary-color)) !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 
            6px 6px 12px var(--shadow-color),
            -6px -6px 12px var(--highlight-color) !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏥 Home Healthcare Analytics")
st.markdown("Analyze client visit frequencies, calculate service fees, and maintain historical records")

# Helper functions for animated displays
def create_animated_service_card(service_name, count, percentage, priority_level="low"):
    """Create an animated service card with visual hierarchy"""
    priority_class = f"service-card {priority_level}-priority"
    
    return f"""
    <div class="{priority_class}">
        <h3 style="color: white; margin: 0 0 10px 0;">{service_name}</h3>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="metric-value" style="color: white; font-size: 1.8em;">{count}</div>
                <div class="metric-label" style="color: rgba(255,255,255,0.8);">Total Visits</div>
            </div>
            <div style="text-align: right;">
                <div style="color: white; font-size: 1.2em; font-weight: bold;">{percentage:.1f}%</div>
                <div style="color: rgba(255,255,255,0.8); font-size: 0.9em;">of Total</div>
            </div>
        </div>
        <div class="progress-container" style="margin-top: 15px;">
            <div class="progress-bar" style="width: {percentage}%; background: rgba(255,255,255,0.3);"></div>
        </div>
    </div>
    """

def create_animated_metric(label, value, icon="📊"):
    """Create an animated metric card"""
    return f"""
    <div class="metric-card">
        <div style="font-size: 1.5em; margin-bottom: 5px;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """

def determine_service_priority(count, max_count):
    """Determine service priority based on visit count"""
    percentage = (count / max_count) * 100 if max_count > 0 else 0
    if percentage >= 70:
        return "high"
    elif percentage >= 40:
        return "medium"
    else:
        return "low"

def show_loading_animation(animation_type="heart", message="Processing...", subtitle="Please wait while we analyze your data"):
    """Display healthcare-themed loading animations"""
    
    if animation_type == "heart":
        loader_html = f"""
        <div class="healthcare-loader">
            <div class="pulse-heart">❤️</div>
            <div class="loading-text">{message}</div>
            <div class="loading-subtitle">{subtitle}</div>
            <div class="healthcare-progress">
                <div class="healthcare-progress-bar"></div>
            </div>
        </div>
        """
    elif animation_type == "cross":
        loader_html = f"""
        <div class="healthcare-loader">
            <div class="spinning-cross">✚</div>
            <div class="loading-text">{message}</div>
            <div class="loading-subtitle">{subtitle}</div>
            <div class="healthcare-progress">
                <div class="healthcare-progress-bar"></div>
            </div>
        </div>
        """
    elif animation_type == "pills":
        loader_html = f"""
        <div class="healthcare-loader">
            <div class="bouncing-pills">
                <span class="pill">💊</span>
                <span class="pill">💊</span>
                <span class="pill">💊</span>
                <span class="pill">💊</span>
                <span class="pill">💊</span>
            </div>
            <div class="loading-text">{message}</div>
            <div class="loading-subtitle">{subtitle}</div>
            <div class="healthcare-progress">
                <div class="healthcare-progress-bar"></div>
            </div>
        </div>
        """
    elif animation_type == "stethoscope":
        loader_html = f"""
        <div class="healthcare-loader">
            <div class="stethoscope-wave">🩺</div>
            <div class="loading-text">{message}</div>
            <div class="loading-subtitle">{subtitle}</div>
            <div class="healthcare-progress">
                <div class="healthcare-progress-bar"></div>
            </div>
        </div>
        """
    elif animation_type == "dna":
        loader_html = f"""
        <div class="healthcare-loader">
            <div class="dna-helix">🧬</div>
            <div class="loading-text">{message}</div>
            <div class="loading-subtitle">{subtitle}</div>
            <div class="healthcare-progress">
                <div class="healthcare-progress-bar"></div>
            </div>
        </div>
        """
    else:
        # Default heart animation
        loader_html = f"""
        <div class="healthcare-loader">
            <div class="pulse-heart">❤️</div>
            <div class="loading-text">{message}</div>
            <div class="loading-subtitle">{subtitle}</div>
            <div class="healthcare-progress">
                <div class="healthcare-progress-bar"></div>
            </div>
        </div>
        """
    
    placeholder = st.empty()
    placeholder.markdown(loader_html, unsafe_allow_html=True)
    time.sleep(2)  # Show animation for 2 seconds
    placeholder.empty()

def show_analysis_loading():
    """Show specialized loading for data analysis"""
    show_loading_animation(
        animation_type="dna",
        message="Analyzing Healthcare Data",
        subtitle="Processing client visits and service frequencies..."
    )

def show_file_processing_loading():
    """Show specialized loading for file processing"""
    show_loading_animation(
        animation_type="cross",
        message="Processing Files",
        subtitle="Reading and validating your healthcare data..."
    )

def show_calculation_loading():
    """Show specialized loading for calculations"""
    show_loading_animation(
        animation_type="pills",
        message="Calculating Service Fees",
        subtitle="Computing billing amounts and generating reports..."
    )

def show_export_loading():
    """Show specialized loading for exports"""
    show_loading_animation(
        animation_type="stethoscope",
        message="Preparing Export",
        subtitle="Formatting data for download..."
    )

def show_login_page():
    """Display login page"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1 style="color: #6C63FF; font-size: 3rem;">🏥</h1>
        <h2 style="color: #4A5568;">Home Healthcare Analytics</h2>
        <p style="color: #6B7280;">Please log in to continue</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="neumorphic-card">', unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### 🔐 Login")
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_button = st.form_submit_button("Login", type="primary", use_container_width=True)
            
            if submit_button:
                if username and password:
                    db_service = st.session_state.db_service
                    user = db_service.authenticate_user(username, password)
                    
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.current_user = {
                            'username': user.username,
                            'full_name': user.full_name,
                            'role': user.role
                        }
                        st.success(f"Welcome, {user.full_name or user.username}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter both username and password")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Check if user is logged in
if not st.session_state.logged_in:
    show_login_page()
    st.stop()

# Sidebar navigation with logout button
st.sidebar.title("Navigation")

# Display current user info
if st.session_state.current_user:
    st.sidebar.markdown(f"""
    <div style="padding: 1rem; margin-bottom: 1rem; background: #F9F9FB; border-radius: 10px; box-shadow: inset 3px 3px 6px #A3B1C6, inset -3px -3px 6px #FFFFFF;">
        <p style="margin: 0; color: #4A5568; font-size: 0.9rem;">👤 <b>{st.session_state.current_user['full_name'] or st.session_state.current_user['username']}</b></p>
        <p style="margin: 0; color: #6B7280; font-size: 0.8rem;">Role: {st.session_state.current_user['role'].title()}</p>
    </div>
    """, unsafe_allow_html=True)

page = st.sidebar.selectbox(
    "Select a page:",
    ["Data Analysis", "Reports", "Billing", "Client Service Configuration", "Service Type Management", "Service Fee Configuration", "Manual Entry", "Historical Records", "Export Data", "Animation Demo"]
)

# Logout button
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.rerun()

if page == "Data Analysis":
    st.header("📊 Data Analysis")
    
    # File upload section
    st.subheader("1. Upload Data Files")
    
    # Toggle between single and batch processing
    processing_mode = st.radio(
        "Select processing mode:",
        ["Single File", "Batch Processing"],
        horizontal=True
    )
    
    if processing_mode == "Single File":
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['xlsm', 'xlsx', 'csv'],
            help="Upload .xlsm, .xlsx, or .csv files containing healthcare visit data"
        )
        uploaded_files = [uploaded_file] if uploaded_file is not None else []
    else:
        uploaded_files = st.file_uploader(
            "Choose multiple files",
            type=['xlsm', 'xlsx', 'csv'],
            accept_multiple_files=True,
            help="Upload multiple .xlsm, .xlsx, or .csv files for batch processing"
        )
    
    if uploaded_files:
        # Display file information
        if processing_mode == "Single File":
            st.success(f"File uploaded: {uploaded_files[0].name} ({uploaded_files[0].type})")
        else:
            st.success(f"Files uploaded: {len(uploaded_files)} files")
            for file in uploaded_files:
                st.write(f"• {file.name} ({file.type})")
        
        # Process button
        if st.button("Process Data", type="primary"):
            # Progress tracking
            overall_progress = st.progress(0)
            status_text = st.empty()
            
            # Initialize containers for batch results
            all_cleaned_data = []
            all_analysis_results = []
            processing_summary = []
            
            try:
                # Initialize data processor
                processor = DataProcessor()
                
                # Process each file
                for i, uploaded_file in enumerate(uploaded_files):
                    current_file_progress = (i / len(uploaded_files))
                    
                    # Step 1: Import data with loading animation
                    status_text.text(f"Processing file {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
                    show_file_processing_loading()
                    overall_progress.progress(int(current_file_progress * 100))
                    
                    try:
                        if uploaded_file.name.endswith('.csv'):
                            df = pd.read_csv(uploaded_file)
                        else:
                            # Handle both .xlsx and .xlsm files
                            df = pd.read_excel(uploaded_file, engine='openpyxl')
                        
                        # Step 2: Clean data
                        status_text.text(f"Processing file {i+1}/{len(uploaded_files)}: {uploaded_file.name} - Cleaning...")
                        
                        cleaned_df = processor.clean_data(df)
                        
                        if cleaned_df.empty:
                            processing_summary.append({
                                'filename': uploaded_file.name,
                                'status': 'Failed',
                                'rows_processed': 0,
                                'error': 'No verified data found'
                            })
                            continue
                        
                        # Step 3: Analyze data with loading animation
                        status_text.text(f"Analyzing data from {uploaded_file.name}...")
                        show_analysis_loading()
                        
                        analysis_results = processor.analyze_data(cleaned_df)
                        
                        # Add filename to cleaned data for tracking
                        cleaned_df['source_file'] = uploaded_file.name
                        
                        # Store results
                        all_cleaned_data.append(cleaned_df)
                        all_analysis_results.append({
                            'filename': uploaded_file.name,
                            'analysis': analysis_results,
                            'row_count': len(cleaned_df)
                        })
                        
                        # Save individual file analysis
                        st.session_state.data_storage.save_analysis(
                            uploaded_file.name,
                            analysis_results,
                            len(cleaned_df)
                        )
                        
                        processing_summary.append({
                            'filename': uploaded_file.name,
                            'status': 'Success',
                            'rows_processed': len(cleaned_df),
                            'error': None
                        })
                        
                    except Exception as file_error:
                        processing_summary.append({
                            'filename': uploaded_file.name,
                            'status': 'Failed',
                            'rows_processed': 0,
                            'error': str(file_error)
                        })
                        continue
                
                # Step 4: Combine results
                status_text.text("Combining results...")
                overall_progress.progress(90)
                
                if all_cleaned_data:
                    # Combine all cleaned data
                    combined_cleaned_data = pd.concat(all_cleaned_data, ignore_index=True)
                    
                    # Create combined analysis
                    combined_analysis = processor.analyze_data(combined_cleaned_data.drop('source_file', axis=1))
                    
                    # Store combined results in session state
                    st.session_state.current_analysis = combined_analysis
                    st.session_state.cleaned_data = combined_cleaned_data
                    st.session_state.batch_results = all_analysis_results
                    st.session_state.processing_summary = processing_summary
                    
                    overall_progress.progress(100)
                    status_text.text("Batch processing complete!")
                    
                    # Display processing summary
                    st.subheader("Processing Summary")
                    summary_df = pd.DataFrame(processing_summary)
                    st.dataframe(summary_df, use_container_width=True)
                    
                    # Success metrics
                    successful_files = len([s for s in processing_summary if s['status'] == 'Success'])
                    total_rows = sum([s['rows_processed'] for s in processing_summary])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Files Processed", f"{successful_files}/{len(uploaded_files)}")
                    with col2:
                        st.metric("Total Rows", total_rows)
                    with col3:
                        st.metric("Total Clients", len(combined_analysis['client_analysis']))
                    
                    st.success("Batch processing completed successfully!")
                
                else:
                    st.error("No files were processed successfully. Please check your data files.")
                
            except Exception as e:
                st.error(f"Error during batch processing: {str(e)}")
                st.stop()
    
    # Display batch processing results if available
    if 'batch_results' in st.session_state and st.session_state.batch_results:
        st.subheader("2. Batch Processing Results")
        
        # Individual file results
        st.markdown("**Individual File Analysis:**")
        
        for result in st.session_state.batch_results:
            with st.expander(f"📄 {result['filename']} ({result['row_count']} rows)"):
                analysis = result['analysis']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Unique Clients", len(analysis['client_analysis']))
                with col2:
                    st.metric("Unique Employees", len(analysis['employee_analysis']))
                with col3:
                    st.metric("Unique Services", len(analysis['service_analysis']))
                
                # Top 5 for each category
                st.markdown("**Top 5 Clients:**")
                st.dataframe(analysis['client_analysis'].head(5), use_container_width=True)
                
                st.markdown("**Top 5 Services:**")
                st.dataframe(analysis['service_analysis'].head(5), use_container_width=True)
    
    # Display combined analysis results
    if st.session_state.current_analysis:
        st.subheader("3. Combined Analysis Results" if 'batch_results' in st.session_state else "2. Analysis Results")
        
        analysis = st.session_state.current_analysis
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Unique Clients", len(analysis['client_analysis']))
            st.metric("Total Client Visits", analysis['client_analysis']['count'].sum())
        
        with col2:
            st.metric("Total Unique Employees", len(analysis['employee_analysis']))
            st.metric("Total Employee Visits", analysis['employee_analysis']['count'].sum())
        
        with col3:
            st.metric("Total Unique Services", len(analysis['service_analysis']))
            st.metric("Total Service Instances", analysis['service_analysis']['count'].sum())
        
        # Top 10 tables
        st.subheader("3. Top 10 Analysis")
        
        tab1, tab2, tab3 = st.tabs(["👥 Client Names", "🧑‍⚕️ Employee Visits", "🏥 Services Provided"])
        
        with tab1:
            st.markdown("**Top 10 Client Names by Visit Frequency**")
            client_top10 = analysis['client_analysis'].head(10)
            st.dataframe(client_top10, use_container_width=True)
        
        with tab2:
            st.markdown("**Top 10 Employees by Visit Count**")
            employee_top10 = analysis['employee_analysis'].head(10)
            st.dataframe(employee_top10, use_container_width=True)
        
        with tab3:
            st.markdown("**Top 10 Services by Frequency**")
            service_top10 = analysis['service_analysis'].head(10)
            st.dataframe(service_top10, use_container_width=True)

elif page == "Reports":
    st.header("📋 Detailed Reports")
    
    if st.session_state.current_analysis:
        analysis = st.session_state.current_analysis
        
        # Animated Overall Summary Section
        st.subheader("📊 Overall Summary")
        
        show_loading_animation()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_verified_records = analysis['client_analysis']['count'].sum()
            metric_html = create_animated_metric("Total Verified Records", total_verified_records, "📋")
            st.markdown(metric_html, unsafe_allow_html=True)
        
        with col2:
            unique_clients = len(analysis['client_analysis'])
            metric_html = create_animated_metric("Unique Clients", unique_clients, "👥")
            st.markdown(metric_html, unsafe_allow_html=True)
        
        with col3:
            unique_employees = len(analysis['employee_analysis'])
            metric_html = create_animated_metric("Unique Employees", unique_employees, "👨‍⚕️")
            st.markdown(metric_html, unsafe_allow_html=True)
        
        with col4:
            unique_services = len(analysis['service_analysis'])
            metric_html = create_animated_metric("Service Types", unique_services, "🔧")
            st.markdown(metric_html, unsafe_allow_html=True)
        
        # Service Types Report
        st.subheader("🏥 Service Types Analysis")
        
        # Create comprehensive service report
        service_df = analysis['service_analysis'].copy()
        service_df['percentage'] = (service_df['count'] / service_df['count'].sum() * 100).round(2)
        service_df = service_df.sort_values('count', ascending=False)
        
        # Display service types table
        st.markdown("**All Service Types Provided:**")
        
        # Format the display
        display_df = service_df.copy()
        display_df.columns = ['Visit Count', 'Percentage (%)']
        display_df.index.name = 'Service Type'
        
        st.dataframe(display_df, use_container_width=True)
        
        # Client-Service Matrix
        st.subheader("👥 Client Billing Report")
        
        # Get the original cleaned data if available in session state
        if 'cleaned_data' in st.session_state:
            cleaned_data = st.session_state.cleaned_data
            
            # Show batch processing breakdown if available
            if 'batch_results' in st.session_state and st.session_state.batch_results:
                st.markdown("---")
                st.subheader("📊 Batch Processing Breakdown")
                
                # File-by-file analysis
                st.markdown("**Analysis by Source File:**")
                
                batch_summary_data = []
                for result in st.session_state.batch_results:
                    analysis = result['analysis']
                    batch_summary_data.append({
                        'Filename': result['filename'],
                        'Total Rows': result['row_count'],
                        'Unique Clients': len(analysis['client_analysis']),
                        'Unique Employees': len(analysis['employee_analysis']),
                        'Unique Services': len(analysis['service_analysis']),
                        'Total Visits': analysis['client_analysis']['count'].sum()
                    })
                
                batch_summary_df = pd.DataFrame(batch_summary_data)
                st.dataframe(batch_summary_df, use_container_width=True)
                
                # File selector for detailed view
                selected_file = st.selectbox(
                    "Select file for detailed breakdown:",
                    ['Combined Results'] + [result['filename'] for result in st.session_state.batch_results]
                )
                
                if selected_file != 'Combined Results':
                    # Show data for selected file only
                    file_data = cleaned_data[cleaned_data['source_file'] == selected_file].drop('source_file', axis=1)
                    if not file_data.empty:
                        st.markdown(f"**Client Billing Report for {selected_file}:**")
                        
                        # Create billing breakdown for selected file
                        file_billing_data = []
                        for client in sorted(file_data['A'].unique()):
                            client_data = file_data[file_data['A'] == client]
                            service_counts = client_data['C'].value_counts()
                            
                            billing_row = {'Client Name': client}
                            for service, count in service_counts.items():
                                billing_row[service] = count
                            billing_row['Total_Visits'] = service_counts.sum()
                            billing_row['Service_Types_Count'] = len(service_counts)
                            
                            file_billing_data.append(billing_row)
                        
                        file_billing_df = pd.DataFrame(file_billing_data)
                        file_billing_df = file_billing_df.fillna(0).astype({col: 'int' for col in file_billing_df.columns if col != 'Client Name'})
                        st.dataframe(file_billing_df, use_container_width=True)
                    else:
                        st.info("No data found for selected file")
                
                st.markdown("---")
            
            # Client-Centric Billing Breakdown
            st.markdown("**Client Billing Breakdown:**")
            st.markdown("*Each client with all their service types and visit counts for billing purposes*")
            
            # Create client billing report
            client_billing_data = []
            
            for client in sorted(cleaned_data['A'].unique()):
                client_data = cleaned_data[cleaned_data['A'] == client]
                
                # Get service counts for this client
                service_counts = client_data['C'].value_counts()
                
                # Create a row for this client with all their services
                billing_row = {'Client Name': client}
                
                # Add each service type as a separate column
                for service, count in service_counts.items():
                    # Clean service name for column header
                    clean_service = service.replace(' - ', '_').replace(' ', '_').replace('-', '_')
                    billing_row[service] = count
                
                # Calculate totals
                billing_row['Total_Visits'] = service_counts.sum()
                billing_row['Service_Types_Count'] = len(service_counts)
                
                client_billing_data.append(billing_row)
            
            # Convert to DataFrame
            billing_df = pd.DataFrame(client_billing_data)
            billing_df = billing_df.fillna(0).astype({col: 'int' for col in billing_df.columns if col != 'Client Name'})
            
            # Display the billing table
            st.dataframe(billing_df, use_container_width=True)
            
            # Summary statistics
            st.markdown("**Billing Summary:**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Clients", len(billing_df))
            with col2:
                st.metric("Total Visits", billing_df['Total_Visits'].sum())
            with col3:
                try:
                    avg_visits = billing_df['Total_Visits'].mean()
                    st.metric("Avg Visits/Client", round(avg_visits, 1))
                except:
                    st.metric("Avg Visits/Client", 0)
            with col4:
                try:
                    avg_services = billing_df['Service_Types_Count'].mean()
                    st.metric("Avg Services/Client", round(avg_services, 1))
                except:
                    st.metric("Avg Services/Client", 0)
            
            # Service-specific breakdown
            st.markdown("---")
            st.markdown("**Service Type Breakdown by Client:**")
            
            # Create a more detailed view for billing
            detailed_billing = []
            for client in sorted(cleaned_data['A'].unique()):
                client_data = cleaned_data[cleaned_data['A'] == client]
                service_counts = client_data['C'].value_counts()
                
                for service, count in service_counts.items():
                    detailed_billing.append({
                        'Client Name': client,
                        'Service Type': service,
                        'Visit Count': count
                    })
            
            detailed_billing_df = pd.DataFrame(detailed_billing)
            
            # Filter options for detailed view
            st.markdown("**Filter by Service Type:**")
            all_services = ['All Services'] + sorted(detailed_billing_df['Service Type'].unique().tolist())
            selected_service = st.selectbox("Select service type to filter:", all_services)
            
            if selected_service != 'All Services':
                filtered_df = detailed_billing_df[detailed_billing_df['Service Type'] == selected_service]
                st.markdown(f"**Clients receiving {selected_service}:**")
            else:
                filtered_df = detailed_billing_df
                st.markdown("**All client services:**")
            
            st.dataframe(filtered_df, use_container_width=True)
            
            # High-volume clients section
            st.markdown("---")
            st.markdown("**High-Volume Clients:**")
            
            high_volume_clients = billing_df.nlargest(10, 'Total_Visits')[['Client Name', 'Total_Visits', 'Service_Types_Count']]
            st.dataframe(high_volume_clients, use_container_width=True)
            
            # Client Service History Timeline
            st.markdown("---")
            st.subheader("📅 Client Service History Timeline")
            
            # Add date functionality if source_file contains date info or use processing timestamp
            timeline_clients = sorted(cleaned_data['A'].unique())
            selected_timeline_client = st.selectbox(
                "Select client for service timeline:",
                timeline_clients,
                key="timeline_client_selector"
            )
            
            if selected_timeline_client:
                client_timeline_data = cleaned_data[cleaned_data['A'] == selected_timeline_client]
                
                # Create timeline visualization
                if 'batch_results' in st.session_state and st.session_state.batch_results:
                    # Group by source file for timeline
                    timeline_summary = []
                    for file_result in st.session_state.batch_results:
                        filename = file_result['filename']
                        file_client_data = client_timeline_data[client_timeline_data.get('source_file', '') == filename]
                        
                        if not file_client_data.empty:
                            services_in_file = file_client_data['C'].value_counts().to_dict()
                            timeline_summary.append({
                                'File/Period': filename,
                                'Total_Visits': len(file_client_data),
                                'Services': ', '.join([f"{service} ({count})" for service, count in services_in_file.items()]),
                                'Employee(s)': ', '.join(file_client_data['B'].unique())
                            })
                    
                    if timeline_summary:
                        timeline_df = pd.DataFrame(timeline_summary)
                        st.markdown(f"**Service Timeline for {selected_timeline_client}:**")
                        st.dataframe(timeline_df, use_container_width=True)
                        
                        # Service frequency over time
                        st.markdown("**Service Trends:**")
                        service_trend_data = {}
                        for file_result in st.session_state.batch_results:
                            filename = file_result['filename']
                            file_client_data = client_timeline_data[client_timeline_data.get('source_file', '') == filename]
                            
                            for service in file_client_data['C'].unique():
                                if service not in service_trend_data:
                                    service_trend_data[service] = {}
                                service_count = len(file_client_data[file_client_data['C'] == service])
                                service_trend_data[service][filename] = service_count
                        
                        # Create trend chart data
                        if service_trend_data:
                            trend_df = pd.DataFrame(service_trend_data).fillna(0)
                            st.bar_chart(trend_df.T)
                    else:
                        st.info(f"No service history found for {selected_timeline_client}")
                
                else:
                    # Single file timeline - show service breakdown
                    st.markdown(f"**Service Summary for {selected_timeline_client}:**")
                    client_services = client_timeline_data['C'].value_counts().reset_index()
                    client_services.columns = ['Service Type', 'Visit Count']
                    
                    # Add employee information
                    service_employee_details = []
                    for _, row in client_services.iterrows():
                        service = row['Service Type']
                        service_data = client_timeline_data[client_timeline_data['C'] == service]
                        employees = ', '.join(service_data['B'].unique())
                        service_employee_details.append({
                            'Service Type': service,
                            'Visit Count': row['Visit Count'],
                            'Employee(s)': employees
                        })
                    
                    detailed_services_df = pd.DataFrame(service_employee_details)
                    st.dataframe(detailed_services_df, use_container_width=True)
                    
                    # Simple service distribution chart
                    st.bar_chart(client_services.set_index('Service Type')['Visit Count'])
        
        else:
            st.info("Detailed client-service breakdown requires re-processing the data. Please go back to Data Analysis and process a file again.")
        
        # Employee Performance Report
        st.subheader("🧑‍⚕️ Employee Performance & Billing Report")
        
        if 'cleaned_data' in st.session_state:
            # Enhanced employee analysis with billing metrics
            employee_detailed_analysis = []
            
            for employee in cleaned_data['B'].unique():
                employee_data = cleaned_data[cleaned_data['B'] == employee]
                
                # Calculate metrics
                total_visits = len(employee_data)
                unique_clients = employee_data['A'].nunique()
                service_types = employee_data['C'].nunique()
                services_breakdown = employee_data['C'].value_counts().to_dict()
                
                # Calculate billing potential if service rates are available
                billing_potential = 0
                if hasattr(st.session_state, 'fee_calculator'):
                    service_rates = st.session_state.fee_calculator.get_service_rates()
                    for service, count in services_breakdown.items():
                        rate_data = service_rates.get(service, {})
                        if isinstance(rate_data, dict):
                            rate = rate_data.get('rate', 0)
                        else:
                            rate = rate_data if rate_data else 0
                        billing_potential += count * rate
                
                employee_detailed_analysis.append({
                    'Employee': employee,
                    'Total_Visits': total_visits,
                    'Unique_Clients': unique_clients,
                    'Service_Types': service_types,
                    'Billing_Potential': billing_potential,
                    'Avg_Visits_Per_Client': round(total_visits / unique_clients, 2) if unique_clients > 0 else 0,
                    'Services_Breakdown': services_breakdown
                })
            
            # Create employee performance DataFrame
            employee_perf_df = pd.DataFrame(employee_detailed_analysis)
            employee_perf_df = employee_perf_df.sort_values('Total_Visits', ascending=False)
            
            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Employees", len(employee_perf_df))
            with col2:
                st.metric("Avg Visits/Employee", round(employee_perf_df['Total_Visits'].mean(), 1))
            with col3:
                st.metric("Top Performer Visits", employee_perf_df['Total_Visits'].max())
            with col4:
                total_billing = employee_perf_df['Billing_Potential'].sum()
                st.metric("Total Billing Potential", f"${total_billing:,.2f}")
            
            # Employee performance table
            st.markdown("**Employee Performance Summary:**")
            display_columns = ['Employee', 'Total_Visits', 'Unique_Clients', 'Service_Types', 'Billing_Potential', 'Avg_Visits_Per_Client']
            display_df = employee_perf_df[display_columns].copy()
            display_df['Billing_Potential'] = display_df['Billing_Potential'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(display_df, use_container_width=True)
            
            # Detailed employee breakdown
            st.markdown("**Detailed Employee Analysis:**")
            selected_employee = st.selectbox(
                "Select employee for detailed view:",
                ['All Employees'] + sorted(employee_perf_df['Employee'].tolist())
            )
            
            if selected_employee != 'All Employees':
                emp_data = employee_perf_df[employee_perf_df['Employee'] == selected_employee].iloc[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**{selected_employee} - Performance Details:**")
                    st.write(f"Total Visits: {emp_data['Total_Visits']}")
                    st.write(f"Unique Clients Served: {emp_data['Unique_Clients']}")
                    st.write(f"Service Types: {emp_data['Service_Types']}")
                    st.write(f"Billing Potential: ${emp_data['Billing_Potential']:,.2f}")
                
                with col2:
                    st.markdown("**Services Provided:**")
                    services_df = pd.DataFrame(list(emp_data['Services_Breakdown'].items()), 
                                             columns=['Service', 'Count'])
                    st.dataframe(services_df, use_container_width=True)
                
                # Client list for selected employee
                emp_clients = cleaned_data[cleaned_data['B'] == selected_employee]
                client_summary = emp_clients.groupby('A').agg({
                    'C': 'count',
                    'C': lambda x: ', '.join(x.unique())
                }).rename(columns={'C': 'Services_Provided'})
                client_summary['Visit_Count'] = emp_clients['A'].value_counts()
                
                st.markdown("**Clients Served:**")
                st.dataframe(client_summary, use_container_width=True)
        
        else:
            # Fallback to basic employee analysis
            employee_df = analysis['employee_analysis'].copy()
            employee_df['percentage'] = (employee_df['count'] / employee_df['count'].sum() * 100).round(2)
            employee_df = employee_df.sort_values('count', ascending=False)
            
            # Format employee display
            employee_display_df = employee_df.copy()
            employee_display_df.columns = ['Visits Conducted', 'Percentage (%)']
            employee_display_df.index.name = 'Employee Name'
            
            st.dataframe(employee_display_df, use_container_width=True)
        
        # Animated Service Frequency Visualization
        st.subheader("📈 Service Frequency Visualization")
        
        show_loading_animation()
        
        # Calculate metrics for visual hierarchy
        total_visits = service_df['count'].sum()
        max_count = service_df['count'].max()
        
        # Create animated service cards with visual hierarchy
        st.markdown("**Service Performance Overview:**")
        
        # Display top services with animated cards
        for idx, (service, row) in enumerate(service_df.head(6).iterrows()):
            count = row['count']
            percentage = (count / total_visits) * 100
            priority = determine_service_priority(count, max_count)
            
            service_card_html = create_animated_service_card(
                service, count, percentage, priority
            )
            st.markdown(service_card_html, unsafe_allow_html=True)
            
            # Add small delay for staggered animation effect
            if idx < 3:
                time.sleep(0.1)
        
        # Traditional chart view option
        with st.expander("View Traditional Chart"):
            top_services = service_df.head(10)
            if not top_services.empty:
                st.bar_chart(data=top_services['count'])
        
        # Export options for reports
        st.subheader("📤 Export Reports")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Export Service Report", type="secondary"):
                csv_data = service_df.reset_index().to_csv(index=False)
                st.download_button(
                    label="Download Service Report CSV",
                    data=csv_data,
                    file_name="service_types_report.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Export Employee Performance Report", type="secondary"):
                # Create comprehensive employee report
                if 'cleaned_data' in st.session_state:
                    # Use detailed employee analysis
                    employee_detailed_analysis = []
                    
                    for employee in st.session_state.cleaned_data['B'].unique():
                        employee_data = st.session_state.cleaned_data[st.session_state.cleaned_data['B'] == employee]
                        
                        # Calculate metrics
                        total_visits = len(employee_data)
                        unique_clients = employee_data['A'].nunique()
                        service_types = employee_data['C'].nunique()
                        services_breakdown = employee_data['C'].value_counts().to_dict()
                        
                        # Calculate billing potential
                        billing_potential = 0
                        if hasattr(st.session_state, 'fee_calculator'):
                            service_rates = st.session_state.fee_calculator.get_service_rates()
                            for service, count in services_breakdown.items():
                                rate_data = service_rates.get(service, {})
                                if isinstance(rate_data, dict):
                                    rate = rate_data.get('rate', 0)
                                else:
                                    rate = rate_data if rate_data else 0
                                billing_potential += count * rate
                        
                        employee_detailed_analysis.append({
                            'Employee': employee,
                            'Total_Visits': total_visits,
                            'Unique_Clients': unique_clients,
                            'Service_Types': service_types,
                            'Billing_Potential': billing_potential,
                            'Avg_Visits_Per_Client': round(total_visits / unique_clients, 2) if unique_clients > 0 else 0,
                            'Top_Service': max(services_breakdown.items(), key=lambda x: x[1])[0] if services_breakdown else 'None'
                        })
                    
                    employee_report_df = pd.DataFrame(employee_detailed_analysis)
                    csv_data = employee_report_df.to_csv(index=False)
                    
                    st.download_button(
                        label="Download Employee Performance Report CSV",
                        data=csv_data,
                        file_name="employee_performance_billing_report.csv",
                        mime="text/csv"
                    )
                else:
                    # Fallback to basic employee report
                    csv_data = analysis['employee_analysis'].reset_index().to_csv(index=False)
                    st.download_button(
                        label="Download Employee Report CSV",
                        data=csv_data,
                        file_name="employee_basic_report.csv",
                        mime="text/csv"
                    )
        
        with col3:
            if 'cleaned_data' in st.session_state:
                if st.button("Export Client-Service Matrix", type="secondary"):
                    show_export_loading()
                    cleaned_data = st.session_state.cleaned_data
                    client_service_matrix = pd.crosstab(cleaned_data['A'], cleaned_data['C'], margins=True)
                    csv_data = client_service_matrix.to_csv()
                    st.download_button(
                        label="Download Client-Service Matrix CSV",
                        data=csv_data,
                        file_name="client_service_matrix.csv",
                        mime="text/csv"
                    )
        
        # Additional export for specific service types
        st.subheader("📋 Export Specific Service Reports")
        
        if 'cleaned_data' in st.session_state:
            cleaned_data = st.session_state.cleaned_data
            
            # Batch processing exports
            if 'batch_results' in st.session_state and st.session_state.batch_results:
                st.markdown("**Batch Processing Exports:**")
                
                batch_col1, batch_col2, batch_col3 = st.columns(3)
                
                with batch_col1:
                    if st.button("Export Batch Summary", type="secondary"):
                        show_export_loading()
                        batch_summary_data = []
                        for result in st.session_state.batch_results:
                            analysis = result['analysis']
                            batch_summary_data.append({
                                'Filename': result['filename'],
                                'Total_Rows': result['row_count'],
                                'Unique_Clients': len(analysis['client_analysis']),
                                'Unique_Employees': len(analysis['employee_analysis']),
                                'Unique_Services': len(analysis['service_analysis']),
                                'Total_Visits': analysis['client_analysis']['count'].sum()
                            })
                        
                        batch_summary_df = pd.DataFrame(batch_summary_data)
                        csv_data = batch_summary_df.to_csv(index=False)
                        st.download_button(
                            label="Download Batch Summary CSV",
                            data=csv_data,
                            file_name="batch_processing_summary.csv",
                            mime="text/csv"
                        )
                
                with batch_col2:
                    if st.button("Export Individual File Reports", type="secondary"):
                        # Create detailed report for each file
                        all_file_reports = []
                        for result in st.session_state.batch_results:
                            filename = result['filename']
                            analysis = result['analysis']
                            
                            # Add client data
                            for client, row in analysis['client_analysis'].iterrows():
                                all_file_reports.append({
                                    'Source_File': filename,
                                    'Type': 'Client',
                                    'Name': client,
                                    'Visit_Count': row['count']
                                })
                            
                            # Add service data
                            for service, row in analysis['service_analysis'].iterrows():
                                all_file_reports.append({
                                    'Source_File': filename,
                                    'Type': 'Service',
                                    'Name': service,
                                    'Visit_Count': row['count']
                                })
                        
                        all_reports_df = pd.DataFrame(all_file_reports)
                        csv_data = all_reports_df.to_csv(index=False)
                        st.download_button(
                            label="Download Individual File Reports CSV",
                            data=csv_data,
                            file_name="individual_file_reports.csv",
                            mime="text/csv"
                        )
                
                with batch_col3:
                    if st.button("Export Combined Data with Sources", type="secondary"):
                        # Export all data with source file information
                        export_data = []
                        for _, row in cleaned_data.iterrows():
                            export_data.append({
                                'Source_File': row.get('source_file', 'Unknown'),
                                'Client_Name': row['A'],
                                'Employee': row['B'],
                                'Service_Type': row['C'],
                                'Status': row['O']
                            })
                        
                        combined_data_df = pd.DataFrame(export_data)
                        csv_data = combined_data_df.to_csv(index=False)
                        st.download_button(
                            label="Download Combined Data CSV",
                            data=csv_data,
                            file_name="combined_data_with_sources.csv",
                            mime="text/csv"
                        )
                
                st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Export Client Billing Report", type="secondary"):
                    # Create client billing report for export
                    client_billing_data = []
                    
                    for client in sorted(cleaned_data['A'].unique()):
                        client_data = cleaned_data[cleaned_data['A'] == client]
                        service_counts = client_data['C'].value_counts()
                        
                        # Create a row for this client with all their services
                        billing_row = {'Client_Name': client}
                        
                        # Add each service type as a separate column
                        for service, count in service_counts.items():
                            billing_row[service] = count
                        
                        # Calculate totals
                        billing_row['Total_Visits'] = service_counts.sum()
                        billing_row['Service_Types_Count'] = len(service_counts)
                        
                        client_billing_data.append(billing_row)
                    
                    # Convert to DataFrame
                    billing_export_df = pd.DataFrame(client_billing_data)
                    billing_export_df = billing_export_df.fillna(0)
                    
                    # Convert service columns to integers
                    for col in billing_export_df.columns:
                        if col != 'Client_Name':
                            billing_export_df[col] = billing_export_df[col].astype(int)
                    
                    csv_data = billing_export_df.to_csv(index=False)
                    st.download_button(
                        label="Download Client Billing Report CSV",
                        data=csv_data,
                        file_name="client_billing_report.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("Export All Client Services", type="secondary"):
                    # Create complete client-service detail report
                    all_services_data = []
                    for _, row in cleaned_data.iterrows():
                        all_services_data.append({
                            'Client Name': row['A'],
                            'Employee': row['B'],
                            'Service Type': row['C'],
                            'Status': row['O']
                        })
                    
                    all_services_df = pd.DataFrame(all_services_data)
                    csv_data = all_services_df.to_csv(index=False)
                    st.download_button(
                        label="Download Complete Client Services CSV",
                        data=csv_data,
                        file_name="complete_client_services.csv",
                        mime="text/csv"
                    )
    
    else:
        st.info("No analysis data available. Please process a file in the Data Analysis section first.")

elif page == "Billing":
    st.header("💳 Client Billing")
    
    # Check if we have cleaned data and service rates
    db_service = st.session_state.db_service
    manual_entries_for_billing = db_service.get_all_manual_entries()
    
    if ('cleaned_data' in st.session_state and hasattr(st.session_state, 'fee_calculator')) or manual_entries_for_billing:
        # Get service rates from database
        db_service = st.session_state.db_service
        all_service_types = db_service.get_all_service_types()
        # Convert ServiceType objects to dictionaries for easier access
        service_rates = {
            st.name: {
                'rate': st.default_rate,
                'billing_method': st.billing_method,
                'unit': st.unit_type,
                'is_medical': st.is_medical
            } 
            for st in all_service_types
        }
        
        # Combine electronic and manual data for billing
        all_billing_data = []
        
        # Add electronic data if available
        if 'cleaned_data' in st.session_state:
            cleaned_data = st.session_state.cleaned_data
            for _, row in cleaned_data.iterrows():
                all_billing_data.append({
                    'client_name': row['A'],
                    'caregiver_name': row['B'],
                    'service_type': row['C'],
                    'visit_count': 1,  # Each row represents one visit
                    'source': 'Electronic',
                    'date': 'N/A'  # Electronic data doesn't have specific dates
                })
        
        # Add manual entries from database
        for entry in manual_entries_for_billing:
            all_billing_data.append({
                'client_name': entry.client_name,
                'caregiver_name': entry.caregiver_name,
                'service_type': entry.service_type,
                'visit_count': entry.visit_count,
                'source': 'Manual',
                'date': f"{entry.start_date} to {entry.end_date}"
            })
        
        if not service_rates and all_billing_data:
            st.warning("⚠️ No service rates configured. Please set rates in Service Fee Configuration first.")
            if st.button("Go to Service Fee Configuration"):
                st.session_state.page = "Service Fee Configuration"
                st.rerun()
        elif all_billing_data:
            # Create comprehensive billing view combining electronic and manual data
            st.subheader("💰 Comprehensive Client Billing")
            
            # Convert to DataFrame for easier processing
            billing_df = pd.DataFrame(all_billing_data)
            
            # Aggregate data by client and service type
            client_service_summary = billing_df.groupby(['client_name', 'service_type']).agg({
                'visit_count': 'sum',
                'source': lambda x: ', '.join(sorted(set(x))),
                'caregiver_name': lambda x: ', '.join(sorted(set(x)))
            }).reset_index()
            
            # Get unique clients for selection
            all_clients = sorted(billing_df['client_name'].unique())
            
            if all_clients:
                # Add neumorphism styling for the dropdown area
                st.markdown("""
                <style>
                .neumorphic-dropdown {
                    background: linear-gradient(145deg, #f0f0f0, #cacaca);
                    border-radius: 20px;
                    box-shadow: 20px 20px 60px #bebebe, -20px -20px 60px #ffffff;
                    padding: 25px;
                    margin: 20px 0;
                    border: none;
                }
                
                .neumorphic-dropdown .stSelectbox > div > div {
                    background: linear-gradient(145deg, #e6e6e6, #ffffff);
                    border-radius: 12px;
                    box-shadow: inset 8px 8px 16px #d1d1d1, inset -8px -8px 16px #ffffff;
                    border: none !important;
                }
                
                .neumorphic-dropdown .stSelectbox > div > div:hover {
                    background: linear-gradient(145deg, #ffffff, #e6e6e6);
                    box-shadow: inset 4px 4px 8px #d1d1d1, inset -4px -4px 8px #ffffff;
                }
                
                .neumorphic-title {
                    color: #666666;
                    font-weight: 600;
                    margin-bottom: 15px;
                    text-shadow: 2px 2px 4px rgba(255,255,255,0.8), -2px -2px 4px rgba(190,190,190,0.3);
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Create neumorphic container for the dropdown
                st.markdown('<div class="neumorphic-dropdown">', unsafe_allow_html=True)
                st.markdown('<p class="neumorphic-title">Select a client to view their detailed billing breakdown:</p>', unsafe_allow_html=True)
                
                # Client selection dropdown
                selected_client = st.selectbox(
                    "Choose Client:",
                    all_clients,
                    key="comprehensive_billing_client_dropdown"
                )
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                if selected_client:
                    # Get client data from comprehensive billing data
                    client_data = billing_df[billing_df['client_name'] == selected_client]
                    client_services_summary = client_service_summary[client_service_summary['client_name'] == selected_client]
                    
                    # Display client info
                    st.subheader(f"Billing Details for: {selected_client}")
                    
                    # Show client summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Visits", client_data['visit_count'].sum())
                    with col2:
                        st.metric("Service Types", len(client_services_summary))
                    with col3:
                        unique_caregivers = client_data['caregiver_name'].nunique()
                        st.metric("Caregivers", unique_caregivers)
                    with col4:
                        data_sources = client_data['source'].nunique()
                        st.metric("Data Sources", data_sources)
                    
                    # Create detailed billing breakdown
                    st.markdown("**Service Breakdown:**")
                    
                    billing_details = []
                    total_client_cost = 0
                    
                    for _, row in client_services_summary.iterrows():
                        service = row['service_type']
                        visits = row['visit_count']
                        sources = row['source']
                        caregivers = row['caregiver_name']
                        
                        # Get rate from database service type
                        service_type_data = service_rates.get(service, {})
                        rate = service_type_data.get('rate', 0) if service_type_data else 0
                        service_total = visits * rate
                        total_client_cost += service_total
                        
                        billing_details.append({
                            'Service Type': service,
                            'Total Visits': visits,
                            'Rate per Visit': format_currency(rate),
                            'Total Cost': format_currency(service_total),
                            'Data Source': sources,
                            'Caregivers': caregivers
                        })
                    
                    # Display billing table
                    if billing_details:
                        show_calculation_loading()
                        billing_df_display = pd.DataFrame(billing_details)
                        st.dataframe(billing_df_display, use_container_width=True)
                        
                        # Display total cost
                        st.metric("**Total Bill for Client**", format_currency(total_client_cost))
                        
                        # Show detailed entries for this client
                        st.markdown("**Individual Entries:**")
                        client_entries_display = client_data[['service_type', 'visit_count', 'caregiver_name', 'source', 'date']].copy()
                        client_entries_display.columns = ['Service', 'Visits', 'Caregiver', 'Source', 'Date']
                        st.dataframe(client_entries_display, use_container_width=True)
                        
                        # Export individual client billing
                        st.markdown("---")
                        if st.button(f"Export {selected_client} Billing Report", type="secondary"):
                            show_export_loading()
                            
                            # Prepare comprehensive export data
                            export_data = []
                            for _, entry in client_data.iterrows():
                                # Get rate from database service type
                                service_type_data = service_rates.get(entry['service_type'], {})
                                rate = service_type_data.get('rate', 0) if service_type_data else 0
                                total_cost = entry['visit_count'] * rate
                                
                                export_data.append({
                                    'Client Name': entry['client_name'],
                                    'Service Type': entry['service_type'],
                                    'Caregiver': entry['caregiver_name'],
                                    'Visit Count': entry['visit_count'],
                                    'Rate per Visit': rate,
                                    'Total Cost': total_cost,
                                    'Data Source': entry['source'],
                                    'Service Period': entry['date']
                                })
                            
                            export_df = pd.DataFrame(export_data)
                            csv_data = export_df.to_csv(index=False)
                            
                            st.download_button(
                                label=f"Download {selected_client} Billing Report CSV",
                                data=csv_data,
                                file_name=f"{selected_client}_billing_report_{datetime.now().strftime('%Y%m%d')}.csv",
                                mime="text/csv"
                            )
                
                # All clients overview
                st.markdown("---")
                st.subheader("📊 All Clients Overview")
                
                # Summary by client
                client_totals = []
                for client in all_clients:
                    client_entries = billing_df[billing_df['client_name'] == client]
                    client_summary = client_service_summary[client_service_summary['client_name'] == client]
                    
                    total_visits = client_entries['visit_count'].sum()
                    total_cost = 0
                    
                    for _, row in client_summary.iterrows():
                        service = row['service_type']
                        visits = row['visit_count']
                        # Get rate from database service type
                        service_type_data = service_rates.get(service, {})
                        rate = service_type_data.get('rate', 0) if service_type_data else 0
                        total_cost += visits * rate
                    
                    client_totals.append({
                        'Client Name': client,
                        'Total Visits': total_visits,
                        'Service Types': len(client_summary),
                        'Total Cost': format_currency(total_cost),
                        'Has Manual Entries': 'Yes' if 'Manual' in client_entries['source'].values else 'No'
                    })
                
                if client_totals:
                    overview_df = pd.DataFrame(client_totals)
                    st.dataframe(overview_df, use_container_width=True)
                    
                    # Export all clients billing with detailed service breakdown
                    if st.button("Export Complete Billing Report", type="secondary"):
                        show_export_loading()
                        
                        # Create detailed export with service-by-service breakdown
                        detailed_export = []
                        
                        for client in all_clients:
                            client_entries = billing_df[billing_df['client_name'] == client]
                            client_summary = client_service_summary[client_service_summary['client_name'] == client]
                            
                            # Add header row for client
                            detailed_export.append({
                                'Client Name': client,
                                'Service Type': '--- CLIENT SUMMARY ---',
                                'Visits': '',
                                'Rate per Visit': '',
                                'Service Total': '',
                                'Data Source': ''
                            })
                            
                            # Add each service type for this client
                            client_total = 0
                            for _, row in client_summary.iterrows():
                                service = row['service_type']
                                visits = row['visit_count']
                                sources = row['source']
                                
                                # Get rate from database service type
                                service_type_data = service_rates.get(service, {})
                                rate = service_type_data.get('rate', 0) if service_type_data else 0
                                
                                service_total = visits * rate
                                client_total += service_total
                                
                                detailed_export.append({
                                    'Client Name': '',
                                    'Service Type': service,
                                    'Visits': visits,
                                    'Rate per Visit': f"${rate:.2f}",
                                    'Service Total': f"${service_total:.2f}",
                                    'Data Source': sources
                                })
                            
                            # Add client subtotal
                            detailed_export.append({
                                'Client Name': '',
                                'Service Type': f"SUBTOTAL - {client}",
                                'Visits': client_entries['visit_count'].sum(),
                                'Rate per Visit': '',
                                'Service Total': f"${client_total:.2f}",
                                'Data Source': ''
                            })
                            
                            # Add blank row for separation
                            detailed_export.append({
                                'Client Name': '',
                                'Service Type': '',
                                'Visits': '',
                                'Rate per Visit': '',
                                'Service Total': '',
                                'Data Source': ''
                            })
                        
                        # Add grand total
                        grand_total = sum([
                            float(row['Service Total'].replace('$', '').replace(',', ''))
                            for row in detailed_export
                            if row['Service Type'].startswith('SUBTOTAL')
                        ])
                        
                        detailed_export.append({
                            'Client Name': '=== GRAND TOTAL ===',
                            'Service Type': 'All Clients',
                            'Visits': billing_df['visit_count'].sum(),
                            'Rate per Visit': '',
                            'Service Total': f"${grand_total:.2f}",
                            'Data Source': ''
                        })
                        
                        export_df = pd.DataFrame(detailed_export)
                        csv_data = export_df.to_csv(index=False)
                        
                        st.download_button(
                            label="Download Detailed Billing Report CSV",
                            data=csv_data,
                            file_name=f"detailed_billing_report_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
        
        else:
            st.info("No billing data available. Please process files or add manual entries first.")
    
    else:
        st.info("No data available. Please process files in the Data Analysis section or add manual entries above.")

elif page == "Client Service Configuration":
    st.header("👥 Client Service Configuration")
    st.markdown("Configure client-specific service hours for accurate billing calculations")
    
    # Tab layout for different management functions
    tab1, tab2, tab3, tab4 = st.tabs(["Add Client", "Manage Clients", "Period Overrides", "History"])
    
    with tab1:
        st.subheader("➕ Add New Client")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_client_name = st.text_input(
                "Client Name",
                placeholder="Enter client's full name",
                key="new_client_name"
            )
            
        with col2:
            # Get service types from database
            db_service = st.session_state.db_service
            available_services = db_service.get_service_type_names()
            
            service_type = st.selectbox(
                "Service Type",
                available_services if available_services else ["Home Health - Basic", "Personal Care", "Homemaker"],
                key="new_client_service_type",
                help="Select the type of service for this client. Manage service types in 'Service Type Management'."
            )
        
        # Service configuration based on type
        col3, col4 = st.columns(2)
        
        # Get service type details from database
        service_info = db_service.get_service_rate(service_type)
        default_rate = service_info.get('rate', 0.0)
        billing_method = service_info.get('billing_method', 'hourly')
        unit_type = service_info.get('unit', 'hour')
        is_medical = service_info.get('is_medical', False)
        
        with col3:
            if billing_method == "hourly":
                default_hours = st.number_input(
                    "Default Hours per Period",
                    min_value=0.0,
                    value=20.0,
                    step=0.5,
                    help="Standard hours for this client (e.g., 20 hours per month)",
                    key="new_client_hours"
                )
                rate = st.number_input(
                    "Hourly Rate ($)",
                    min_value=0.0,
                    value=default_rate,
                    step=0.01,
                    format="%.2f",
                    key="new_client_rate",
                    help=f"Default rate: ${default_rate:.2f}/hour"
                )
            else:
                default_hours = st.number_input(
                    "Default 15-minute Units per Period",
                    min_value=0.0,
                    value=40.0,
                    step=1.0,
                    help="Standard 15-minute units for this client",
                    key="new_client_units"
                )
                rate = st.number_input(
                    "Rate per 15-minute Unit ($)",
                    min_value=0.0,
                    value=default_rate,
                    step=0.01,
                    format="%.2f",
                    key="new_client_unit_rate",
                    help=f"Default rate: ${default_rate:.2f}/unit"
                )
        
        with col4:
            service_type_badge = "🏥 Medical" if is_medical else "🤝 Non-Medical"
            st.info(f"""
            **Service Configuration:**
            - Type: {service_type_badge}
            - Billing Method: {billing_method.title()}
            - Unit Type: {unit_type}
            - Estimated Monthly Cost: {format_currency(default_hours * rate)}
            """)
        
        if st.button("Add Client Configuration", type="primary"):
            if new_client_name:
                try:
                    # Save to database
                    db_service.create_client_config(
                        client_name=new_client_name,
                        service_type_name=service_type,
                        default_hours=default_hours,
                        custom_rate=rate,
                        billing_method=billing_method,
                        unit_type=unit_type
                    )
                    
                    # Also save to legacy JSON for backward compatibility
                    service_config = {
                        service_type: {
                            "default_hours": default_hours,
                            "billing_method": billing_method,
                            "rate": rate,
                            "unit": unit_type
                        }
                    }
                    st.session_state.client_service_manager.add_client(
                        new_client_name, service_config
                    )
                    
                    st.success(f"✅ Client '{new_client_name}' added successfully with {service_type} configuration!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding client: {str(e)}")
            else:
                st.warning("Please enter a client name.")
    
    with tab2:
        st.subheader("📋 Manage Existing Clients")
        
        # Get all clients from database
        db_service = st.session_state.db_service
        db_clients = db_service.get_all_clients()
        all_clients = [client.name for client in db_clients]
        
        if all_clients:
            # Client selection
            selected_client = st.selectbox(
                "Select Client to Manage:",
                all_clients,
                key="manage_client_select"
            )
            
            if selected_client:
                # Get client services
                client_services = st.session_state.client_service_manager.get_client_services(selected_client)
                
                st.markdown(f"**Managing: {selected_client}**")
                
                for service_type in client_services:
                    with st.expander(f"{service_type} Configuration", expanded=True):
                        config = st.session_state.client_service_manager.get_client_service_config(
                            selected_client, service_type
                        )
                        
                        if config:
                            col1, col2, col3 = st.columns([2, 1, 1])
                            
                            with col1:
                                current_hours = config["default_hours"]
                                billing_method = config["billing_method"]
                                current_rate = config["rate"]
                                
                                unit_label = "Hours" if billing_method == "hourly" else "15-min Units"
                                
                                new_hours = st.number_input(
                                    f"Default {unit_label}",
                                    min_value=0.0,
                                    value=current_hours,
                                    step=0.5 if billing_method == "hourly" else 1.0,
                                    key=f"update_hours_{selected_client}_{service_type}"
                                )
                                
                                new_rate = st.number_input(
                                    f"Rate per {unit_label.lower()}",
                                    min_value=0.0,
                                    value=current_rate,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"update_rate_{selected_client}_{service_type}"
                                )
                            
                            with col2:
                                st.metric("Current Cost", format_currency(current_hours * current_rate))
                                st.metric("New Cost", format_currency(new_hours * new_rate))
                            
                            with col3:
                                reason = st.text_input(
                                    "Reason for Change",
                                    placeholder="Care plan update, rate change, etc.",
                                    key=f"update_reason_{selected_client}_{service_type}"
                                )
                                
                                if st.button(f"Update {service_type}", 
                                           key=f"update_btn_{selected_client}_{service_type}"):
                                    success = st.session_state.client_service_manager.update_client_service_hours(
                                        selected_client, service_type, new_hours, reason
                                    )
                                    if success:
                                        st.success(f"Updated {service_type} for {selected_client}")
                                        st.rerun()
                
                # Delete client option
                st.markdown("---")
                st.markdown("**Danger Zone**")
                if st.button(f"Delete Client: {selected_client}", type="secondary"):
                    if st.session_state.client_service_manager.delete_client(selected_client):
                        st.success(f"Client '{selected_client}' deleted successfully")
                        st.rerun()
        else:
            st.info("No clients configured yet. Add clients in the 'Add Client' tab.")
    
    with tab3:
        st.subheader("🗓️ Period Overrides")
        st.markdown("Apply temporary adjustments for specific billing periods (hospital stays, vacations, etc.)")
        
        # Get all clients from database
        db_service = st.session_state.db_service
        db_clients = db_service.get_all_clients()
        all_clients = [client.name for client in db_clients]
        
        if all_clients:
            col1, col2 = st.columns(2)
            
            with col1:
                override_client = st.selectbox(
                    "Select Client:",
                    all_clients,
                    key="override_client_select"
                )
                
                if override_client:
                    client_services = st.session_state.client_service_manager.get_client_services(override_client)
                    override_service = st.selectbox(
                        "Select Service:",
                        client_services,
                        key="override_service_select"
                    )
                    
                    if override_service:
                        config = st.session_state.client_service_manager.get_client_service_config(
                            override_client, override_service
                        )
                        default_hours = config["default_hours"]
                        
                        override_hours = st.number_input(
                            f"Override Amount (Default: {default_hours})",
                            min_value=0.0,
                            value=default_hours,
                            step=0.5,
                            key="override_hours_input"
                        )
            
            with col2:
                st.markdown("**Period Dates:**")
                period_start = st.date_input("Start Date", key="override_start_date")
                period_end = st.date_input("End Date", key="override_end_date")
                
                reason_options = [
                    "Hospital stay",
                    "Vacation/Travel",
                    "Temporary care reduction",
                    "Increased care needs",
                    "Other"
                ]
                
                override_reason = st.selectbox(
                    "Reason for Override:",
                    reason_options,
                    key="override_reason_select"
                )
                
                if override_reason == "Other":
                    custom_reason = st.text_input(
                        "Specify reason:",
                        key="override_custom_reason"
                    )
                    override_reason = custom_reason if custom_reason else override_reason
            
            if st.button("Apply Period Override", type="primary"):
                if override_client and override_service and period_start <= period_end:
                    success = st.session_state.client_service_manager.apply_period_override(
                        override_client, override_service, override_hours,
                        period_start, period_end, override_reason
                    )
                    if success:
                        st.success(f"Period override applied: {override_client} - {override_service}")
                        st.success(f"Period: {period_start} to {period_end}")
                        st.success(f"Hours: {default_hours} → {override_hours} ({override_reason})")
                    else:
                        st.error("Failed to apply override. Please check the configuration.")
                else:
                    st.warning("Please ensure all fields are filled and end date is after start date.")
        else:
            st.info("No clients configured yet. Add clients first.")
    
    with tab4:
        st.subheader("📊 Change History")
        
        # Recent changes
        st.markdown("**Recent Changes:**")
        recent_history = st.session_state.client_service_manager.get_recent_history(20)
        
        if recent_history:
            history_data = []
            for entry in recent_history:
                history_data.append({
                    "Date": entry["timestamp"][:10],
                    "Time": entry["timestamp"][11:19],
                    "Client": entry["client_name"],
                    "Action": entry["action"].replace("_", " ").title(),
                    "Service": ", ".join(entry["service_types"]),
                    "Details": entry["details"],
                    "Reason": entry.get("reason", "")
                })
            
            history_df = pd.DataFrame(history_data)
            st.dataframe(history_df, use_container_width=True)
            
            # Export history
            if st.button("Export History"):
                history_csv = history_df.to_csv(index=False)
                st.download_button(
                    label="Download History CSV",
                    data=history_csv,
                    file_name=f"client_service_history_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No change history available yet.")
        
        # Client-specific history
        all_clients = st.session_state.client_service_manager.get_all_clients()
        if all_clients:
            st.markdown("---")
            st.markdown("**Client-Specific History:**")
            
            history_client = st.selectbox(
                "Select Client for History:",
                ["All Clients"] + all_clients,
                key="history_client_select"
            )
            
            if history_client != "All Clients":
                client_history = st.session_state.client_service_manager.get_client_history(history_client)
                if client_history:
                    client_history_data = []
                    for entry in client_history:
                        client_history_data.append({
                            "Date": entry["timestamp"][:10],
                            "Action": entry["action"].replace("_", " ").title(),
                            "Service": ", ".join(entry["service_types"]),
                            "Old Value": entry.get("old_value", ""),
                            "New Value": entry.get("new_value", ""),
                            "Reason": entry.get("reason", ""),
                            "Details": entry["details"]
                        })
                    
                    client_history_df = pd.DataFrame(client_history_data)
                    st.dataframe(client_history_df, use_container_width=True)
                else:
                    st.info(f"No history found for {history_client}")
    
    # Summary section
    st.markdown("---")
    st.subheader("📈 Client Summary")
    
    # Get clients summary
    clients_summary = st.session_state.client_service_manager.get_clients_summary()
    
    if not clients_summary.empty:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Clients", len(clients_summary['Client'].unique()))
        
        with col2:
            total_hours = clients_summary['Default Hours'].sum()
            st.metric("Total Default Hours", f"{total_hours:.1f}")
        
        with col3:
            hourly_clients = len(clients_summary[clients_summary['Billing Method'] == 'hourly'])
            st.metric("Hourly Billing Clients", hourly_clients)
        
        with col4:
            unit_clients = len(clients_summary[clients_summary['Billing Method'] == 'unit'])
            st.metric("Unit Billing Clients", unit_clients)
        
        # Detailed summary table
        st.markdown("**All Client Configurations:**")
        st.dataframe(clients_summary, use_container_width=True)
        
        # Export client configuration
        if st.button("Export Client Configuration"):
            config_csv = clients_summary.to_csv(index=False)
            st.download_button(
                label="Download Client Configuration CSV",
                data=config_csv,
                file_name=f"client_service_configuration_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No client configurations found. Start by adding clients in the 'Add Client' tab.")

elif page == "Service Type Management":
    st.header("🏥 Service Type Management")
    st.markdown("Manage service types including medical and non-medical services")
    
    db_service = st.session_state.db_service
    
    # Tabs for different operations
    tab1, tab2, tab3 = st.tabs(["📋 View All Service Types", "➕ Add New Service Type", "✏️ Edit Service Types"])
    
    with tab1:
        st.subheader("All Service Types")
        
        # Get all service types from database
        service_types = db_service.get_all_service_types(active_only=True)
        
        if service_types:
            # Separate medical and non-medical
            medical_services = [st for st in service_types if st.is_medical]
            non_medical_services = [st for st in service_types if not st.is_medical]
            
            # Display Medical Services
            st.markdown("### 🏥 Medical Services")
            if medical_services:
                medical_data = []
                for service in medical_services:
                    medical_data.append({
                        'Service Name': service.name,
                        'Rate': f"${service.default_rate:.2f}",
                        'Billing Method': service.billing_method.title(),
                        'Unit Type': service.unit_type,
                        'Description': service.description or 'N/A'
                    })
                medical_df = pd.DataFrame(medical_data)
                st.dataframe(medical_df, use_container_width=True)
            else:
                st.info("No medical services configured yet.")
            
            # Display Non-Medical Services
            st.markdown("### 🤝 Non-Medical Services")
            if non_medical_services:
                non_medical_data = []
                for service in non_medical_services:
                    non_medical_data.append({
                        'Service Name': service.name,
                        'Rate': f"${service.default_rate:.2f}",
                        'Billing Method': service.billing_method.title(),
                        'Unit Type': service.unit_type,
                        'Description': service.description or 'N/A'
                    })
                non_medical_df = pd.DataFrame(non_medical_data)
                st.dataframe(non_medical_df, use_container_width=True)
            else:
                st.info("No non-medical services configured yet.")
        else:
            st.warning("No service types found. Add some service types to get started.")
    
    with tab2:
        st.subheader("Add New Service Type")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_service_name = st.text_input(
                "Service Name",
                placeholder="e.g., Physical Therapy, Speech Therapy, Nursing",
                key="new_service_name"
            )
            
            is_medical = st.checkbox(
                "Medical Service",
                value=True,
                help="Check if this is a medical service (e.g., nursing, PT, OT). Uncheck for non-medical services.",
                key="new_is_medical"
            )
            
            billing_method = st.selectbox(
                "Billing Method",
                ["hourly", "unit"],
                format_func=lambda x: "Hourly" if x == "hourly" else "15-minute Units",
                key="new_billing_method"
            )
        
        with col2:
            default_rate = st.number_input(
                "Default Rate ($)",
                min_value=0.0,
                value=41.45 if billing_method == "hourly" else 12.50,
                step=0.01,
                format="%.2f",
                help="Default rate for this service type",
                key="new_default_rate"
            )
            
            unit_type = st.selectbox(
                "Unit Type",
                ["hour", "15min"],
                index=0 if billing_method == "hourly" else 1,
                disabled=True,
                key="new_unit_type"
            )
            
        description = st.text_area(
            "Description (Optional)",
            placeholder="Brief description of this service type...",
            key="new_description"
        )
        
        if st.button("Add Service Type", type="primary"):
            if new_service_name:
                try:
                    # Check if service already exists
                    existing = db_service.get_service_type_by_name(new_service_name)
                    if existing:
                        st.error(f"Service type '{new_service_name}' already exists!")
                    else:
                        # Create new service type
                        db_service.create_service_type(
                            name=new_service_name,
                            is_medical=is_medical,
                            default_rate=default_rate,
                            billing_method=billing_method,
                            unit_type="hour" if billing_method == "hourly" else "15min",
                            description=description if description else None
                        )
                        st.success(f"✅ Service type '{new_service_name}' added successfully!")
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f"Error adding service type: {str(e)}")
            else:
                st.warning("Please enter a service name.")
    
    with tab3:
        st.subheader("Edit Service Types")
        
        # Get all service types
        all_services = db_service.get_all_service_types(active_only=True)
        
        if all_services:
            service_names = [s.name for s in all_services]
            selected_service_name = st.selectbox(
                "Select Service Type to Edit",
                service_names,
                key="edit_service_select"
            )
            
            if selected_service_name:
                service = db_service.get_service_type_by_name(selected_service_name)
                
                if service:
                    st.markdown(f"### Editing: {service.name}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edit_rate = st.number_input(
                            "Default Rate ($)",
                            min_value=0.0,
                            value=float(service.default_rate),
                            step=0.01,
                            format="%.2f",
                            key="edit_rate"
                        )
                        
                        edit_is_medical = st.checkbox(
                            "Medical Service",
                            value=service.is_medical,
                            key="edit_is_medical"
                        )
                    
                    with col2:
                        edit_billing_method = st.selectbox(
                            "Billing Method",
                            ["hourly", "unit"],
                            index=0 if service.billing_method == "hourly" else 1,
                            format_func=lambda x: "Hourly" if x == "hourly" else "15-minute Units",
                            key="edit_billing_method"
                        )
                        
                        edit_is_active = st.checkbox(
                            "Active",
                            value=service.is_active,
                            help="Uncheck to deactivate this service type",
                            key="edit_is_active"
                        )
                    
                    edit_description = st.text_area(
                        "Description",
                        value=service.description or "",
                        key="edit_description"
                    )
                    
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button("Save Changes", type="primary"):
                            try:
                                db_service.update_service_type(
                                    service_id=service.id,
                                    default_rate=edit_rate,
                                    is_medical=edit_is_medical,
                                    billing_method=edit_billing_method,
                                    unit_type="hour" if edit_billing_method == "hourly" else "15min",
                                    description=edit_description if edit_description else None,
                                    is_active=edit_is_active
                                )
                                st.success(f"✅ Service type '{service.name}' updated successfully!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error updating service type: {str(e)}")
                    
                    with col_btn2:
                        if st.button("Delete Service Type", type="secondary"):
                            try:
                                db_service.delete_service_type(service.id, soft_delete=True)
                                st.success(f"✅ Service type '{service.name}' deleted successfully!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting service type: {str(e)}")
        else:
            st.info("No service types available to edit.")

elif page == "Service Fee Configuration":
    st.header("💰 Service Fee Configuration")
    
    st.markdown("Configure service rates for automatic fee calculation")
    
    # Get current service rates
    current_rates = st.session_state.fee_calculator.get_service_rates()
    
    # Service rate configuration
    st.subheader("Service Rates")
    
    if st.session_state.current_analysis:
        # Get unique services from current analysis
        services = st.session_state.current_analysis['service_analysis'].index.tolist()
        
        # Create input fields for each service
        updated_rates = {}
        
        for service in services:
            rate_data = current_rates.get(service, 0.0)
            # Extract actual rate value from structured data
            if isinstance(rate_data, dict):
                current_rate = rate_data.get('rate', 0.0)
            else:
                current_rate = rate_data if rate_data else 0.0
            
            new_rate = st.number_input(
                f"Rate for '{service}'",
                min_value=0.0,
                value=current_rate,
                step=0.01,
                format="%.2f",
                key=f"rate_{service}"
            )
            updated_rates[service] = new_rate
        
        # Save rates button
        if st.button("Save Service Rates", type="primary"):
            show_calculation_loading()
            st.session_state.fee_calculator.update_service_rates(updated_rates)
            st.success("Service rates updated successfully!")
            st.rerun()
    
    else:
        st.info("Please analyze data first to configure service rates.")
    
    # Fee calculation section
    if st.session_state.current_analysis and current_rates:
        st.subheader("Fee Calculation")
        
        # Check if we have cleaned_data for client-based breakdown
        if 'cleaned_data' in st.session_state:
            st.markdown("**Fee Breakdown by Client**")
            
            cleaned_data = st.session_state.cleaned_data
            
            # Create client-based billing breakdown
            client_billing_data = []
            
            for client in sorted(cleaned_data['A'].unique()):
                client_data = cleaned_data[cleaned_data['A'] == client]
                client_services = client_data['C'].value_counts().to_dict()
                
                # Calculate client total
                client_total = 0
                client_service_details = []
                
                for service, count in client_services.items():
                    rate = current_rates.get(service, 0)
                    service_total = count * rate
                    client_total += service_total
                    
                    client_service_details.append({
                        'Service': service,
                        'Count': count,
                        'Rate': rate,
                        'Total': service_total
                    })
                
                client_billing_data.append({
                    'Client_Name': client,
                    'Services': client_service_details,
                    'Total_Visits': sum(client_services.values()),
                    'Total_Charge': client_total
                })
            
            # Display detailed billing breakdown (like your example)
            if client_billing_data:
                detailed_billing = []
                
                for client_info in client_billing_data:
                    client_name = client_info['Client_Name']
                    
                    # Add each service as a separate row with calculation
                    for service_detail in client_info['Services']:
                        service_name = service_detail['Service']
                        count = service_detail['Count']
                        rate = service_detail['Rate']
                        total = service_detail['Total']
                        
                        detailed_billing.append({
                            'Client Name': client_name,
                            'Service Type': service_name,
                            'Visit Count': count,
                            'Rate': f"${rate:.2f}",
                            'Calculation': f"{count} × ${rate:.2f} = ${total:.2f}",
                            'Total Charge': f"${total:.2f}"
                        })
                
                # Create DataFrame and display
                billing_df = pd.DataFrame(detailed_billing)
                st.dataframe(billing_df, use_container_width=True)
                
                # Grand total
                grand_total = sum([client['Total_Charge'] for client in client_billing_data])
                st.metric("Grand Total", f"${grand_total:.2f}")
                
                # Summary by client option
                with st.expander("View Client Summary"):
                    client_summary = []
                    for client_info in client_billing_data:
                        # Show client with their service breakdown text
                        service_breakdown = []
                        for service_detail in client_info['Services']:
                            service_breakdown.append(
                                f"{service_detail['Count']} {service_detail['Service']} "
                                f"({service_detail['Count']} × ${service_detail['Rate']:.2f} = ${service_detail['Total']:.2f})"
                            )
                        
                        client_summary.append({
                            'Client Name': client_info['Client_Name'],
                            'Services Received': '; '.join(service_breakdown),
                            'Total Charge': f"${client_info['Total_Charge']:.2f}"
                        })
                    
                    summary_df = pd.DataFrame(client_summary)
                    st.dataframe(summary_df, use_container_width=True)
                
                # Export client billing report
                if st.button("📤 Export Client Billing Report", type="secondary"):
                    # Use the detailed billing data for export
                    csv_data = billing_df.to_csv(index=False)
                    
                    st.download_button(
                        label="Download Detailed Client Billing Report CSV",
                        data=csv_data,
                        file_name="detailed_client_billing_report.csv",
                        mime="text/csv"
                    )
            else:
                st.info("No billing data available.")
                
        else:
            # Fallback to service-based calculation
            fee_analysis = st.session_state.fee_calculator.calculate_fees(
                st.session_state.current_analysis['service_analysis']
            )
            
            if not fee_analysis.empty:
                # Display fee breakdown
                st.markdown("**Fee Breakdown by Service**")
                st.dataframe(fee_analysis, use_container_width=True)
                
                # Total fees
                total_fees = fee_analysis['total_fee'].sum()
                st.metric("Total Calculated Fees", format_currency(total_fees))
                
                st.info("For client-based billing breakdown, please re-process your data file.")
            else:
                st.info("No fees calculated. Please set service rates above.")

elif page == "Manual Entry":
    st.header("📝 Manual Entry for Exempt Clients")
    st.markdown("Add services for clients and caregivers exempt from electronic verification (paper-based tracking)")
    
    with st.expander("➕ Add Manual Entry", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            manual_client_name = st.text_input(
                "Client Name",
                placeholder="Enter client's full name",
                key="manual_client"
            )
            manual_service_type = st.text_input(
                "Service Type",
                placeholder="e.g., Home Care, Physical Therapy",
                key="manual_service"
            )
        
        with col2:
            manual_caregiver_name = st.text_input(
                "Caregiver/Nurse Name",
                placeholder="Enter caregiver's full name",
                key="manual_caregiver"
            )
            manual_visit_count = st.number_input(
                "Number of Visits",
                min_value=1,
                value=1,
                step=1,
                help="How many times this service was provided",
                key="manual_visits"
            )
        
        # Date range for the services
        st.markdown("**Service Period:**")
        date_col1, date_col2 = st.columns(2)
        with date_col1:
            start_date = st.date_input("Start Date", key="manual_start_date")
        with date_col2:
            end_date = st.date_input("End Date", key="manual_end_date")
        
        # Notes section
        manual_notes = st.text_area(
            "Notes (Optional)",
            placeholder="Additional notes about this service entry",
            key="manual_notes"
        )
        
        # Add entry button
        if st.button("Add Manual Entry", type="primary"):
            if manual_client_name and manual_caregiver_name and manual_service_type:
                # Save to database
                db_service = st.session_state.db_service
                db_service.create_manual_entry(
                    client_name=manual_client_name.strip(),
                    caregiver_name=manual_caregiver_name.strip(),
                    service_type=manual_service_type.strip(),
                    visit_count=manual_visit_count,
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d'),
                    notes=manual_notes.strip() if manual_notes else ''
                )
                st.success(f"✅ Manual entry saved to database: {manual_visit_count} visits for {manual_client_name} by {manual_caregiver_name}")
                st.rerun()
            else:
                st.error("Please fill in Client Name, Caregiver Name, and Service Type")
    
    # Display existing manual entries from database
    db_service = st.session_state.db_service
    manual_entries_from_db = db_service.get_all_manual_entries()
    
    if manual_entries_from_db:
        st.subheader("📋 Current Manual Entries")
        
        # Convert database entries to DataFrame
        manual_entries_data = []
        for entry in manual_entries_from_db:
            manual_entries_data.append({
                'id': entry.id,
                'client_name': entry.client_name,
                'caregiver_name': entry.caregiver_name,
                'service_type': entry.service_type,
                'visit_count': entry.visit_count,
                'start_date': entry.start_date,
                'end_date': entry.end_date,
                'notes': entry.notes or '',
                'created_at': entry.created_at.strftime('%Y-%m-%d %H:%M')
            })
        manual_df = pd.DataFrame(manual_entries_data)
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Manual Entries", len(manual_df))
        with col2:
            st.metric("Unique Clients", manual_df['client_name'].nunique())
        with col3:
            st.metric("Unique Caregivers", manual_df['caregiver_name'].nunique())
        with col4:
            st.metric("Total Manual Visits", manual_df['visit_count'].sum())
        
        # Display entries table
        display_df = manual_df[['client_name', 'caregiver_name', 'service_type', 'visit_count', 'start_date', 'end_date']].copy()
        display_df.columns = ['Client Name', 'Caregiver', 'Service Type', 'Visits', 'Start Date', 'End Date']
        st.dataframe(display_df, use_container_width=True)
        
        # Management buttons
        manage_col1, manage_col2, manage_col3 = st.columns(3)
        
        with manage_col1:
            if st.button("Export Manual Entries", type="secondary"):
                show_export_loading()
                csv_data = manual_df.to_csv(index=False)
                st.download_button(
                    label="Download Manual Entries CSV",
                    data=csv_data,
                    file_name=f"manual_entries_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with manage_col2:
            if st.button("Clear All Manual Entries", type="secondary"):
                if st.button("Confirm Clear All", type="secondary"):
                    db_service.clear_all_manual_entries()
                    st.success("All manual entries cleared from database!")
                    st.rerun()
        
        with manage_col3:
            # Delete specific entry
            if len(manual_df) > 0:
                entry_to_delete_idx = st.selectbox(
                    "Select entry to delete:",
                    range(len(manual_df)),
                    format_func=lambda x: f"{manual_df.iloc[x]['client_name']} - {manual_df.iloc[x]['service_type']} ({manual_df.iloc[x]['visit_count']} visits)",
                    key="delete_entry_selector"
                )
                
                if st.button("Delete Selected Entry", type="secondary"):
                    if st.button("Confirm Delete", type="secondary", key="confirm_delete_entry"):
                        entry_id = manual_df.iloc[entry_to_delete_idx]['id']
                        db_service.delete_manual_entry(entry_id)
                        st.success("Entry deleted from database!")
                        st.rerun()

elif page == "Historical Records":
    st.header("📚 Historical Records & Data Management")
    
    # Backup and Restore Section
    st.subheader("💾 Backup & Restore")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Create Backup**")
        if st.button("📤 Export All Historical Data", type="primary"):
            try:
                # Export complete historical data
                history_export = st.session_state.data_storage.export_history()
                
                # Create backup timestamp
                backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"healthcare_analytics_backup_{backup_timestamp}.json"
                
                st.download_button(
                    label="Download Backup File",
                    data=history_export,
                    file_name=filename,
                    mime="application/json"
                )
                st.success("Backup file ready for download!")
                
            except Exception as e:
                st.error(f"Error creating backup: {str(e)}")
    
    with col2:
        st.markdown("**Restore from Backup**")
        uploaded_backup = st.file_uploader(
            "Choose backup file",
            type=['json'],
            help="Upload a previously created backup JSON file",
            key="backup_restore_uploader"
        )
        
        if uploaded_backup is not None:
            if st.button("📥 Restore Backup", type="secondary"):
                try:
                    # Read and restore backup
                    backup_content = uploaded_backup.read().decode('utf-8')
                    success = st.session_state.data_storage.import_history(backup_content)
                    
                    if success:
                        st.success("Backup restored successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to restore backup. Please check the file format.")
                        
                except Exception as e:
                    st.error(f"Error restoring backup: {str(e)}")
    
    with col3:
        st.markdown("**Data Management**")
        if st.button("🗑️ Clear All History", type="secondary"):
            if st.button("⚠️ Confirm Clear All", type="secondary"):
                st.session_state.data_storage.clear_history()
                st.success("All historical data cleared!")
                st.rerun()
        
        # Display history summary
        history_summary = st.session_state.data_storage.get_history_summary()
        st.metric("Total Records", history_summary['total_analyses'])
        st.metric("Unique Files", history_summary['unique_files'])
    
    st.markdown("---")
    
    # Get historical data
    history = st.session_state.data_storage.get_analysis_history()
    
    if history:
        st.subheader("📋 Historical Analysis Records")
        
        # Enhanced history view with filters
        col1, col2 = st.columns(2)
        
        with col1:
            # Date range filter
            if history:
                dates = [datetime.fromisoformat(record['timestamp']).date() for record in history]
                min_date = min(dates)
                max_date = max(dates)
                
                date_range = st.date_input(
                    "Filter by date range:",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
        
        with col2:
            # File filter
            unique_filenames = list(set([record['filename'] for record in history]))
            selected_files = st.multiselect(
                "Filter by filename:",
                unique_filenames,
                default=unique_filenames
            )
        
        # Filter records based on selections
        filtered_history = []
        for record in history:
            record_date = datetime.fromisoformat(record['timestamp']).date()
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
                if start_date <= record_date <= end_date and record['filename'] in selected_files:
                    filtered_history.append(record)
            elif record['filename'] in selected_files:
                filtered_history.append(record)
        
        # Display filtered records summary
        if filtered_history:
            st.markdown(f"**Showing {len(filtered_history)} of {len(history)} records**")
            
            # Create summary table
            summary_data = []
            for record in filtered_history:
                analysis = record['analysis']
                summary_data.append({
                    'Filename': record['filename'],
                    'Date': datetime.fromisoformat(record['timestamp']).strftime("%Y-%m-%d %H:%M"),
                    'Total_Rows': record['total_rows'],
                    'Clients': len(analysis['client_analysis']),
                    'Employees': len(analysis['employee_analysis']),
                    'Services': len(analysis['service_analysis'])
                })
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True)
            
            # Record selection for detailed view
            record_options = []
            for record in filtered_history:
                timestamp = datetime.fromisoformat(record['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
                record_options.append(f"{record['filename']} - {timestamp}")
            
            selected_record = st.selectbox("Select a record for detailed view:", record_options)
            
            if selected_record:
                # Find the selected record
                selected_index = record_options.index(selected_record)
                record = filtered_history[selected_index]
                
                # Display record details in expandable sections
                with st.expander("📄 File Information & Summary", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**File Details**")
                        st.write(f"**Filename:** {record['filename']}")
                        st.write(f"**Processed:** {datetime.fromisoformat(record['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"**Total Rows:** {record['total_rows']}")
                    
                    with col2:
                        st.markdown("**Analysis Summary**")
                        analysis = record['analysis']
                        st.write(f"**Unique Clients:** {len(analysis['client_analysis'])}")
                        st.write(f"**Unique Employees:** {len(analysis['employee_analysis'])}")
                        st.write(f"**Unique Services:** {len(analysis['service_analysis'])}")
                
                # Display analysis data
                with st.expander("📊 Detailed Analysis Data"):
                    tab1, tab2, tab3 = st.tabs(["Client Analysis", "Employee Analysis", "Service Analysis"])
                    
                    with tab1:
                        client_df = pd.DataFrame(analysis['client_analysis'])
                        st.dataframe(client_df, use_container_width=True)
                        
                        # Export option for this record
                        csv_data = client_df.to_csv()
                        st.download_button(
                            label="Export Client Data CSV",
                            data=csv_data,
                            file_name=f"client_analysis_{record['filename']}_{record['timestamp'][:10]}.csv",
                            mime="text/csv"
                        )
                    
                    with tab2:
                        employee_df = pd.DataFrame(analysis['employee_analysis'])
                        st.dataframe(employee_df, use_container_width=True)
                        
                        csv_data = employee_df.to_csv()
                        st.download_button(
                            label="Export Employee Data CSV",
                            data=csv_data,
                            file_name=f"employee_analysis_{record['filename']}_{record['timestamp'][:10]}.csv",
                            mime="text/csv"
                        )
                    
                    with tab3:
                        service_df = pd.DataFrame(analysis['service_analysis'])
                        st.dataframe(service_df, use_container_width=True)
                        
                        csv_data = service_df.to_csv()
                        st.download_button(
                            label="Export Service Data CSV",
                            data=csv_data,
                            file_name=f"service_analysis_{record['filename']}_{record['timestamp'][:10]}.csv",
                            mime="text/csv"
                        )
                
                # Individual record actions
                with st.expander("⚙️ Record Actions"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("🔄 Load as Current Analysis", key=f"load_{record['timestamp']}"):
                            # Load this historical record as current analysis
                            st.session_state.current_analysis = analysis
                            st.success("Historical record loaded as current analysis!")
                            st.rerun()
                    
                    with col2:
                        if st.button("📤 Export Record", key=f"export_{record['timestamp']}"):
                            record_export = json.dumps([record], indent=2)
                            st.download_button(
                                label="Download Record JSON",
                                data=record_export,
                                file_name=f"record_{record['filename']}_{record['timestamp'][:10]}.json",
                                mime="application/json"
                            )
                    
                    with col3:
                        if st.button("🗑️ Delete Record", key=f"delete_{record['timestamp']}"):
                            if st.button("⚠️ Confirm Delete", key=f"confirm_delete_{record['timestamp']}"):
                                success = st.session_state.data_storage.delete_analysis(record['timestamp'])
                                if success:
                                    st.success("Record deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete record.")
        
        else:
            st.info("No records match the selected filters.")
    
    else:
        st.info("No historical records found. Process some data first!")

elif page == "Export Data":
    st.header("📤 Export Data")
    
    if st.session_state.current_analysis:
        st.subheader("Current Analysis Export")
        
        analysis = st.session_state.current_analysis
        
        # Export options
        export_type = st.selectbox(
            "Select export type:",
            ["Analysis Summary", "Client Analysis", "Employee Analysis", "Service Analysis", "Fee Calculation"]
        )
        
        if st.button("Generate Export", type="primary"):
            try:
                export_df = None
                filename = None
                
                if export_type == "Analysis Summary":
                    # Create summary data
                    summary_data = {
                        'Category': ['Clients', 'Employees', 'Services'],
                        'Unique_Count': [
                            len(analysis['client_analysis']),
                            len(analysis['employee_analysis']),
                            len(analysis['service_analysis'])
                        ],
                        'Total_Instances': [
                            analysis['client_analysis']['count'].sum(),
                            analysis['employee_analysis']['count'].sum(),
                            analysis['service_analysis']['count'].sum()
                        ]
                    }
                    export_df = pd.DataFrame(summary_data)
                    filename = "analysis_summary.csv"
                
                elif export_type == "Client Analysis":
                    export_df = analysis['client_analysis'].reset_index()
                    filename = "client_analysis.csv"
                
                elif export_type == "Employee Analysis":
                    export_df = analysis['employee_analysis'].reset_index()
                    filename = "employee_analysis.csv"
                
                elif export_type == "Service Analysis":
                    export_df = analysis['service_analysis'].reset_index()
                    filename = "service_analysis.csv"
                
                elif export_type == "Fee Calculation":
                    fee_analysis = st.session_state.fee_calculator.calculate_fees(
                        analysis['service_analysis']
                    )
                    if not fee_analysis.empty:
                        export_df = fee_analysis.reset_index()
                        filename = "fee_calculation.csv"
                    else:
                        st.error("No fee data available. Please configure service rates first.")
                        export_df = None
                        filename = None
                
                # Generate download if we have valid data
                if export_df is not None and filename is not None:
                    csv_data = export_to_csv(export_df)
                    
                    st.download_button(
                        label=f"Download {filename}",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv"
                    )
                    
                    st.success(f"Export ready! Click the download button to save {filename}")
                else:
                    st.error("Failed to generate export data.")
                
            except Exception as e:
                st.error(f"Error generating export: {str(e)}")
    
    else:
        st.info("No current analysis data available. Please process a file first.")
    
    # Historical data export
    st.subheader("Historical Data Export")
    
    history = st.session_state.data_storage.get_analysis_history()
    
    if history:
        if st.button("Export All Historical Data", type="secondary"):
            try:
                # Create historical summary
                historical_summary = []
                for record in history:
                    analysis = record['analysis']
                    historical_summary.append({
                        'filename': record['filename'],
                        'timestamp': record['timestamp'],
                        'total_rows': record['total_rows'],
                        'unique_clients': len(analysis['client_analysis']),
                        'unique_employees': len(analysis['employee_analysis']),
                        'unique_services': len(analysis['service_analysis']),
                        'total_client_visits': sum(analysis['client_analysis'].values()) if isinstance(analysis['client_analysis'], dict) else analysis['client_analysis']['count'].sum(),
                        'total_employee_visits': sum(analysis['employee_analysis'].values()) if isinstance(analysis['employee_analysis'], dict) else analysis['employee_analysis']['count'].sum(),
                        'total_service_instances': sum(analysis['service_analysis'].values()) if isinstance(analysis['service_analysis'], dict) else analysis['service_analysis']['count'].sum()
                    })
                
                historical_df = pd.DataFrame(historical_summary)
                csv_data = export_to_csv(historical_df)
                
                st.download_button(
                    label="Download Historical Summary",
                    data=csv_data,
                    file_name="historical_analysis_summary.csv",
                    mime="text/csv"
                )
                
                st.success("Historical data export ready!")
                
            except Exception as e:
                st.error(f"Error exporting historical data: {str(e)}")
    
    else:
        st.info("No historical data available for export.")

elif page == "Animation Demo":
    st.header("🎨 Healthcare Loading Animations Demo")
    
    st.markdown("""
    This page demonstrates all the healthcare-themed loading animations available in the application.
    Each animation is designed to enhance user experience during different operations.
    """)
    
    st.subheader("Available Animation Types")
    
    # Create columns for animation demos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Heart Animation")
        st.markdown("Used for: General processing and data analysis")
        if st.button("Demo Heart Animation", key="demo_heart"):
            show_loading_animation(
                animation_type="heart",
                message="Processing Healthcare Data",
                subtitle="Analyzing patient visit patterns..."
            )
        
        st.markdown("### Medical Cross Animation")
        st.markdown("Used for: File processing and data validation")
        if st.button("Demo Cross Animation", key="demo_cross"):
            show_loading_animation(
                animation_type="cross",
                message="Processing Medical Files",
                subtitle="Validating healthcare records..."
            )
        
        st.markdown("### DNA Helix Animation")
        st.markdown("Used for: Advanced data analysis")
        if st.button("Demo DNA Animation", key="demo_dna"):
            show_loading_animation(
                animation_type="dna",
                message="Analyzing Healthcare Data",
                subtitle="Processing genetic information patterns..."
            )
    
    with col2:
        st.markdown("### Pills Animation")
        st.markdown("Used for: Fee calculations and billing")
        if st.button("Demo Pills Animation", key="demo_pills"):
            show_loading_animation(
                animation_type="pills",
                message="Calculating Service Fees",
                subtitle="Computing medication and treatment costs..."
            )
        
        st.markdown("### Stethoscope Animation")
        st.markdown("Used for: Data exports and reports")
        if st.button("Demo Stethoscope Animation", key="demo_stethoscope"):
            show_loading_animation(
                animation_type="stethoscope",
                message="Preparing Medical Report",
                subtitle="Formatting patient data for export..."
            )
    
    st.markdown("---")
    
    st.subheader("🎯 Specialized Loading Functions")
    
    demo_col1, demo_col2, demo_col3, demo_col4 = st.columns(4)
    
    with demo_col1:
        if st.button("File Processing Demo", type="secondary"):
            show_file_processing_loading()
    
    with demo_col2:
        if st.button("Analysis Demo", type="secondary"):
            show_analysis_loading()
    
    with demo_col3:
        if st.button("Calculation Demo", type="secondary"):
            show_calculation_loading()
    
    with demo_col4:
        if st.button("Export Demo", type="secondary"):
            show_export_loading()
    
    st.markdown("---")
    
    st.subheader("✨ Animation Features")
    
    features_col1, features_col2 = st.columns(2)
    
    with features_col1:
        st.markdown("""
        **Visual Elements:**
        - Animated healthcare icons (heart, cross, pills, stethoscope, DNA)
        - Smooth CSS transitions and transformations
        - Healthcare-themed color gradients
        - Pulsing, spinning, bouncing, and rotating effects
        """)
    
    with features_col2:
        st.markdown("""
        **User Experience:**
        - Context-specific loading messages
        - Progress indication with animated bars
        - Consistent 2-second display duration
        - Professional healthcare aesthetic
        """)

# Footer
st.markdown("---")
st.markdown("**Home Healthcare Analytics** - Streamline your healthcare data analysis workflow")
