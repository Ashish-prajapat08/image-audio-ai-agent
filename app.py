
import streamlit as st
import os
import base64
import json
import time
import tempfile
import requests
from mistralai import Mistral
from pathlib import Path


st.set_page_config(layout="wide",page_title="OCR & Audio AI",page_icon="🔊")

tab1, tab2 = st.tabs(["OCR Text Extraction", "Text to Audio conversion"])


def save_file(content, filename,folder_path, file_type ="binary"):

    try:
        os. makedirs(folder_path, exist_ok=True)
    
        file_path =os.path.join(folder_path, filename)

        if file_type == "text":
          with open( file_path , 'w', encoding = 'utf-8') as f:
            f.write(content)

        else: #binary content
           with open (file_path,'wb') as f:
            f.write(content)

        return True, file_path
    except Exception as e:
        return False, str(e)
    

with tab1:
    st.title("OCR Text Extraction")
    st.markdown("<h3 style= 'color: white; '> extract text from images and pdf's</h3>", unsafe_allow_html=True)

    api_key = st.text_input("Enter your Mistral API key", type="password")
    if not api_key:
        st.info("Please enter your API key to continue")
        st.stop()

    if "ocr_result" not in st.session_state:
        st.session_state["ocr_result"] = []
    if "preview_src" not in st.session_state:
        st.session_state["preview_src"] = []
    if "image_bytes" not in st.session_state:
        st.session_state["image_bytes"] = []

    output_folder = st.text_input("Output folder path for saving files", value=str(Path.home()/"ocr_audio_output"), help="file will be saved on this folder")

    if os.path.exists(output_folder):
        st.success(f"folder exists at : {output_folder}")
    else:
        st.warning(f"folder does not exist yet,but will be created when saving files.")
        try:
            os.makedirs(output_folder, exist_ok=True)
            st.success(f"folder created at : {output_folder}")
        except Exception as e:
            st.error(f"Error creating folder: {e}")

    # horizontal layout for file type and source type
    col1, col2 = st.columns(2)

    with col1:
        # choose the file type : PDF or Image
        file_type = st.radio("Select file type", ("Image", "PDF"), horizontal=True)

    with col2:
        # choose the source type : Upload local or URL
        source_type = st.radio("Select source type", ("local Upload", "URL"), horizontal=True)

    # input based on source type
    if source_type == "URL":
        input_url = st.text_area("enter one or multiple URLs (separated with new lines)")
        uploaded_files = []
    else:
        uploaded_files = st.file_uploader("Upload one or more files", type=["png", "jpg", "jpeg", "pdf"], accept_multiple_files=True)
        input_url = ""

    if st.button("process"):
        if source_type == "URL" and not input_url.strip():
            st.error("please enter at least one valid URL.")
        elif source_type == "local Upload" and not uploaded_files:
            st.error("please upload at least one file.")
        else:
            client = Mistral(api_key=api_key)
            st.session_state["ocr_result"] = []
            st.session_state["preview_src"] = []
            st.session_state["image_bytes"] = []

            source = input_url.split("\n") if source_type == "URL" else uploaded_files

            for idx, source in enumerate(source):
                if file_type == "PDF":
                    if source_type == "URL":
                        document = {"type": "document_url",
                                    "document_url": source.strip()} # type: ignore
                        preview_src = source.strip() # type: ignore
                    else:
                        file_bytes = source.read() # type: ignore
                        encoded_pdf = base64.b64encode(file_bytes).decode('utf-8')
                        document = {"type": "document_url",
                                    "document_url": f"data:application/pdf;base64,{encoded_pdf}"}
                else:
                    if source_type == "URL":
                        document = {"type": "image_url", "image_url": source.strip()} # type: ignore
                        preview_src = source.strip() # type: ignore
                    else:
                        file_bytes = source.read() # type: ignore
                        mime_type = source.type # type: ignore
                        encoded_image = base64.b64encode(file_bytes).decode('utf-8')
                        document = {"type": "image_url",
                                    "image_url": f"data:{mime_type};base64,{encoded_image}"}
                        preview_src = f"data:{mime_type};base64,{encoded_image}"
                        st.session_state["image_bytes"].append(file_bytes)

                with st.spinner(f"processing {source if source_type == 'URL' else source.name} ..."): # type: ignore
                    try:
                        ocr_response = client.ocr.process(model="mistral-ocr-latest",
                                                          document=document, include_image_base64=True) # type: ignore
                        time.sleep(1)  # wait 1 second between request to prevent rate limiting exceeding

                        pages = ocr_response.pages if hasattr(ocr_response, 'pages') else (ocr_response if isinstance(ocr_response, list) else [])
                        result_text = "\n\n".join(page.markdown for page in pages) or "no result found." # type: ignore
                    except Exception as e:
                        result_text = f"error extracting result: {e}"

                    st.session_state["ocr_result"].append(result_text)
                    st.session_state["preview_src"].append(preview_src) # type: ignore

    if st.session_state["ocr_result"]:
        for idx, result in enumerate(st.session_state["ocr_result"]):
            st.markdown("---")
            st.subheader(f"result {idx+1}")

            col1, col2 = st.columns(2)

            with col1:
                file_type_label = "PDF" if file_type == "PDF" else "Image"
                st.subheader(f"input {file_type_label}")
                if file_type == "PDF":
                    pdf_embed_html = f'<iframe src="{st.session_state["preview_src"][idx]}" width= "100%" height="400" frameborder="0"></iframe>'
                    st.markdown(pdf_embed_html, unsafe_allow_html=True)
                else:
                    if source_type == "local Upload" and idx < len(st.session_state["image_bytes"]):
                        st.image(st.session_state["image_bytes"][idx])
                    else:
                        st.image(st.session_state["preview_src"][idx])

            with col2:
                st.subheader("OCR Result")
                edited_text = st.text_area(
                    "extracted text (you can edit this)",
                    value=result,
                    height=300,
                    key=f"result_text_{idx}"
                )
                st.session_state["ocr_result"][idx] = edited_text

            btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)

            with btn_col1:
                    json_data = json.dumps({"ocr_result": edited_text}, ensure_ascii=False, indent=2)
                    json_b64 = base64.b64encode(json_data.encode()).decode()
                    st.markdown(
                        f'<a href ="data:application/json;base64,{json_b64}" download= "output_{idx+1}.json">download JSON</a>',
                        unsafe_allow_html=True
                    )
            with btn_col2:
                    text_b64 = base64.b64encode(edited_text.encode()).decode()
                    st.markdown(
                        f'<a href ="data:text/plain;base64,{text_b64}" download= "output_{idx+1}.txt">download TXT</a>',
                        unsafe_allow_html=True
                    )
            with btn_col3:
                    if st.button(f"save JSON to folder", key=f"save_json_{idx}"):
                        json_data = json.dumps({"ocr_result": edited_text}, ensure_ascii=False, indent=2)
                        success, result_path = save_file(
                            json_data, f"output_{idx+1}.json", output_folder, file_type="text")
                        if success:
                            st.success(f"JSON saved to: {result_path}")

                            if os.path.exists(result_path):
                                st.success(f" verified:file exists at: {result_path}")
                            else:
                                st.error(f"file not found at: {result_path}")
                        else:
                            st.error(f"failed to save JSON to: {result_path}")

            with btn_col4:
                    if st.button(f"save text to folder", key=f"save_text_{idx}"):
                        success, result_path = save_file(
                            edited_text, f"output_{idx+1}.txt", output_folder, file_type="text"
                        )
                        if success:
                            st.success(f"text saved to: {result_path}")

                            if os.path.exists(result_path):
                                st.success(f" verified:file exists at: {result_path}")
                            else:
                                st.error(f"file not found at: {result_path}")
                        else:
                            st.error(f"failed to save text: {result_path}")
            if st.button(f"convert to audio", key=f"convert_btn_{idx}"):
                st.session_state["current_text_for_audio"] = edited_text
                st.info("text ready for conversation. please go to the 'text to audio conversation' tab.")

with tab2:
    st.title("text to audio converter")
    openai_api_key = st.text_input("enter your openai api key", type="password", key="openai_api_key")

    if "output_folder" in locals():
        audio_output_folder = st.text_input("ouput folder, saved files", value=output_folder,
                                            help="files will be saved to this folder",
                                            key="audio_output_folder")
    else:
        audio_output_folder = st.text_input("output folder path for saved files",
                                            value=str(Path.home()/"ocr_audio_output"), help="files will be saved to this folder",
                                            key="audio_output_folder")
    if os.path.exists(audio_output_folder):
        st.success(f"folder exists at: {audio_output_folder}")
    else:
        st.warning(f"folder does not exist yet, but will be created when saving files.")
        try:
            os.makedirs(audio_output_folder, exist_ok=True)
            st.success(f"successfully folder created at: {audio_output_folder}")
        except Exception as e:
            st.error(f"unable to create folder: {str(e)}")

    col1, col2 = st.columns(2)

    with col1:
        text_source = st.radio("text source", ["OCR results input", "upload file"], horizontal=True)

    with col2:
        voice_option = st.selectbox("select voice style",
                                   ["alloy", "echo", "onyx", "nova", "shimmer"])

    text_for_audio = ""

    if text_source == "OCR results input":
        if st.session_state.get("ocr_result", []):
            result_options = [f"result {i+1}" for i in range(len(st.session_state["ocr_result"]))]

            default_idx = 0
            if "current_text_for_audio" in st.session_state:
                try:
                    default_idx = st.session_state["ocr_result"].index(
                        st.session_state["current_text_for_audio"])
                except ValueError:
                    default_idx = 0

            selected_result = st.selectbox("select OCR result to convert", result_options, index=default_idx)

            result_idx = result_options.index(selected_result)
            text_for_audio = st.session_state["ocr_result"][result_idx]

            text_for_audio = st.text_area("OCR text (you can edit before converting)", value=text_for_audio, height=300)

        else:
            st.warning("NO OCR results available. Process files in the OCR tab first or choose another source")

    elif text_source == "direct input":
        text_for_audio = st.text_area(
            "enter text to convert to audio",
            value="",
            height=300
        )
    else:
        uploaded_text_files = st.file_uploader("upload text files", type=["txt", "md"])

        if uploaded_text_files:
            text_content = uploaded_text_files.read().decode("utf-8")
            text_for_audio = st.text_area("text content from file (you can edit before converting)", value=text_content, height=300)

    def convert_text_to_speech(text, api_key, voice="alloy"):
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            url = "https://api.openai.com/v1/audio/speech"

            data = {
                "model": "tts-1",
                "input": text,
                "voice": voice
            }

            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                    temp_file.write(response.content)
                    temp_file_path = temp_file.name

                return True, temp_file_path, response.content
            else:
                return False, f"API Error: {response.status_code} , {response.text}", None

        except Exception as e:
            return False, f"Error: {str(e)}", None

    if "audio_results" not in st.session_state:
        st.session_state["audio_results"] = []

    if st.button("generate audio"):
        if not openai_api_key:
            st.error("please enter your openai api key to continue")
        elif not text_for_audio:
            st.error("please provide text to convert to audio")
        else:
            with st.spinner("converting text to audio..."):
                success, audio_path, audio_content = convert_text_to_speech(
                    text_for_audio, openai_api_key, voice=voice_option)

                if success:
                    st.session_state["audio_results"].append({
                        "text": text_for_audio[:100] + "..." if len(text_for_audio) > 100 else text_for_audio,
                        "path": audio_path,
                        "content": audio_content,
                        "voice": voice_option
                    })

                    st.success("audio generated successfully!")
                else:
                    st.error(f"error generating audio: {audio_path}")

    if st.session_state["audio_results"]:
        st.subheader("generated audio results")

        for idx, audio_data in enumerate(st.session_state["audio_results"]):
            with st.expander(f"Audio {idx+1} - {audio_data['voice']}",
                             expanded=(idx == len(st.session_state["audio_results"]) - 1)):

                st.markdown(f"**text:** {audio_data['text']}")
                st.audio(audio_data["path"])

                dl_col1, dl_col2 = st.columns(2)

                with dl_col1:
                    audio_b64 = base64.b64encode(audio_data["content"]).decode()
                    audio_href = f'<a href="data:audio/mp3;base64,{audio_b64}" download="audio_{idx+1}.mp3">Download audio file</a>'
                    st.markdown(audio_href, unsafe_allow_html=True)

                with dl_col2:
                    if st.button(f"save audio to folder", key=f"save_audio_{idx}"):
                        text_preview = audio_data["text"][:20].replace(" ", "_")

                        filename = f"audio_{idx+1}_{text_preview}.mp3"

                        success, result_path = save_file(audio_data["content"], filename,
                                                         audio_output_folder)

                        if success:
                            st.success(f"audio sved to: {result_path}")

                            if os.path.exists(result_path):
                                st.success(f"verified: file exists at: {result_path}")
                            else:
                                st.error(f"file not found at: {result_path}")
                        else:
                            st.error(f"failed to save audio: {result_path}")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color:#888888">
    <p>Built with mistral OCR and openAI Text-to-Speech</p>
</div>
""", unsafe_allow_html=True)
