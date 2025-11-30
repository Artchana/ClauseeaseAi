import streamlit as st
from datetime import datetime
import requests
import tempfile
import json
import io
import os

# PDF/DOCX extraction libraries 
try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

try:
    from docx import Document
except Exception:
    Document = None


class UniqueClauseEase:
    def __init__(self):
        self.setup_page()
        self.initialize_session_state()

    def setup_page(self):
        st.set_page_config(
            page_title="ClauseEase",
            page_icon="⚖️",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Unique modern CSS 
        st.markdown("""
        <style>
        /* Main theme colors */
        :root {
            --primary: #7B1FA2;
            --primary-dark: #6A1B9A;
            --secondary: #FF6F00;
            --accent: #00BFA5;
            --dark: #2E2E3A;
            --light: #F5F5F7;
        }
                    
        /* Placeholder text color */
            ::placeholder {
            color: #555 !important;
            opacity: 0.7 !important;
        }
        
        /* Main container */
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Unique chat bubbles */
        .user-message {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            padding: 18px 22px;
            border-radius: 24px 24px 8px 24px;
            margin: 12px 0;
            max-width: 75%;
            margin-left: auto;
            position: relative;
            box-shadow: 0 8px 25px rgba(123, 31, 162, 0.3);
            border: 2px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .user-message::before {
            content: "⚖️";
            position: absolute;
            right: -35px;
            top: 50%;
            transform: translateY(-50%);
            background: var(--primary);
            border-radius: 50%;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        .assistant-message {
            background: rgba(255, 255, 255, 0.95);
            color: var(--dark);
            padding: 18px 22px;
            border-radius: 24px 24px 24px 8px;
            margin: 12px 0;
            max-width: 75%;
            margin-right: auto;
            position: relative;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.3);
            backdrop-filter: blur(10px);
        }
        
        .assistant-message::before {
            content: "🤖";
            position: absolute;
            left: -35px;
            top: 50%;
            transform: translateY(-50%);
            background: var(--accent);
            border-radius: 50%;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0, 191, 165, 0.3);
        }
        
        /* Sidebar styling */
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, var(--dark) 0%, #1a1a24 100%);
            color: white;
        }
        
        /* Chat history items */
        .history-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 14px 16px;
            margin: 8px 0;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            border-left: 4px solid transparent;
            backdrop-filter: blur(10px);
        }
        
        .history-item:hover {
            background: rgba(255, 255, 255, 0.2);
            border-left: 4px solid var(--accent);
            transform: translateX(5px);
        }
        
        .history-item.active {
            background: rgba(123, 31, 162, 0.3);
            border-left: 4px solid var(--primary);
        }
        
        /* File upload area */
        .upload-area {
            border: 2px dashed var(--accent);
            border-radius: 16px;
            padding: 25px;
            text-align: center;
            background: rgba(0, 191, 165, 0.1);
            margin: 15px 0;
            transition: all 0.3s ease;
        }
        
        .upload-area:hover {
            background: rgba(0, 191, 165, 0.2);
            border-color: var(--primary);
        }
        
        /* Buttons with unique styling */
        .stButton button {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(123, 31, 162, 0.3);
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(123, 31, 162, 0.4);
        }
        
        /* Input field styling */
        .stTextInput input {
        border-radius: 16px;
        border: 2px solid rgba(123, 31, 162, 0.2);
        padding: 16px 20px;
        font-size: 16px;
        background: rgba(255, 255, 255, 0.95);
        color: black; /*  make user-typed text visible */
        transition: all 0.3s ease;
        }

        
        .stTextInput input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(123, 31, 162, 0.1);
        }
        
        /* Header styling */
        .main-header {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            position: relative;
            overflow: hidden;
        }
        
        .main-header::before {
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
            transform: rotate(45deg);
            animation: shine 3s infinite;
        }
        
        @keyframes shine {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }
        
        /* Quick action cards */
        .action-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 16px;
            margin: 10px 0;
            text-align: center;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
        }
        
        .action-card:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-5px);
            border-color: var(--accent);
        }
        
        /* File cards */
        .file-card {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 12px;
            margin: 8px 0;
            border-left: 4px solid var(--secondary);
        }
        </style>
        """, unsafe_allow_html=True)

    def initialize_session_state(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "uploaded_files" not in st.session_state:
            st.session_state.uploaded_files = []
        if "current_chat" not in st.session_state:
            st.session_state.current_chat = "chat_1"
        if "chat_sessions" not in st.session_state:
            st.session_state.chat_sessions = {
                "chat_1": {"name": "Contract Discussion", "messages": [], "timestamp": datetime.now()}
            }
        # New session state keys for doc pipeline
        if "doc_memory" not in st.session_state:
            st.session_state.doc_memory = ""            # merged summaries from chunks
        if "processed_files" not in st.session_state:
            st.session_state.processed_files = set()    # filenames processed this session
        if "processing_doc" not in st.session_state:
            st.session_state.processing_doc = False    # flag while processing

    def process_file(self, uploaded_file):
        """Process uploaded file with proper error handling (keeps original behaviour)"""
        try:
            if uploaded_file is None:
                return None

            if uploaded_file.type == "text/plain":
                # note: avoid consuming file if other pipeline reads it; this method used only for small preview
                content = str(uploaded_file.read(), "utf-8")
                return {
                    "filename": uploaded_file.name,
                    "content": content[:800] + "..." if len(content) > 800 else content,
                    "upload_time": datetime.now().strftime("%H:%M"),
                    "icon": "📄",
                    "size": f"{(len(content) / 1024):.1f} KB"
                }
            else:
                return {
                    "filename": uploaded_file.name,
                    "content": f"File type: {uploaded_file.type}",
                    "upload_time": datetime.now().strftime("%H:%M"),
                    "icon": "📄",
                    "size": f"{(uploaded_file.size / 1024):.1f} KB"
                }
        except Exception as e:
            return {
                "filename": uploaded_file.name if uploaded_file else "Unknown",
                "content": f"Error processing file: {str(e)}",
                "upload_time": datetime.now().strftime("%H:%M"),
                "icon": "❌",
                "size": "Unknown"
            }

    def simplify_text(self, text):
        """Simplify contract text with enhanced processing"""
        simplifications = {
            "hereinafter": "from now on",
            "notwithstanding": "despite",
            "forthwith": "immediately",
            "pursuant to": "according to",
            "in lieu of": "instead of",
            "termination": "ending",
            "obligation": "duty",
            "indemnify": "protect from loss",
            "warranty": "guarantee",
            "liability": "legal responsibility",
            "party of the first part": "first party",
            "party of the second part": "second party",
            "thirty (30) days": "30 days",
            "written notice": "written notification",
            "either party": "any party",
            "this agreement": "this contract"
        }

        simplified = text
        for complex_word, simple_word in simplifications.items():
            simplified = simplified.replace(complex_word, f"**{simple_word}**")

        return simplified

    def get_response(self, user_input):
        """
        Generate chatbot response using local Llama 3.2 model via Ollama
        """
        import requests

        try:
            # Send request to Ollama API
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": user_input,
                    "stream": False
                },
                timeout=180
            )

            # Handle API result
            if response.status_code == 200:
                # attempt to parse common response shapes
                data = response.json()
                if isinstance(data, dict):
                    # common key "response"
                    if "response" in data:
                        return data["response"]
                    # sometimes it's {"choices": [{"text": "..."}]}
                    if "choices" in data and isinstance(data["choices"], list) and len(data["choices"]) > 0:
                        c = data["choices"][0]
                        return c.get("text") or c.get("message") or str(c)
                    # fallback
                    return str(data)
                else:
                    return str(data)
            else:
                return f" Ollama API Error: {response.status_code} - {response.text}"

        except requests.exceptions.ConnectionError:
            return " Cannot connect to Ollama. Please ensure Ollama is running (`ollama serve`)."

        except Exception as e:
            return f" Error generating response: {str(e)}"

    # ------------------- NEW: extraction, chunking, temp-json, send-to-model -------------------
    def extract_text_from_file(self, uploaded_file):
        """
        Extract text from uploaded file content. Supports txt, pdf, docx.
        """
        try:
            raw = uploaded_file.read()
            # ensure we can re-read this file later by rewinding
            try:
                uploaded_file.seek(0)
            except Exception:
                pass

            name_lower = (uploaded_file.name or "").lower()
            ctype = (uploaded_file.type or "").lower()

            # TXT
            if "text" in ctype or name_lower.endswith(".txt"):
                try:
                    return raw.decode("utf-8")
                except:
                    return raw.decode("latin-1", errors="ignore")

            # PDF
            if "pdf" in ctype or name_lower.endswith(".pdf"):
                if PdfReader is None:
                    return "[PDF extractor not available: PyPDF2 not installed]"
                try:
                    reader = PdfReader(io.BytesIO(raw))
                    text = ""
                    for p in reader.pages:
                        page_text = p.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    return text
                except Exception as e:
                    return f"[PDF extraction error] {str(e)}"

            # DOCX
            if name_lower.endswith(".docx") or "word" in ctype or name_lower.endswith(".doc"):
                if Document is None:
                    return "[DOCX extractor not available: python-docx not installed]"
                try:
                    doc = Document(io.BytesIO(raw))
                    paragraphs = [p.text for p in doc.paragraphs]
                    return "\n".join(paragraphs)
                except Exception as e:
                    return f"[DOCX extraction error] {str(e)}"

            return "[Unsupported file type]"

        except Exception as ex:
            return f"[Extraction failed] {str(ex)}"

    def chunk_text(self, text, chunk_size=400):
        """Word-based chunker"""
        if not text:
            return []
        words = text.split()
        chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
        return chunks

    def create_temp_json(self, filename, chunks):
        """Create temporary json file containing filename + chunks; return path"""
        tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json", prefix="clauseease_", encoding="utf-8")
        json_obj = {"filename": filename, "created_at": datetime.now().isoformat(), "chunks_count": len(chunks), "chunks": chunks}
        json.dump(json_obj, tmp, ensure_ascii=False, indent=2)
        tmp.close()
        return tmp.name

    def process_uploaded_document(self, uploaded_file, chunk_size=400):
        """
        Full pipeline called when user uploads a file:
        extract -> chunk -> temp json -> send each chunk to Ollama (get summary) -> merge summaries
        """
        if uploaded_file is None:
            return {"success": False, "error": "No file"}

        filename = uploaded_file.name
        # guard: skip re-processing same filename in same session
        if filename in st.session_state.processed_files:
            return {"success": True, "message": "Already processed in this session."}

        # mark processing
        st.session_state.processing_doc = True

        try:
            extracted = self.extract_text_from_file(uploaded_file)

            # Basic checks
            if not extracted or extracted.strip() == "" or extracted.startswith("["):
                return {"success": False, "error": f"Extraction error or empty content: {extracted}"}

            # chunk
            chunks = self.chunk_text(extracted, chunk_size=chunk_size)
            if not chunks:
                return {"success": False, "error": "No chunks created (empty text)."}

            # save temp json
            json_path = self.create_temp_json(filename, chunks)

            # send each chunk to Ollama and collect short summaries
            chunk_summaries = []
            total = len(chunks)
            for idx, ch in enumerate(chunks):
                # short summarization prompt for chunk
                prompt = (
                    f"You are ClauseEase assistant. Summarize the following document chunk in 2-4 short sentences. "
                    f"List any key obligations, deadlines, or party duties if present.\n\nChunk ({idx+1}/{total}):\n{ch}\n\nSummary:"
                )
                summary = self.get_response(prompt)
                # fallback if no response
                if not summary:
                    summary = "[No summary returned]"
                chunk_summaries.append({"index": idx, "summary": summary})

            # merge summaries into a single doc memory
            merged = "\n\n".join([f"Chunk {c['index']+1} summary:\n{c['summary']}" for c in chunk_summaries])
            st.session_state.doc_memory = merged
            st.session_state.processed_files.add(filename)

            return {"success": True, "json_path": json_path, "chunks": len(chunks), "merged_preview": merged[:2000]}

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            st.session_state.processing_doc = False

    # ------------------- Sidebar & main UI rendering -------------------
    def render_sidebar(self):
        """Render the unique sidebar"""
        with st.sidebar:
            # Header
            st.markdown("""
            <div style='text-align: center; padding: 20px 0;'>
                <h1 style='color: white; margin: 0; font-size: 28px;'>⚖️</h1>
                <h2 style='color: white; margin: 5px 0; font-size: 18px;'>ClauseEase</h2>
                <p style='color: #aaa; margin: 0; font-size: 12px;'>Legal AI Assistant</p>
            </div>
            """, unsafe_allow_html=True)

            # New Chat Button
            if st.button(" New Conversation", use_container_width=True):
                new_chat_id = f"chat_{len(st.session_state.chat_sessions) + 1}"
                st.session_state.chat_sessions[new_chat_id] = {
                    "name": f"Chat {len(st.session_state.chat_sessions) + 1}",
                    "messages": [], "timestamp": datetime.now()
                }
                st.session_state.current_chat = new_chat_id
                st.session_state.messages = []
                st.rerun()

            st.markdown("---")

            # Chat History
            st.markdown("### 💬 Conversations")
            for chat_id, chat_data in sorted(
                st.session_state.chat_sessions.items(),
                key=lambda x: x[1]["timestamp"],
                reverse=True
            )[:6]:
                is_active = chat_id == st.session_state.current_chat
                emoji = "🔵" if is_active else "⚪"

                if st.button(
                    f"{emoji} {chat_data['name']}",
                    key=chat_id,
                    use_container_width=True,
                    type="primary" if is_active else "secondary"
                ):
                    st.session_state.current_chat = chat_id
                    st.session_state.messages = chat_data["messages"]
                    st.rerun()

            st.markdown("---")

            # File Upload Section (unchanged placement / styling)
            st.markdown("### Upload Contract")
            st.markdown('<div class="upload-area">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Drag & Drop or Click to Browse",
                type=['txt', 'pdf', 'docx', 'doc'],
                label_visibility="collapsed",
                key="file_uploader"
            )
            st.markdown('</div>', unsafe_allow_html=True)

            # NEW: Immediately process uploaded file (only once per filename per session)
            if uploaded_file is not None:
                # only append lightweight metadata to uploaded_files to show in sidebar
                if uploaded_file.name not in [f["filename"] for f in st.session_state.uploaded_files]:
                    file_meta = {
                        "filename": uploaded_file.name,
                        "upload_time": datetime.now().strftime("%H:%M"),
                        "size": f"{(uploaded_file.size / 1024):.1f} KB",
                        "icon": "📄"
                    }
                    st.session_state.uploaded_files.append(file_meta)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"**📎 File Uploaded Successfully!**\n\n• **File:** {file_meta.get('filename', 'Unknown')}\n• **Time:** {file_meta.get('upload_time', 'Unknown')}\n• **Size:** {file_meta.get('size', 'Unknown')}\n• **Status:** ✅ Ready for analysis\n\nI'm processing the document now (extract → json → chunk → model). Please wait a moment..."
                    })

                # call the pipeline if not already processed
                if uploaded_file.name not in st.session_state.processed_files and not st.session_state.processing_doc:
                    info = self.process_uploaded_document(uploaded_file, chunk_size=400)
                    if info.get("success"):
                        # Append the document summary as an assistant message (main chat)
                        merged_preview = st.session_state.doc_memory
                        preview_short = merged_preview[:4000]  # limit size shown in one message
                        st.session_state.messages.append({"role": "assistant", "content": f"**📄 Document processed: {uploaded_file.name}**\n\n{preview_short}"})
                        st.rerun()
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": f"Document processing failed: {info.get('error')}"})
                        st.rerun()

            st.markdown("---")
            # Quick Actions
            st.markdown("###  Quick Actions")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(" Help", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": "help"})
                    response = self.get_response("help")
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()
            with col2:
                if st.button(" Example", use_container_width=True):
                    example = "simplify Either party may terminate this agreement with a thirty (30) days written notice to the other party"
                    st.session_state.messages.append({"role": "user", "content": example})
                    response = self.get_response(example)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()

    def render_main_chat(self):
        """Render the main chat interface"""
        # Unique header
        st.markdown("""
        <div class="main-header">
            <h1 style="margin: 0; font-size: 2.5rem;">⚖️ ClauseEase</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9;">
            AI-Powered Contract Simplification
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Chat container
        chat_container = st.container()

        with chat_container:
            # Display messages
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="user-message">
                        <div style="font-weight: 600; margin-bottom: 8px;">You</div>
                        <div>{message["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="assistant-message">
                        <div style="font-weight: 600; margin-bottom: 8px;">ClauseEase AI</div>
                        <div>{message["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # If doc_memory exists but no message was added (edge case), show it once here
            # (Usually we appended merged summary into messages during processing)
            if st.session_state.get("doc_memory", "").strip() and not any("Document processed" in (m.get("content","") if m.get("role")=="assistant" else "") for m in st.session_state.messages):
                preview_short = st.session_state.doc_memory[:4000]
                st.markdown(f"""
                <div class="assistant-message">
                    <div style="font-weight: 600; margin-bottom: 8px;">ClauseEase AI</div>
                    <div>**📄 Document summary (loaded):**<br>{preview_short}</div>
                </div>
                """, unsafe_allow_html=True)

            # Empty space for new messages
            if not st.session_state.messages:
                st.markdown("""
                <div style="text-align: center; padding: 60px 20px; color: #666;">
                    <h3> Ready to Simplify Your Contracts?</h3>
                    <p>Start by uploading a contract file or typing a message below!</p>
                </div>
                """, unsafe_allow_html=True)

        # Input section
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_input(
                "Type your message here...",
                placeholder="Type your message here...'",
                label_visibility="collapsed"
            )
        with col2:
            send_button = st.button("Send ", use_container_width=True)

        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        with col2:
            if st.button("More Examples", use_container_width=True):
                examples = [
                    "simplify Notwithstanding anything to the contrary herein",
                    "What does indemnification mean?",
                    "Explain termination clauses in simple terms"
                ]
                import random
                example = random.choice(examples)
                st.session_state.messages.append({"role": "user", "content": example})
                response = self.get_response(example)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        with col3:
            if st.button(" Simplify", use_container_width=True) and user_input:
                user_input = "simplify " + user_input
                st.session_state.messages.append({"role": "user", "content": user_input})
                response = self.get_response(user_input)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()

        if send_button and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            # include document memory as context if present
            doc_ctx = st.session_state.get("doc_memory", "")
            if doc_ctx:
                prompt = doc_ctx + "\n\nUser: " + user_input
            else:
                prompt = user_input

            response = self.get_response(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    def run(self):
        # Update current chat session
        if st.session_state.current_chat in st.session_state.chat_sessions:
            st.session_state.chat_sessions[st.session_state.current_chat]["messages"] = st.session_state.messages

        # Render layout
        self.render_sidebar()
        self.render_main_chat()


# Run the app
if __name__ == "__main__":
    app = UniqueClauseEase()
    app.run()
