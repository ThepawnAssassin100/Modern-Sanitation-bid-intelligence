import streamlit as st
import sqlite3
import pandas as pd

# --- DB setup ---
conn = sqlite3.connect("bids.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS bids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project TEXT,
    client TEXT,
    competitor TEXT,
    amount REAL,
    outcome TEXT CHECK(outcome IN ('won','lost'))
)
""")
conn.commit()

# --- Prepopulate with example bid data if empty ---
c.execute("SELECT COUNT(*) FROM bids")
if c.fetchone()[0] == 0:
    example_bids = [
        ("Sanitation Upgrade Lilongwe 🚰", "Lilongwe City Council", "CleanTech Ltd", 50000.00, "won"),
        ("Waste Management Mzuzu 🗑️", "Mzuzu City Council", "EcoSolutions", 42000.00, "lost"),
        ("Drainage Project Blantyre 🌧️", "Blantyre City Council", "UrbanFlow", 60000.00, "won"),
        ("Sewerage Extension Zomba 💧", "Zomba City Council", "PipeMasters", 55000.00, "lost"),
        ("Modern Toilet Installation Mangochi 🚽", "Mangochi District", "Sanitech", 48000.00, "won")
    ]
    c.executemany("INSERT INTO bids (project, client, competitor, amount, outcome) VALUES (?,?,?,?,?)", example_bids)
    conn.commit()

# --- App UI ---
st.set_page_config(page_title="Modern Sanitation", layout="wide")
st.title("Modern Sanitation")

st.markdown("Welcome to the **Modern Sanitation Bid Intelligence Dashboard**! 💡📊\n\nTrack your bids, analyze trends, and improve decision-making based on historical bid data.")

# --- Add new bid ---
with st.expander("➕ Add New Bid"):
    with st.form("new_bid"):
        st.subheader("Enter New Bid 📝")
        project = st.text_input("Project Name")
        client = st.text_input("Client")
        competitor = st.text_input("Competitor")
        amount = st.number_input("Bid Amount (MK)", min_value=0.0, format="%.2f")
        outcome = st.selectbox("Outcome", ["won","lost"])
        submitted = st.form_submit_button("💾 Save Bid")
        if submitted:
            c.execute(
                "INSERT INTO bids (project,client,competitor,amount,outcome) VALUES (?,?,?,?,?)",
                (project, client, competitor, amount, outcome)
            )
            conn.commit()
            st.success("✅ Bid saved successfully!")

# --- Display stored bids ---
st.subheader("📂 Stored Bids")
df = pd.read_sql("SELECT * FROM bids", conn)
st.dataframe(df.style.highlight_max(axis=0, color='#D6EAF8'))

# --- Basic analytics ---
st.subheader("📈 Bid Analytics")
if not df.empty:
    total_bids = len(df)
    wins = len(df[df['outcome'] == 'won'])
    losses = len(df[df['outcome'] == 'lost'])
    win_rate = (wins / total_bids) * 100
    st.metric("🏆 Overall Win Rate", f"{win_rate:.1f}%")
    st.metric("📌 Total Bids", total_bids)
    st.metric("❌ Lost Bids", losses)
    
    # Optional: highlight won/lost rows
    def highlight_outcome(val):
        color = '#A9DFBF' if val == 'won' else '#F5B7B1'
        return f'background-color: {color}'
    st.dataframe(df.style.applymap(highlight_outcome, subset=['outcome']))
