# HKT_MS_Obitus
# AI Agent for High School Teachers - AI Skill Fest Hackathon Project

## 🚀 Description

This project is an AI assistant designed specifically to support high school teachers by providing quick access to school information, assisting with administrative queries, and potentially helping with data analysis tasks. Developed as part of the Microsoft AI Skill Fest AI Agents Hackathon, this agent aims to reduce teacher workload to manage large volumn of data timely and improve efficiency by leveraging Azure AI capabilities.

The agent understands natural language queries and utilizes a knowledge base derived from school documents (like regulations, calendars, and policies) and can perform calculations or data analysis using Code Interpreter.

## ✨ Features

*   **Knowledge-Based Q&A (RAG):** Answers questions based on uploaded school documents, including:
    *   Academic Calendar & Event Information
    *   School Rules & Operating Guidelines (Staff/Student regulations, Safety)
    *   Curriculum & Assessment Details (e.g., Grade 10 English examples)
    *   Facility Usage & Equipment Loan Procedures
    *   Internal System Usage Tips (LMS, Admin Systems)
    *   Teacher FAQs
*   **Data Analysis & Calculation (via Code Interpreter):**
    *   Analyzes anonymized sample data provided in CSV/XLSX files (e.g., calculating average scores, visualizing survey results).
    *   Performs mathematical calculations and solves equations upon request.
    *   Processes simple text files (e.g., sorting lists, finding definitions).
*   **Contextual Understanding:** Uses education-specific terminology and maintains a helpful, professional tone suitable for teachers.
*   **Safety & Constraints:** Designed to avoid handling sensitive student data and politely decline out-of-scope requests.

## ⚙️ How it Works

This AI Agent is built using **Azure AI Studio**. The core functionality relies on:

1.  **Azure OpenAI Service:** Utilizes a powerful language model (Model: gpt-4o-mini) as the agent's "brain".
2.  **Retrieval-Augmented Generation (RAG):**
    *   School documents (TXT) containing regulations, calendars, guides, etc., were uploaded and processed into a searchable knowledge base (likely using Azure AI Search behind the scenes).
    *   When a teacher asks a question, the agent first searches this knowledge base for relevant information.
3.  **Generation:** The retrieved information is then fed to the language model along with the original question and the system instructions (prompt) to generate an accurate and contextually relevant answer.
4.  **Code Interpreter Action:** For specific tasks like calculations or data analysis on provided files, the agent leverages the built-in Code Interpreter tool. The LLM generates Python code based on the request and the uploaded data files, which is then executed in a secure sandbox environment.
5.  **System Instructions (Prompt Engineering):** Carefully crafted instructions guide the agent's persona, capabilities, limitations, and tool usage logic.

## 🛠️ Technology Stack

*   **Platform:** Azure AI Studio
*   **Core AI Service:** Azure OpenAI Service (Model: gpt-4o-mini)
*   **Knowledge Base:** Azure AI Search (Managed via Azure AI Studio Data sources)
*   **Actions:** Code Interpreter (Built-in Azure AI Studio Action)
*   **Knowledge Files:** TXT

## 📚 Setup & Configuration (Conceptual)

To conceptually replicate this agent:

1.  Create an Azure AI Hub and an associated Azure OpenAI resource (deploying the desired model).
2.  In Azure AI Studio, create a new Agent project.
3.  **Knowledge Setup:**
    *   Prepare knowledge documents (like those in the `knowledge_files` folder of this repository). **Ensure all sensitive information is removed/anonymized.**
    *   Upload these documents via the Data sources -> `files` option to create a searchable index.
    *   Connect this data source in the Agent's 'Knowledge' settings.
4.  **Code Interpreter Setup:**
    *   Prepare sample data files (like those in the `code_interpreter_files` folder).
    *   Upload these files via the 'Manage files for code interpreter' option in the Agent's 'Actions' settings.
5.  **Instructions:** Configure the Agent's 'Instructions' (system prompt) similar to the content in `config/agent_instructions.md`. Ensure guidelines for using knowledge sources and Code Interpreter are included.
6.  **Actions:** Enable the 'Code Interpreter' action in the Agent's 'Actions' settings.
7.  **Testing:** Use the Azure AI Studio Playground to test the agent's responses to various queries related to the knowledge base and data analysis tasks.

**Note:** This repository contains the configuration files and knowledge assets, not the deployed Azure resources themselves. **Do NOT commit any API keys or sensitive credentials.**

## 🎬 Demo
https://youtu.be/XH4HpWa7h_g?feature=shared

Example Interactions:

**User:** "What are the dates for Term 1 final exams?"
**Agent:** (Retrieves info from Academic Calendar) "According to the school calendar, Term 1 final exams are scheduled from July 8th to July 12th, 2024."

**User:** "Calculate the average score for 'Unit 1 Quiz' from the `sample_grades_anonymized.txt` file."
**Agent:** (Uses Code Interpreter) "Okay, I will use the Code Interpreter to calculate the average score for 'Unit 1 Quiz' from the provided CSV file. ... The average score for the Unit 1 Quiz is 88.6."

[*(Insert Screenshot/GIF here if possible)*]

## 👥 Team

*   **Dave LEE:**
    *   Project Lead
    *   AI Agent Implementation
    *   Action/Knowledge Definition
*   **Moe:**
    *   Project Management
    *   Action/Knowledge Support
    *   Quality Assurance
    *   Technical Contribution

## 🙏 Acknowledgements

------PLAN TO ADD A MENTORS, DOCUMENTATION, RESOURCES HERE------

---
