"""
MediVault AI Agent - Streamlit Application
HIPAA-aware claims automation assistant with chat interface.
"""

import streamlit as st
import os
import sys
from pathlib import Path
import tempfile
import logging
from datetime import datetime
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import application modules
from core.parsing import parse_document
from core.extraction import DataExtractor
from core.coding import MedicalCodingAssistant
from cms1500.generator import CMS1500Generator
from cms1500.rules import CMS1500Validator
from cms1500.render import CMS1500Renderer
from security.auth import get_auth_manager, Role
from security.audit import get_audit_logger
from security.policy import get_policy_manager, ConsentType
from llm.ollama import OllamaClient, verify_ollama

# Page configuration
st.set_page_config(
    page_title="MediVault AI Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 1rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'extracted_data' not in st.session_state:
        st.session_state.extracted_data = None
    if 'coding_result' not in st.session_state:
        st.session_state.coding_result = None
    if 'claim' not in st.session_state:
        st.session_state.claim = None
    if 'consent_given' not in st.session_state:
        st.session_state.consent_given = False


def login_page():
    """Display login page"""
    st.markdown('<div class="main-header">🏥 MediVault AI Agent</div>', unsafe_allow_html=True)
    st.markdown("### Secure Claims Automation Assistant")
    
    st.info("🔒 **HIPAA-Compliant Local Processing** - All data processed locally with no external APIs")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True):
            auth_manager = get_auth_manager()
            user = auth_manager.authenticate(username, password)
            
            if user:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user = user
                
                # Log authentication
                audit_logger = get_audit_logger()
                audit_logger.log_authentication(username, success=True)
                
                st.success("Login successful!")
                st.rerun()
            else:
                # Log failed attempt
                audit_logger = get_audit_logger()
                audit_logger.log_authentication(username, success=False)
                
                st.error("Invalid credentials")
        
        with st.expander("ℹ️ Default Credentials"):
            st.write("Username: `admin`")
            st.write("Password: `admin`")
            st.warning("**Change default credentials in production!**")


def sidebar():
    """Display sidebar with settings and controls"""
    st.sidebar.markdown("## 🏥 MediVault AI Agent")
    st.sidebar.markdown(f"**User:** {st.session_state.username}")
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # System status
    st.sidebar.markdown("### System Status")
    
    # Check Ollama
    ollama_status = verify_ollama()
    if ollama_status["ollama_available"]:
        st.sidebar.success("✅ Ollama Connected")
        st.sidebar.write(f"Models: {len(ollama_status['models'])}")
    else:
        st.sidebar.error("❌ Ollama Not Available")
        st.sidebar.write(ollama_status.get("error", "Unknown error"))
    
    st.sidebar.markdown("---")
    
    # Settings
    st.sidebar.markdown("### Settings")
    
    use_llm = st.sidebar.checkbox("Enable LLM Enhancement", value=True)
    use_vision = st.sidebar.checkbox("Enable Vision OCR Fallback", value=False)
    phi_minimization = st.sidebar.select_slider(
        "PHI Minimization",
        options=["None", "Minimum", "Maximum"],
        value="Minimum"
    )
    
    return {
        "use_llm": use_llm,
        "use_vision": use_vision,
        "phi_minimization": phi_minimization
    }


def consent_dialog():
    """Display consent dialog for PHI processing"""
    if not st.session_state.consent_given:
        st.warning("⚠️ **Consent Required**")
        
        with st.expander("📋 Review Consent Information", expanded=True):
            st.markdown("""
            ### PHI Processing Consent
            
            This application will process Protected Health Information (PHI) for the following purposes:
            
            - **Treatment**: Extract clinical information for care coordination
            - **Payment**: Generate CMS-1500 claims for billing
            - **Operations**: Analyze and suggest medical codes
            - **LLM Processing**: Use local AI models to enhance data extraction
            
            **Your Privacy:**
            - All processing is performed **locally** on this machine
            - No data is sent to external servers or APIs
            - Data is encrypted at rest
            - Access is logged for audit purposes
            - You can revoke consent at any time
            
            **Data Retention:**
            - Records are retained for 90 days by default
            - You can request deletion at any time
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ I Consent", use_container_width=True):
                    st.session_state.consent_given = True
                    
                    # Log consent
                    policy_manager = get_policy_manager()
                    policy_manager.record_consent(
                        st.session_state.username,
                        ConsentType.LLM_PROCESSING,
                        granted=True
                    )
                    
                    audit_logger = get_audit_logger()
                    audit_logger.log_consent(
                        st.session_state.username,
                        "llm_processing",
                        granted=True
                    )
                    
                    st.rerun()
            
            with col2:
                if st.button("❌ Decline", use_container_width=True):
                    st.error("Consent is required to use this application.")
        
        return False
    
    return True


def document_upload_section(settings):
    """Document upload and processing section"""
    st.markdown('<div class="sub-header">📄 Document Upload</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload medical document (PDF, Image, or Text)",
        type=['pdf', 'png', 'jpg', 'jpeg', 'txt'],
        help="Supported formats: PDF, PNG, JPG, JPEG, TXT"
    )
    
    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")
        
        if st.button("🔍 Process Document", use_container_width=True):
            with st.spinner("Processing document..."):
                try:
                    # Save temp file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    
                    # Parse document
                    st.info("📖 Parsing document...")
                    parsed = parse_document(tmp_path)
                    
                    # Extract data
                    st.info("🔍 Extracting structured data...")
                    extractor = DataExtractor(use_llm=settings['use_llm'])
                    extracted = extractor.extract(parsed['text'])
                    
                    # Medical coding
                    st.info("🩺 Analyzing medical codes...")
                    coding_assistant = MedicalCodingAssistant(use_llm=settings['use_llm'])
                    coding_result = coding_assistant.suggest_codes(
                        parsed['text'],
                        extracted.diagnoses,
                        extracted.procedures
                    )
                    
                    # Store in session
                    st.session_state.extracted_data = extracted
                    st.session_state.coding_result = coding_result
                    
                    # Log access
                    audit_logger = get_audit_logger()
                    audit_logger.log_access(
                        st.session_state.username,
                        f"document:{uploaded_file.name}",
                        access_type="process"
                    )
                    
                    # Cleanup
                    os.unlink(tmp_path)
                    
                    st.success("✅ Document processed successfully!")
                    
                except Exception as e:
                    st.error(f"Error processing document: {str(e)}")
                    logger.error(f"Document processing error: {e}", exc_info=True)


def extracted_data_section():
    """Display extracted data"""
    if not st.session_state.extracted_data:
        return
    
    st.markdown('<div class="sub-header">📊 Extracted Data</div>', unsafe_allow_html=True)
    
    extracted = st.session_state.extracted_data
    
    tabs = st.tabs(["Patient Info", "Insurance", "Provider", "Diagnoses", "Procedures"])
    
    with tabs[0]:
        if extracted.patient:
            patient_data = extracted.patient.model_dump()
            st.json(patient_data)
        else:
            st.warning("No patient data extracted")
    
    with tabs[1]:
        if extracted.insurance:
            insurance_data = extracted.insurance.model_dump()
            st.json(insurance_data)
        else:
            st.warning("No insurance data extracted")
    
    with tabs[2]:
        if extracted.provider:
            provider_data = extracted.provider.model_dump()
            st.json(provider_data)
        else:
            st.warning("No provider data extracted")
    
    with tabs[3]:
        if extracted.diagnoses:
            for dx in extracted.diagnoses:
                st.write(f"**{dx.code}**: {dx.description or 'N/A'} (confidence: {dx.confidence:.2f})")
        else:
            st.warning("No diagnoses extracted")
    
    with tabs[4]:
        if extracted.procedures:
            for proc in extracted.procedures:
                st.write(f"**{proc.code}**: {proc.description or 'N/A'} (confidence: {proc.confidence:.2f})")
        else:
            st.warning("No procedures extracted")


def coding_section():
    """Display medical coding results"""
    if not st.session_state.coding_result:
        return
    
    st.markdown('<div class="sub-header">🩺 Medical Coding</div>', unsafe_allow_html=True)
    
    coding = st.session_state.coding_result
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Diagnosis Codes")
        for dx in coding.diagnoses:
            with st.expander(f"{dx.code} - {dx.description}"):
                st.write(f"**Rationale:** {dx.rationale}")
                st.write(f"**Confidence:** {dx.confidence:.1%}")
                st.write(f"**Letter:** {coding.diagnosis_letters.get(dx.code, 'N/A')}")
    
    with col2:
        st.markdown("#### Procedure Codes")
        for proc in coding.procedures:
            with st.expander(f"{proc.code} - {proc.description}"):
                st.write(f"**Rationale:** {proc.rationale}")
                st.write(f"**Confidence:** {proc.confidence:.1%}")
                
                # Show diagnosis pointers
                if proc.metadata and 'diagnosis_pointers' in proc.metadata:
                    pointers = proc.metadata['diagnosis_pointers']
                    st.write(f"**Diagnosis Pointers:** {', '.join(pointers)}")
    
    # Validation issues
    if coding.mismatches:
        st.markdown("#### ⚠️ Validation Issues")
        for mismatch in coding.mismatches:
            if mismatch.severity == "error":
                st.error(f"**Error:** {mismatch.message}")
            elif mismatch.severity == "warning":
                st.warning(f"**Warning:** {mismatch.message}")
            else:
                st.info(f"**Info:** {mismatch.message}")
            
            if mismatch.suggestion:
                st.write(f"💡 {mismatch.suggestion}")


def cms1500_section():
    """Generate and display CMS-1500 claim"""
    st.markdown('<div class="sub-header">📋 CMS-1500 Claim</div>', unsafe_allow_html=True)
    
    if not st.session_state.extracted_data or not st.session_state.coding_result:
        st.info("Complete document processing and coding first to generate claim.")
        return
    
    if st.button("🔨 Generate CMS-1500 Claim"):
        with st.spinner("Generating claim..."):
            try:
                generator = CMS1500Generator()
                claim = generator.create_claim(
                    extracted_data=st.session_state.extracted_data,
                    coding_result=st.session_state.coding_result
                )
                
                st.session_state.claim = claim
                st.success("✅ Claim generated!")
                
            except Exception as e:
                st.error(f"Error generating claim: {str(e)}")
                logger.error(f"Claim generation error: {e}", exc_info=True)
    
    # Display claim
    if st.session_state.claim:
        claim = st.session_state.claim
        
        # Validate
        validator = CMS1500Validator()
        validation_result = validator.validate(claim)
        
        # Show validation status
        if validation_result.valid:
            st.success(f"✅ Claim is valid ({validation_result.warnings_count} warnings)")
        else:
            st.error(f"❌ Claim has {validation_result.errors_count} errors")
        
        # Display validation messages
        if validation_result.messages:
            with st.expander(f"📝 Validation Messages ({len(validation_result.messages)})"):
                for msg in validation_result.messages:
                    if msg.severity == "error":
                        st.error(f"**Field {msg.field}:** {msg.message}")
                    elif msg.severity == "warning":
                        st.warning(f"**Field {msg.field}:** {msg.message}")
                    else:
                        st.info(f"**Field {msg.field}:** {msg.message}")
                    
                    if msg.suggestion:
                        st.write(f"💡 {msg.suggestion}")
        
        # Render claim
        renderer = CMS1500Renderer()
        rendered = renderer.render_for_display(claim)
        
        # Display claim fields
        tabs = st.tabs(["Overview", "Patient", "Insurance", "Diagnoses", "Services", "Provider"])
        
        with tabs[0]:
            st.metric("Total Charge", rendered['totals']['total_charge'])
            st.metric("Confidence", f"{st.session_state.coding_result.overall_confidence:.1%}")
        
        with tabs[1]:
            st.json(rendered['patient_info'])
        
        with tabs[2]:
            st.json(rendered['insurance_info'])
        
        with tabs[3]:
            for dx in rendered['diagnoses']:
                st.write(f"**{dx['letter']}:** {dx['code']}")
        
        with tabs[4]:
            for line in rendered['service_lines']:
                st.write(f"**Line {line['line_number']}:** {line['cpt_hcpcs']} - {line['charges']}")
        
        with tabs[5]:
            st.json(rendered['provider_info']['billing_provider'])
        
        # Export options
        st.markdown("#### Export")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export as JSON"):
                json_data = claim.model_dump_json(indent=2)
                st.download_button(
                    "Download JSON",
                    json_data,
                    file_name=f"claim_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )


def chat_interface():
    """Chat interface for questions and assistance"""
    st.markdown('<div class="sub-header">💬 AI Assistant</div>', unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about claims, codes, or processing..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    client = OllamaClient()
                    
                    # Build context
                    messages = [{"role": msg["role"], "content": msg["content"]} 
                               for msg in st.session_state.chat_history]
                    
                    result = client.chat(messages=messages)
                    response = result.get("message", {}).get("content", "Sorry, I couldn't generate a response.")
                    
                    st.write(response)
                    
                    # Add to history
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    logger.error(f"Chat error: {e}", exc_info=True)


def main_app():
    """Main application interface"""
    settings = sidebar()
    
    # Consent check
    if not consent_dialog():
        return
    
    # Main content
    st.markdown('<div class="main-header">🏥 MediVault AI Agent</div>', unsafe_allow_html=True)
    st.markdown("### HIPAA-Compliant Claims Automation Assistant")
    
    # Layout
    col_left, col_right = st.columns([2, 3])
    
    with col_left:
        document_upload_section(settings)
        st.markdown("---")
        chat_interface()
    
    with col_right:
        extracted_data_section()
        st.markdown("---")
        coding_section()
        st.markdown("---")
        cms1500_section()


def main():
    """Main entry point"""
    initialize_session_state()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        main_app()


if __name__ == "__main__":
    main()
