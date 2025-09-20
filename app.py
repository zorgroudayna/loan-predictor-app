# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="Prédicteur de Demande de Prêt",
    page_icon="https://apiv1.2l-courtage.com/public/storage/jpg/pPy95t2JQnO2rgBOpXVJoT9HD0YW4JSgee74GNKD.jpeg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add CSS
st.markdown("""
<style>
    .main-header { 
        font-family: 'Montserrat', Arial, sans-serif;
        font-weight: 800;
        font-size: 2.2rem; 
        color: #22abc5; 
        text-align: center; 
        margin-bottom: 2rem; 
        letter-spacing: 1px;
    }
    .section-header { 
        font-family: 'Montserrat', Arial, sans-serif;
        font-weight: 700;
        font-size: 1.1rem; 
        text-align: left; 
        margin-top: 15px; 
        margin-bottom: 10px; 
        width: 100%; 
        border-bottom: 3px solid #22abc5;
        color: #22abc5; 
        text-transform: uppercase; 
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# En-tête avec logo
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("https://apiv1.2l-courtage.com/public/storage/jpg/pPy95t2JQnO2rgBOpXVJoT9HD0YW4JSgee74GNKD.jpeg", 
             width=100)
with col_title:
    st.markdown("""
    <div class="main-header">Prédicteur de Demande de Prêt</div>
    """, unsafe_allow_html=True)

# Simple form for demonstration
with st.form("loan_form"):
    st.markdown('<div class="section-header">Informations de Base</div>', unsafe_allow_html=True)
    salary = st.number_input("Salaire Mensuel (€)", min_value=0.0, value=2500.0, step=100.0)
    loan_amount = st.number_input("Montant du Prêt (€)", min_value=0.0, value=100000.0, step=1000.0)
    loan_duration = st.slider("Durée du Prêt (années)", min_value=1, max_value=30, value=20)
    
    submitted = st.form_submit_button("Évaluer la Demande")

if submitted:
    # Simple calculation for demonstration
    monthly_payment = loan_amount / (loan_duration * 12)
    affordability = salary * 0.35  # 35% of salary
    
    if monthly_payment <= affordability:
        st.success("Votre demande a de fortes chances d'être acceptée!")
        st.write(f"Mensualité estimée: {monthly_payment:.2f}€")
        st.write(f"Seuil de faisabilité: {affordability:.2f}€")
    else:
        st.error("Votre demande pourrait être refusée en l'état actuel.")
        st.write(f"Mensualité estimée: {monthly_payment:.2f}€")
        st.write(f"Seuil de faisabilité: {affordability:.2f}€")
        st.write("Conseil: Essayez de réduire le montant du prêt ou d'augmenter la durée.")