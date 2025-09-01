# image-audio-ai-agent
this is a image to audio ai agent using open ai and mistralai

🖼️🔊 Image-to-Audio AI Agent

This project extracts text from images or PDFs using Mistral AI (OCR) and then converts that extracted text into audio using OpenAI Whisper TTS.
The app is built with Streamlit for an interactive UI and integrates LangChain + Mistral + OpenAI APIs for AI capabilities.

🚀 Features

Upload images or PDFs or provide URLs for OCR processing

Extracts text using Mistral OCR

Edit extracted text directly inside the app

Export results as JSON or TXT files

Convert extracted text into audio using OpenAI TTS

Save generated audio files locally

Simple & user-friendly Streamlit UI

🛠️ Tech Stack

Frontend/UI → Streamlit

OCR Engine → Mistral AI OCR

Text-to-Speech → OpenAI Whisper TTS

Integration/Workflow → Python, Requests, LangChain

📂 Project Structure
image-audio-ai-agent/
│── app.py                # Main Streamlit app
│── requirements.txt      # Python dependencies
│── README.md             # Project documentation
│── .gitignore            # Ignore unnecessary files (venv, __pycache__, etc.)

⚡ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/your-username/image-audio-ai-agent.git
cd image-audio-ai-agent

2️⃣ Create Virtual Environment (recommended)
python -m venv venv
source venv/bin/activate   # for Linux/Mac
venv\Scripts\activate      # for Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run the App
streamlit run app.py

🔑 API Keys Required

Mistral API Key → for OCR (paste in UI input box)

OpenAI API Key → for Text-to-Speech (paste in UI input box)

🎯 Usage

Go to the OCR Text Extraction tab

Upload image/PDF or enter a URL

Extract and edit text

Save as .json or .txt

Switch to Text to Audio Conversion tab

Choose OCR result or upload a text file

Select a voice style

Generate & download audio

🚀 Deployment

You can deploy on:

Streamlit Cloud

[AWS EC2 + Docker]

[Heroku]

[Render]