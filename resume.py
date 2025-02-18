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
            "Projects": ["Chatbot using NLP"],
            "Languages": ["English", "Spanish"],
            "Achievements": ["Best Employee Award 2022"],
            "Interests": ["AI Research", "Open Source Contributions"]
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

    **Important Notes:**
    - If you cannot extract certain details, use "N/A" or an empty list/string as appropriate.
    - Ensure the output is always in valid JSON format.
    - If the resume text is insufficient or unclear, return a JSON with default values and suggestions for improvement.
    """

    model = model_llm()
    response = model.generate_content(prompt)

    try:
        # Attempt to parse the response as JSON
        return json.loads(response.text.strip())
    except json.JSONDecodeError:
        # If parsing fails, return a default JSON structure
        return {
            "ATS_Score": 0,
            "Key_Details": {
                "Name": "N/A",
                "Contact": "N/A",
                "Skills": [],
                "Education": "N/A",
                "Experience": "N/A",
                "Certifications": [],
                "Projects": [],
                "Languages": [],
                "Achievements": [],
                "Interests": []
            },
            "Improvement_Suggestions": [
                "The resume text was insufficient or unclear. Please ensure the resume is complete and well-formatted."
            ],
            "Recommended_Courses": []
        }


# Streamlit UI
def main():
    st.set_page_config(page_title="Resume ATS Evaluator", layout="wide")

    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>📄 Resume ATS Evaluator</h1>", unsafe_allow_html=True)
    st.write("Upload your resume, and get tailored ATS insights. You can optionally enter the job role you are applying for.")

    uploaded_file = st.file_uploader("📂 Upload Resume (PDF)", type="pdf")

    job_role = st.text_input("🎯 Enter the job role you are applying for (e.g., Software Engineer, Data Analyst) (Optional)")

    # Add a button to trigger the analysis
    analyze_button = st.button("🔍 Analyze Resume")

    if uploaded_file and analyze_button:
        st.success("✅ Resume uploaded successfully!")
        resume_text = extract_text_from_pdf(uploaded_file)

        if resume_text:
            st.subheader("📊 Resume Analysis")
            with st.spinner("🔍 Analyzing resume... Please wait."):
                # If job role is provided, use it, otherwise use a default message
                job_role_input = job_role if job_role else "General Job Role"
                ats_result = analyze_resume(resume_text, job_role_input)

            # Display ATS Score
            st.markdown(
                f"<h2 style='text-align: center; color: #FF5733;'>🎯 ATS Score: {ats_result['ATS_Score']}/100</h2>",
                unsafe_allow_html=True,
            )

            # Display Key Details in a structured format
            st.subheader("📌 Extracted Resume Details")
            details = ats_result["Key_Details"]
            st.markdown(f"""
            - **👤 Name:** {details.get("Name", "N/A")}
            - **📧 Contact:** {details.get("Contact", "N/A")}
            - **🛠 Skills:** {", ".join(details.get("Skills", []))}
            - **🎓 Education:** {details.get("Education", "N/A")}
            - **💼 Experience:** {details.get("Experience", "N/A")}
            - **📜 Certifications:** {", ".join(details.get("Certifications", []))}
            - **📂 Projects:** {", ".join(details.get("Projects", []))}
            - **🗣 Languages:** {", ".join(details.get("Languages", []))}
            - **🏆 Achievements:** {", ".join(details.get("Achievements", []))}
            - **🎨 Interests:** {", ".join(details.get("Interests", []))}
            """, unsafe_allow_html=True)

            # Improvement Suggestions
            st.subheader("🚀 Suggestions for Improvement")
            for suggestion in ats_result["Improvement_Suggestions"]:
                st.markdown(f"- ✅ {suggestion}")

            # Recommended Courses
            st.subheader("📚 Recommended Courses & Certifications")
            for course in ats_result["Recommended_Courses"]:
                st.markdown(f"- 📖 {course}")

    elif uploaded_file and not analyze_button:
        st.warning("⚠️ Please click the 'Analyze Resume' button to get the ATS evaluation.")

    elif not uploaded_file and analyze_button:
        st.warning("⚠️ Please upload your resume before analysis.")


if __name__ == "__main__":
    main()