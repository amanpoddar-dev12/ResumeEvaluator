import streamlit as st
import PyPDF2
import google.generativeai as genai
import json  # To handle structured responses
import os
from dotenv import load_dotenv

load_dotenv()
# Function to extract text from a PDF resume
def extract_text_from_pdf(uploaded_file):
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None


# Function to initialize the Gemini model
def model_llm():
    genai.configure(api_key=os.getenv("API_KEY"))  # Replace with your actual Gemini API key
    return genai.GenerativeModel("gemini-pro")


# Function to analyze the resume based on the selected job role
def analyze_resume(resume_text, job_role):
    prompt = f"""
    You are an AI-powered ATS resume evaluator. Your task is to analyze the following resume and provide a structured review **specific to the job role of {job_role}**.

    **Resume Text:** 
    ---
    {resume_text}
    ---

    **Expected JSON Output Format:** 
    {{
        "ATS_Score": 85,
        "Key_Details": {{
            "Name": "John Doe",
            "Contact": "johndoe@email.com",
            "Skills": ["Python", "Machine Learning", "Data Science"],
            "Education": "B.Tech in Computer Science",
            "Experience": "2 years at XYZ Company",
            "Certifications": ["AWS Certified"],
            "Projects": ["Chatbot using NLP"]
        }},
        "Improvement_Suggestions": [
            "Add more technical skills relevant to {job_role}.",
            "Include more ATS-friendly keywords.",
            "Optimize resume formatting for better readability."
        ],
        "Recommended_Courses": [
            "Machine Learning by Andrew Ng (Coursera)",
            "Data Structures & Algorithms in Python (Udemy)"
        ]
    }}
    """

    model = model_llm()
    response = model.generate_content(prompt)

    return response.text.strip()


# Streamlit UI
def main():
    st.set_page_config(page_title="Resume ATS Evaluator", layout="wide")

    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>📄 Resume ATS Evaluator</h1>", unsafe_allow_html=True)
    st.write("Upload your resume, select the job role you are applying for, and get tailored ATS insights.")

    uploaded_file = st.file_uploader("📂 Upload Resume (PDF)", type="pdf")

    job_role = st.text_input("🎯 Enter the job role you are applying for (e.g., Software Engineer, Data Analyst)")

    if uploaded_file and job_role:
        st.success("✅ Resume uploaded successfully!")
        resume_text = extract_text_from_pdf(uploaded_file)

        if resume_text:
            st.subheader("📊 Resume Analysis")
            with st.spinner("🔍 Analyzing resume... Please wait."):
                ats_result = analyze_resume(resume_text, job_role)

            try:
                ats_data = json.loads(ats_result)  # Convert string to JSON
            except json.JSONDecodeError:
                st.error("⚠️ Error in AI response formatting.")
                st.write(ats_result)  # Show raw output if JSON parsing fails
                return

            # Display ATS Score
            st.markdown(
                f"<h2 style='text-align: center; color: #FF5733;'>🎯 ATS Score: {ats_data['ATS_Score']}/100</h2>",
                unsafe_allow_html=True,
            )

            # Display Key Details in a structured format
            st.subheader("📌 Extracted Resume Details")
            details = ats_data["Key_Details"]
            st.markdown(f"""
            - **👤 Name:** {details.get("Name", "N/A")}
            - **📧 Contact:** {details.get("Contact", "N/A")}
            - **🛠 Skills:** {", ".join(details.get("Skills", []))}
            - **🎓 Education:** {details.get("Education", "N/A")}
            - **💼 Experience:** {details.get("Experience", "N/A")}
            - **📜 Certifications:** {", ".join(details.get("Certifications", []))}
            - **📂 Projects:** {", ".join(details.get("Projects", []))}
            """, unsafe_allow_html=True)

            # Improvement Suggestions
            st.subheader("🚀 Suggestions for Improvement")
            for suggestion in ats_data["Improvement_Suggestions"]:
                st.markdown(f"- ✅ {suggestion}")

            # Recommended Courses
            st.subheader("📚 Recommended Courses & Certifications")
            for course in ats_data["Recommended_Courses"]:
                st.markdown(f"- 📖 {course}")

    elif uploaded_file and not job_role:
        st.warning("⚠️ Please enter the job role before analyzing your resume.")

    elif not uploaded_file and job_role:
        st.warning("⚠️ Please upload your resume before analysis.")


if __name__ == "__main__":
    main()
