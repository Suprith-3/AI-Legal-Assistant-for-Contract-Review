import streamlit as st
import pdfplumber
import docx
from annotated_text import annotated_text

st.title("AI Legal Assistant - Contract Review with Highlights & Suggestions")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload a contract (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

def extract_text(uploaded_file):
    text = ""
    if uploaded_file.name.endswith(".pdf"):
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    elif uploaded_file.name.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:  # TXT
        text = uploaded_file.read().decode("utf-8")
    return text

# --- Risky Clause Detector with Suggestions ---
def analyze_contract(text):
    risks = {
        "sole discretion": {
            "risk": "High Risk",
            "color": "red",
            "issue": "Too vague and one-sided, Party A has all control.",
            "suggestion": "Clearly define the scope of services."
        },
        "any interest rate": {
            "risk": "High Risk",
            "color": "red",
            "issue": "Uncapped interest rate, unfair to Party B.",
            "suggestion": "Set a fixed or capped interest rate (e.g., 2% per month)."
        },
        "trusted partners": {
            "risk": "Medium Risk",
            "color": "orange",
            "issue": "Allows disclosure of confidential info without consent.",
            "suggestion": "Require prior written consent before disclosure."
        },
        "terminate immediately": {
            "risk": "Medium Risk",
            "color": "orange",
            "issue": "Too harsh, no grace period.",
            "suggestion": "Provide a cure period (e.g., 15 days for payment delays)."
        },
        "not be held liable for any damages": {
            "risk": "High Risk",
            "color": "red",
            "issue": "Removes all accountability from Party A.",
            "suggestion": "Limit liability to reasonable levels (e.g., gross negligence)."
        }
    }

    annotations = []
    reviews = []

    sentences = text.split(".")
    for sent in sentences:
        found = False
        for phrase, details in risks.items():
            if phrase in sent:
                annotations.append((sent.strip() + ". ", details["risk"], details["color"]))
                reviews.append({
                    "clause": sent.strip(),
                    "risk": details["risk"],
                    "issue": details["issue"],
                    "suggestion": details["suggestion"]
                })
                found = True
                break
        if not found and sent.strip():
            annotations.append((sent.strip() + ". ", "OK", "green"))

    return annotations, reviews

if uploaded_file:
    contract_text = extract_text(uploaded_file)

    st.subheader("📄 Original Contract")
    st.text_area("Contract Content", contract_text, height=250)

    if st.button("🔍 Review Contract"):
        st.subheader("✅ Reviewed Contract with Highlights")
        annotations, reviews = analyze_contract(contract_text)
        annotated_text(*annotations)

        st.subheader("📋 Detailed Review & Suggestions")
        for idx, review in enumerate(reviews, 1):
            st.markdown(f"**Clause {idx}:** {review['clause']}")
            st.markdown(f"- ⚠️ **Issue:** {review['issue']}")
            st.markdown(f"- 💡 **Suggestion:** {review['suggestion']}")
            st.markdown(f"- 🛑 **Risk Level:** {review['risk']}")
            st.markdown("---")