import streamlit as st

def page_layout():
    return st.markdown("""
        <style>
            /* Global Font & Theme Adjustments */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
            }

            /* Main Container Padding */
            .block-container {
                padding-top: 1.8rem;
                padding-bottom: 3rem;
                max-width: 1200px;
            }

            /* Header Banner Styling */
            .jarvis-header {
                background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 50%, rgba(236, 72, 153, 0.15) 100%);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 24px 30px;
                margin-bottom: 25px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
            }
            
            .jarvis-title {
                font-size: 2.2rem;
                font-weight: 700;
                background: linear-gradient(90deg, #818cf8, #c084fc, #f472b6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0 0 6px 0;
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .jarvis-subtitle {
                color: #94a3b8;
                font-size: 0.95rem;
                font-weight: 400;
                margin: 0;
            }

            /* Status Badges */
            .badge-container {
                display: flex;
                gap: 10px;
                margin-top: 12px;
                flex-wrap: wrap;
            }

            .badge {
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.12);
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.8rem;
                color: #cbd5e1;
                display: flex;
                align-items: center;
                gap: 6px;
            }

            .status-dot {
                width: 8px;
                height: 8px;
                background-color: #10b981;
                border-radius: 50%;
                box-shadow: 0 0 8px #10b981;
            }

            /* Sidebar Styling */
            section[data-testid="stSidebar"] {
                background-color: #0f172a;
                border-right: 1px solid rgba(255, 255, 255, 0.08);
            }

            .sidebar-card {
                background: rgba(30, 41, 59, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 16px;
                margin-top: 15px;
            }

            .sidebar-card-title {
                font-size: 0.85rem;
                font-weight: 600;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 10px;
            }

            /* Welcome Hero Card for Empty State */
            .welcome-hero {
                background: rgba(30, 41, 59, 0.4);
                border: 1px dashed rgba(255, 255, 255, 0.15);
                border-radius: 16px;
                padding: 35px;
                text-align: center;
                margin: 20px 0 30px 0;
            }

            .welcome-icon {
                font-size: 3rem;
                margin-bottom: 12px;
            }

            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 25px;
                text-align: left;
            }

            .feature-card {
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 14px 18px;
                transition: transform 0.2s ease, border-color 0.2s ease;
            }

            .feature-card:hover {
                transform: translateY(-2px);
                border-color: rgba(99, 102, 241, 0.4);
            }

            .feature-title {
                font-weight: 600;
                color: #e2e8f0;
                font-size: 0.9rem;
                margin-bottom: 4px;
            }

            .feature-desc {
                font-size: 0.8rem;
                color: #94a3b8;
            }

            /* File Tag styling */
            .file-tag {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: rgba(99, 102, 241, 0.2);
                border: 1px solid rgba(99, 102, 241, 0.4);
                color: #c7d2fe;
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 0.82rem;
                margin-bottom: 8px;
            }

            /* Hide standard top header line padding */
            header[data-testid="stHeader"] {
                background: transparent;
            }
        </style>
        """, unsafe_allow_html=True)

def header():
    return st.markdown("""
            <div class="jarvis-header">
                <div class="jarvis-title">
                    <span>🤖</span> Jarvis AI Workspace
                </div>
                <div class="jarvis-subtitle">
                    Your intelligent multimodal assistant for conversation, document intelligence, and image recognition.
                </div>
                <div class="badge-container">
                    <div class="badge"><div class="status-dot"></div> Online</div>
                    <div class="badge">⚡ LLaMA 3.3 70B Versatile</div>
                    <div class="badge">📄 RAG (PDF, DOCX, TXT)</div>
                    <div class="badge">👁️ Vision Classifier</div>
                </div>
            </div>
            """, unsafe_allow_html=True)