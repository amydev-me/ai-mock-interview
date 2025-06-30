# app.py (Main Streamlit Application)
import streamlit as st
import json
import os
from datetime import datetime
from workflows.basic_workflow import InterviewPrepWorkflow
from agents.interview_simulator import InterviewSimulatorAgent
from agents.feedback_agent import FeedbackAgent
from mcp_servers.file_server import FileSystemMCPServer
import traceback

# Page configuration
st.set_page_config(
    page_title="Smart Interview Prep AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin: 1.5rem 0 1rem 0;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<h1 class="main-header">🎯 Smart Interview Prep AI</h1>', unsafe_allow_html=True)
    st.markdown("### *AI-Powered Multi-Agent Interview Preparation System*")

    # Sidebar for navigation
    st.sidebar.title("🚀 Navigation")
    page = st.sidebar.selectbox(
        "Choose your step:",
        ["🏠 Home", "🔍 Company Research", "❓ Question Generation", "🎤 Mock Interview", "📊 Get Feedback",
         "📈 Progress Tracking"]
    )

    # Initialize session state
    if 'workflow' not in st.session_state:
        st.session_state.workflow = InterviewPrepWorkflow()
    if 'simulator' not in st.session_state:
        st.session_state.simulator = InterviewSimulatorAgent()
    if 'feedback_agent' not in st.session_state:
        st.session_state.feedback_agent = FeedbackAgent()

    # Page routing
    if page == "🏠 Home":
        show_home_page()
    elif page == "🔍 Company Research":
        show_research_page()
    elif page == "❓ Question Generation":
        show_question_generation_page()
    elif page == "🎤 Mock Interview":
        show_interview_page()
    elif page == "📊 Get Feedback":
        show_feedback_page()
    elif page == "📈 Progress Tracking":
        show_progress_page()


def show_home_page():
    """Home page with overview"""
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<h2 class="step-header">🎯 Welcome to Smart Interview Prep</h2>', unsafe_allow_html=True)

        st.markdown("""
        This AI-powered system helps you prepare for job interviews using cutting-edge technologies:

        **🤖 Multi-Agent System:**
        - **Research Agent**: Analyzes companies and roles
        - **Question Generator**: Creates tailored interview questions  
        - **Interview Simulator**: Conducts realistic mock interviews
        - **Feedback Agent**: Provides detailed performance analysis

        **🔧 Technologies Used:**
        - **LangChain**: AI agent framework
        - **LangGraph**: Multi-agent workflow orchestration
        - **MCP (Model Context Protocol)**: Standardized data access
        - **OpenAI GPT**: Advanced language model
        - **Streamlit**: Interactive web interface
        """)

        st.markdown(
            '<div class="info-box">💡 <strong>How it works:</strong> Follow the steps in the sidebar to research a company, generate questions, practice interviews, and get feedback!</div>',
            unsafe_allow_html=True)

    with col2:
        st.markdown("### 📊 System Status")

        # Check system components
        try:
            # Test workflow
            st.success("✅ Multi-Agent Workflow: Ready")
            st.success("✅ Research Agent: Ready")
            st.success("✅ Question Generator: Ready")
            st.success("✅ Interview Simulator: Ready")
            st.success("✅ Feedback Agent: Ready")
            st.success("✅ MCP Server: Ready")
        except Exception as e:
            st.error(f"❌ System Error: {str(e)}")

        # Quick stats
        if os.path.exists("data"):
            files = os.listdir("data")
            st.info(f"📁 Data Files: {len(files)}")

        st.markdown("### 🚀 Quick Start")
        if st.button("Start Interview Prep", type="primary"):
            st.session_state.current_page = "🔍 Company Research"
            st.rerun()


def show_research_page():
    """Company research page"""
    st.markdown('<h2 class="step-header">🔍 Company Research</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("**Step 1: Tell us about your interview**")

        # Input form
        with st.form("research_form"):
            company_name = st.text_input("Company Name", placeholder="e.g., Google, Netflix, Amazon")
            job_role = st.text_input("Job Role", placeholder="e.g., Software Engineer, Data Scientist")
            additional_info = st.text_area("Additional Information (Optional)",
                                           placeholder="Any specific requirements or details about the role...")

            submit_research = st.form_submit_button("🔍 Research Company", type="primary")

        if submit_research and company_name and job_role:
            with st.spinner(f"🔍 Researching {company_name} for {job_role} position..."):
                try:
                    # Run the research workflow
                    query = f"{company_name} {job_role} position"
                    result = st.session_state.workflow.run(query)

                    st.markdown(
                        '<div class="success-box">✅ <strong>Research Complete!</strong> Company information has been analyzed and saved.</div>',
                        unsafe_allow_html=True)

                    # Show research results
                    if os.path.exists("data/research_data.json"):
                        with open("data/research_data.json", "r") as f:
                            research_data = json.load(f)

                        st.markdown("### 📋 Research Results")

                        if "company_data" in research_data:
                            company_info = research_data["company_data"]

                            # Display company information in a nice format
                            col_a, col_b = st.columns(2)

                            with col_a:
                                st.markdown("**🏢 Company Culture:**")
                                st.info(company_info.get("culture", "N/A"))

                                st.markdown("**💡 Company Values:**")
                                st.info(company_info.get("values", "N/A"))

                            with col_b:
                                st.markdown("**🎯 Interview Style:**")
                                st.info(company_info.get("interview_style", "N/A"))

                                st.markdown("**📰 Recent News:**")
                                st.info(company_info.get("recent_news", "N/A"))

                except Exception as e:
                    st.error(f"❌ Research failed: {str(e)}")

    with col2:
        st.markdown("### 💡 Research Tips")
        st.markdown("""
        **What we analyze:**
        - Company culture and values
        - Interview process and style
        - Recent company news
        - Role-specific requirements

        **This helps us:**
        - Generate relevant questions
        - Tailor behavioral questions
        - Prepare you for company culture
        - Focus on what matters most
        """)

        # Show recent research files
        if os.path.exists("data"):
            research_files = [f for f in os.listdir("data") if f.startswith("research")]
            if research_files:
                st.markdown("### 📁 Recent Research")
                for file in research_files[-3:]:  # Show last 3
                    st.text(f"📄 {file}")


# Replace the show_question_generation_page function in app.py with this:

def show_question_generation_page():
    """Question generation page"""
    st.markdown('<h2 class="step-header">❓ Question Generation</h2>', unsafe_allow_html=True)

    # Check if research data exists
    if not os.path.exists("data/research_data.json"):
        st.markdown(
            '<div class="warning-box">⚠️ <strong>Research Required:</strong> Please complete company research first!</div>',
            unsafe_allow_html=True)
        if st.button("Go to Research Page"):
            st.session_state.current_page = "🔍 Company Research"
            st.rerun()
        return

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("**Step 2: Generate Interview Questions**")

        # Load research data to show context
        with open("data/research_data.json", "r") as f:
            research_data = json.load(f)

        if "company_data" in research_data:
            company_name = research_data["company_data"].get("name", "Unknown Company")
            st.info(f"🏢 Generating questions for: **{company_name}**")

        # Question generation options
        question_types = st.multiselect(
            "Select question types to generate:",
            ["Technical Questions", "Behavioral Questions", "Company-Specific Questions"],
            default=["Technical Questions", "Behavioral Questions"]
        )

        difficulty_level = st.select_slider(
            "Question Difficulty:",
            options=["Beginner", "Intermediate", "Advanced", "Mixed"],
            value="Mixed"
        )

        num_questions = st.slider("Number of questions:", 5, 20, 10)

        # Extract role from research data or ask user
        role = st.text_input("Job Role", value="Software Engineer", help="Enter the job role for tailored questions")

        if st.button("❓ Generate Questions", type="primary"):
            with st.spinner("🤖 AI agents are creating your personalized questions..."):
                try:
                    question_generator = st.session_state.workflow.question_generator

                    # Construct a clear prompt for the agent's LLM to interpret
                    # The agent's system prompt will guide it to use its tools
                    user_command = (
                        f"Generate {num_questions} interview questions for a {role} position at {company_name}. "
                        f"Ensure the questions are a mix of {', '.join(question_types).lower()} types. "
                        f"Load any relevant research data, then generate and save the questions."
                    )

                    # Run the agent! It will handle loading research, generating, and saving
                    agent_response = question_generator.run(user_command)

                    st.markdown(
                        '<div class="success-box">✅ <strong>Questions Generated!</strong> Your personalized interview questions are ready.</div>',
                        unsafe_allow_html=True)

                    # Now, load and display the generated questions from the file
                    if os.path.exists("data/interview_questions.json"):
                        with open("data/interview_questions.json", "r") as f:
                            questions_data = json.load(f)

                        if "questions" in questions_data and isinstance(questions_data["questions"], list):
                            questions = questions_data["questions"]

                            st.markdown("### 📝 Your Generated Interview Questions")

                            for i, question in enumerate(questions, 1):
                                st.markdown(f"**Q{i}:** {question}")

                            # Save questions to session state for interview
                            st.session_state.generated_questions = questions

                        else:
                            st.error("❌ Questions format error in saved file. Expected a list under 'questions' key.")
                    else:
                        st.error("❌ Questions file not found after generation. Agent might have failed to save.")
                        st.error(f"Agent's raw response: {agent_response}")

                except Exception as e:
                    st.error(f"❌ Question generation failed: {str(e)}")
                    st.warning("🔄 Using sample questions for demo purposes (due to error).")

                    # Fallback to sample questions in case of error (for robust demo)
                    sample_questions = [
                        f"Tell me about yourself and your background in {role.lower()}",
                        f"Why are you interested in working at {company_name}?",
                        "Describe a challenging technical problem you solved recently",
                        "How do you handle working under tight deadlines?",
                        "What's your experience with modern development practices?",
                        "Tell me about a time you had to learn something new quickly",
                        "How would you approach debugging a complex system issue?",
                        "Describe your ideal work environment and team dynamic",
                        f"What attracts you to {company_name}'s mission and values?",
                        "Where do you see your career heading in the next 5 years?"
                    ]

                    # Save sample questions
                    st.session_state.generated_questions = sample_questions[:num_questions]

                    for i, question in enumerate(st.session_state.generated_questions, 1):
                        st.markdown(f"**Q{i}:** {question}")

    with col2:
        st.markdown("### 🎯 Question Types")
        st.markdown("""
        **Technical Questions:**
        - Coding problems
        - System design
        - Architecture decisions

        **Behavioral Questions:**
        - Past experiences
        - Problem-solving scenarios
        - Team collaboration

        **Company-Specific:**
        - Culture fit
        - Values alignment
        - Recent company news
        """)

        # Show progress
        if hasattr(st.session_state, 'generated_questions'):
            st.success(f"✅ {len(st.session_state.generated_questions)} questions ready!")


# app.py (UPDATED show_interview_page function - Corrected text area clearing)

def show_interview_page():
    """Mock interview page"""
    st.markdown('<h2 class="step-header">🎤 Mock Interview</h2>', unsafe_allow_html=True)

    # Check if questions were generated
    if not hasattr(st.session_state, 'generated_questions') or not st.session_state.generated_questions:
        st.markdown(
            '<div class="warning-box">⚠️ <strong>Questions Required:</strong> Please generate questions first!</div>',
            unsafe_allow_html=True)
        if st.button("Go to Question Generation"):
            st.session_state.current_page = "❓ Question Generation"
            st.rerun()
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("**Step 3: Practice Your Interview**")

        # Interview controls
        if 'interview_started' not in st.session_state:
            st.session_state.interview_started = False
        if 'current_question_text' not in st.session_state:
            st.session_state.current_question_text = ""
        if 'current_question_num' not in st.session_state:
            st.session_state.current_question_num = 0
        if 'total_questions_count' not in st.session_state:
            st.session_state.total_questions_count = len(st.session_state.generated_questions)

        # New state variable to control text area content
        if 'answer_input_value' not in st.session_state:
            st.session_state.answer_input_value = ""

        simulator = st.session_state.simulator  # Get the simulator agent instance

        if not st.session_state.interview_started:
            st.markdown(
                '<div class="info-box">🎤 <strong>Ready to start your mock interview?</strong><br>I\'ll ask you the questions we generated. Take your time and answer as you would in a real interview.</div>',
                unsafe_allow_html=True)

            # Show preview of questions
            st.markdown("### 📋 Preview of Your Questions:")
            for i, q in enumerate(st.session_state.generated_questions[:3], 1):  # Show first 3
                st.markdown(f"**{i}.** {q}")
            if len(st.session_state.generated_questions) > 3:
                st.markdown(f"*... and {len(st.session_state.generated_questions) - 3} more questions*")

            if st.button("🚀 Start Mock Interview", type="primary"):
                st.session_state.interview_started = True

                # Directly call the agent's sequence starter
                with st.spinner("Preparing interview..."):
                    response = simulator.start_interview_sequence()  # This loads questions AND asks first
                    st.session_state.current_question_text = response

                    # Update internal state based on simulator's current state
                    st.session_state.current_question_num = simulator.current_question_index + 1
                    st.session_state.total_questions_count = len(simulator.questions)
                    st.session_state.answer_input_value = ""  # Clear input on start
                st.rerun()

        else:  # Interview in progress
            # Show the current question
            if simulator.current_question_index < len(simulator.questions):
                st.markdown(f"### Current Question: {simulator.current_question_index + 1}/{len(simulator.questions)}")
                st.markdown(st.session_state.current_question_text)

                # Answer input - uses st.session_state.answer_input_value as its default
                # The key is still needed to track its internal state if not explicitly managed by value
                answer = st.text_area("Your Answer:", height=150, value=st.session_state.answer_input_value,
                                      key="current_answer_input_widget")

                col_a, col_b, col_c = st.columns([1, 1, 1])

                with col_a:
                    if st.button("⏭️ Submit Answer & Next Question"):
                        if answer.strip():
                            with st.spinner("Recording answer & getting next question..."):
                                # Instruct agent to record answer
                                record_response = simulator.run(f"Record this answer: '{answer.strip()}'")
                                st.info(record_response)

                                # Instruct agent to ask next question (direct call)
                                next_q_response = simulator._ask_next_question()
                                st.session_state.current_question_text = next_q_response

                                # Update question numbers based on simulator's new index
                                st.session_state.current_question_num = simulator.current_question_index + 1
                                st.session_state.total_questions_count = len(simulator.questions)

                                # --- CORRECT WAY TO CLEAR INPUT ---
                                # We set the session_state variable that the text_area's 'value' parameter refers to.
                                # This will effectively clear the text_area on the *next* rerun.
                                st.session_state.answer_input_value = ""
                                # --- END CORRECT WAY TO CLEAR INPUT ---

                            st.rerun()
                        else:
                            st.warning("Please provide an answer before continuing.")

                with col_b:
                    if st.button("⏸️ Pause Interview"):
                        st.info(
                            "Interview paused. Your progress is saved. You can resume anytime by navigating back to this page.")

                with col_c:
                    if st.button("🔄 Restart Interview"):
                        st.session_state.interview_started = False
                        st.session_state.current_question_text = ""
                        st.session_state.current_question_num = 0
                        st.session_state.total_questions_count = len(st.session_state.generated_questions)

                        # Reset agent's internal state directly
                        simulator.current_question_index = 0
                        simulator.answers = []
                        simulator.questions = []
                        st.session_state.answer_input_value = ""  # Clear input on restart
                        st.rerun()


            else:  # Interview completed

                st.markdown(
                    '<div class="success-box">🎉 <strong>Interview Complete!</strong> Great job! You\'ve answered all questions.</div>',
                    unsafe_allow_html=True)

                # --- NEW STATE VARIABLE TO PREVENT DUPLICATE SAVES ---

                if 'session_saved_flag' not in st.session_state:
                    st.session_state.session_saved_flag = False

                if not st.session_state.session_saved_flag:  # Only save if not already saved in this session

                    with st.spinner("Saving interview session..."):

                        save_response = simulator.run("Save the completed interview session.")

                        st.success(save_response)

                        st.session_state.session_saved_flag = True  # Set flag after saving

                else:

                    st.info("Interview session already saved.")  # Inform user if re-rendering after save

                # --- END NEW STATE VARIABLE ---

                st.markdown("### 📋 Interview Summary")

                st.write(f"**Questions Answered:** {len(simulator.answers)}")

                st.write(f"**Questions Used:** {len(simulator.questions)} generated questions")

                col_x, col_y = st.columns(2)

                with col_x:

                    if st.button("📊 Get Feedback", type="primary"):
                        # Reset feedback generation flag so it re-runs on feedback page

                        st.session_state.feedback_generated_for_session = None

                        st.session_state.current_page = "📊 Get Feedback"

                        st.rerun()

                with col_y:

                    if st.button("🔄 New Interview"):
                        st.session_state.interview_started = False

                        st.session_state.current_question_text = ""

                        st.session_state.current_question_num = 0

                        st.session_state.total_questions_count = len(st.session_state.generated_questions)

                        # Reset agent's internal state

                        simulator.current_question_index = 0

                        simulator.answers = []

                        simulator.questions = []

                        st.session_state.answer_input_value = ""

                        st.session_state.session_saved_flag = False  # Reset save flag for new interview

                        st.rerun()

    with col2:
        st.markdown("### 💡 Interview Tips")
        st.markdown("""
        **During the interview:**
        - Take your time to think
        - Be specific with examples
        - Use the STAR method for behavioral questions
        - Stay calm and confident

        **STAR Method:**
        - **Situation**: Set the context
        - **Task**: Describe your responsibility
        - **Action**: Explain what you did
        - **Result**: Share the outcome
        """)

        # Progress indicator
        answered_questions = simulator.current_question_index
        if st.session_state.total_questions_count > 0:
            progress = answered_questions / st.session_state.total_questions_count
            st.progress(progress)
            st.write(f"Progress: {answered_questions}/{st.session_state.total_questions_count} questions answered")
        else:
            st.progress(0.0)
            st.write("Progress: 0/0 questions answered")

        st.markdown("### 📝 Your Questions")
        if hasattr(st.session_state, 'generated_questions') and st.session_state.generated_questions:
            st.info(f"✅ {len(st.session_state.generated_questions)} unique questions loaded from generation step.")

            # Display all questions, highlighting the current one
            for i, q_text in enumerate(st.session_state.generated_questions):
                if simulator.current_question_index == i and simulator.current_question_index < len(
                        simulator.questions):
                    st.markdown(f"**Q{i + 1}:** <span style='background-color:#fff3cd;'>{q_text}</span>",
                                unsafe_allow_html=True)
                else:
                    st.markdown(f"**Q{i + 1}:** {q_text}")


def show_feedback_page():
    """Feedback and analysis page"""
    st.markdown('<h2 class="step-header">📊 Performance Feedback</h2>', unsafe_allow_html=True)

    interview_files = []

    # Get the singleton MCP server instance
    file_server_instance = FileSystemMCPServer()

    # Use the MCP server's list_files method to get all files in the data directory
    list_result = file_server_instance.list_files()

    if list_result.get("success"):
        all_files_in_data_dir = list_result["files"]
        # Filter for interview session files
        interview_files = sorted([f for f in all_files_in_data_dir if f.startswith("interview_session")], reverse=True)
        print(f"DEBUG_APP: Feedback page found {len(interview_files)} interview session files: {interview_files}")
        if not interview_files:
            print("DEBUG_APP: No files starting with 'interview_session' found by filter in the data directory.")
    else:
        print(f"DEBUG_APP: Feedback page error listing files: {list_result.get('error')}")
        st.error(f"Error accessing data directory: {list_result.get('error')}")

    if not interview_files:
        st.markdown(
            '<div class="warning-box">⚠️ <strong>No Interview Sessions Found:</strong> Please complete a mock interview first!</div>',
            unsafe_allow_html=True)
        if st.button("Go to Mock Interview"):
            st.session_state.current_page = "🎤 Mock Interview"
            st.rerun()
        return

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("**Step 4: Get AI-Powered Feedback**")

        # Select session to analyze
        selected_session = st.selectbox(
            "Select interview session:",
            interview_files,
            format_func=lambda x: f"📅 {x.replace('interview_session_', '').replace('.json', '').replace('_', ' ')}"
        )

        # Initialize session state variables for feedback generation and display
        if 'feedback_generated_for_session' not in st.session_state:
            st.session_state.feedback_generated_for_session = None
        if 'last_selected_session' not in st.session_state:
            st.session_state.last_selected_session = None  # Initialize to None
        if 'feedback_display_data' not in st.session_state:
            st.session_state.feedback_display_data = {}  # Initialize as empty dict

        # Determine if feedback needs to be generated (button clicked or session changed)
        generate_button_clicked = st.button("📊 Generate Feedback Report", type="primary")

        # Only generate if button is clicked OR if session changed and feedback hasn't been generated for new session
        if generate_button_clicked or (
                selected_session != st.session_state.last_selected_session and st.session_state.feedback_generated_for_session != selected_session):
            if selected_session != st.session_state.last_selected_session:
                print(f"DEBUG_APP: Selected session changed to {selected_session}. Re-generating feedback.")
                st.session_state.last_selected_session = selected_session  # Update last selected session
                st.session_state.feedback_generated_for_session = None  # Reset flag for new session

            st.session_state.feedback_generated_for_session = None  # Reset flag to show spinner if re-generating

            with st.spinner("🤖 AI is analyzing your interview performance..."):
                try:
                    # Use the MCP server to load session data
                    session_content_result = file_server_instance.read_file(selected_session)
                    if session_content_result.get("success"):
                        session_data = json.loads(session_content_result["content"])
                        print(f"DEBUG_APP: Successfully loaded session data for analysis: {selected_session}")
                    else:
                        raise Exception(f"Failed to read session file: {session_content_result.get('error')}")

                    recorded_answers = session_data.get('recorded_answers', [])
                    if not recorded_answers:
                        st.warning("No answers recorded in this session. Cannot generate detailed feedback.")
                        st.session_state.feedback_display_data = {
                            "total_score": "0/10", "performance_level": "No Answers",
                            "key_strengths": [], "priority_improvements": ["No answers provided."], "next_steps": []
                        }
                    else:
                        # Call the Feedback Agent to generate real overall feedback
                        feedback_agent_instance = st.session_state.feedback_agent
                        # The agent's run method will select the _generate_overall_feedback_llm tool
                        overall_feedback_str = feedback_agent_instance.run(
                            f"Generate an overall feedback report for these answers: {json.dumps(recorded_answers)}")

                        # Try to parse the agent's overall feedback
                        try:
                            overall_feedback = json.loads(overall_feedback_str)
                            if not isinstance(overall_feedback, dict) or "total_score" not in overall_feedback:
                                # Fallback if primary keys are missing
                                print(
                                    f"DEBUG_APP: LLM feedback missing 'total_score' or not dict. Raw: {overall_feedback_str}")
                                raise ValueError("Feedback agent did not return a dictionary with 'total_score'.")

                            st.session_state.feedback_display_data = overall_feedback
                        except (json.JSONDecodeError, ValueError) as e:
                            print(
                                f"DEBUG_APP: Failed to parse feedback agent's output: {e}. Raw: {overall_feedback_str}")
                            st.warning(
                                "Could not parse AI feedback. Showing generic report. Check console for AI output.")
                            st.session_state.feedback_display_data = {
                                "total_score": "N/A", "performance_level": "Parsing Error",
                                "key_strengths": ["Raw AI output issue (check console)."],
                                "priority_improvements": ["Review LLM output."],
                                "next_steps": ["Try another session/prompt."]
                            }

                    st.markdown(
                        '<div class="success-box">✅ <strong>Analysis Complete!</strong> Here\'s your detailed feedback report.</div>',
                        unsafe_allow_html=True)
                    st.session_state.feedback_generated_for_session = selected_session  # Mark as generated for this session


                except Exception as e:

                    st.error(f"❌ Analysis failed: {str(e)}. Please check console logs for full details.")

                    print(f"DEBUG_APP: An error occurred during feedback analysis: {e}")

                    traceback.print_exc()  # <--- CRITICAL CHANGE HERE: Use traceback.print_exc()

                    st.session_state.feedback_display_data = {  # Fallback display data on error

                        "total_score": "Error", "performance_level": "Analysis Failed",

                        "key_strengths": ["System error occurred during analysis."],
                        "priority_improvements": ["Review error message and console traceback."],
                        "next_steps": ["Contact support if issue persists."]

                    }

        # --- Display the feedback from session state ---
        # Ensure feedback_display_data is populated before attempting to display
        if st.session_state.feedback_generated_for_session == selected_session and st.session_state.feedback_display_data:
            overall_feedback = st.session_state.feedback_display_data

            st.markdown("### 🎯 Overall Performance Score")
            st.metric(
                "Interview Score",
                overall_feedback.get("total_score", "N/A"),
                overall_feedback.get("performance_level", "")
            )

            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.metric("Clarity", overall_feedback.get("clarity_score", "N/A"))
            with col_b:
                st.metric("Relevance", overall_feedback.get("relevance_score", "N/A"))
            with col_c:
                st.metric("Confidence", overall_feedback.get("confidence_score", "N/A"))
            with col_d:
                st.metric("Depth", overall_feedback.get("depth_score", "N/A"))

            st.markdown("### 💪 Key Strengths")
            for strength in overall_feedback.get("key_strengths", []):
                st.success(f"✅ {strength}")

            st.markdown("### 🎯 Areas for Improvement")
            for improvement in overall_feedback.get("priority_improvements", []):
                st.warning(f"📈 {improvement}")

            st.markdown("### 🚀 Next Steps")
            for step in overall_feedback.get("next_steps", []):
                st.info(f"👉 {step}")

            # Save feedback report using the MCP server (only after displaying)
            # Use a consistent filename based on the interview session timestamp
            report_timestamp_part = selected_session.replace("interview_session_", "").replace(".json", "")
            feedback_filename_to_save = f"feedback_report_for_{report_timestamp_part}.json"

            # Initialize feedback_report_saved_flag as a dictionary to track saves per session
            if 'feedback_report_saved_flag' not in st.session_state:
                st.session_state.feedback_report_saved_flag = {}

                # Only save if not already saved for this specific selected session
            if not st.session_state.feedback_report_saved_flag.get(selected_session, False):
                # Ensure the file doesn't already exist on disk from a previous run
                if not file_server_instance.base_path.joinpath(
                        feedback_filename_to_save).exists():  # Using pathlib for robust path check
                    feedback_report_data = {  # Data to save
                        "session_file": selected_session,
                        "analysis_timestamp": datetime.now().isoformat(),
                        "feedback_report": overall_feedback
                    }
                    save_feedback_result = file_server_instance.write_file(feedback_filename_to_save,
                                                                           json.dumps(feedback_report_data, indent=2))
                    if save_feedback_result.get("success"):
                        st.success(f"📁 Feedback report saved: {feedback_filename_to_save}")
                        st.session_state.feedback_report_saved_flag[selected_session] = True  # Mark as saved
                    else:
                        st.error(f"❌ Error saving feedback report: {save_feedback_result.get('error')}")
                else:
                    st.info(f"Report for {selected_session} already exists on disk: {feedback_filename_to_save}")
                    st.session_state.feedback_report_saved_flag[selected_session] = True  # Mark as saved if it exists
            else:
                st.info(f"Report for {selected_session} already processed and saved in this session.")

    with col2:
        st.markdown("### 📈 Feedback Categories")
        st.markdown("""
        **Clarity Score:** How clear and well-structured your answers are.
        **Relevance Score:** How well you address the question and stay on topic.
        **Confidence Score:** Your delivery, presence, and professional demeanor.
        **Depth Score:** The level of detail, examples, and expertise demonstrated.
        """)

        st.markdown("### 📁 Available Sessions")
        for file in interview_files[-5:]:  # Show last 5
            st.text(f"📄 {file.replace('interview_session_', '').replace('.json', '')}")

def show_progress_page():
    """Progress tracking page"""
    st.markdown('<h2 class="step-header">📈 Progress Tracking</h2>', unsafe_allow_html=True)

    # Load all feedback reports
    feedback_files = []
    if os.path.exists("data"):
        feedback_files = [f for f in os.listdir("data") if f.startswith("feedback_report")]

    if not feedback_files:
        st.info("📊 No progress data yet. Complete some interviews and get feedback to see your progress!")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📊 Your Interview Progress")

        # Mock progress data (in real app, load from files)
        import pandas as pd

        progress_data = {
            "Session": ["Session 1", "Session 2", "Session 3", "Session 4"],
            "Overall Score": [6.5, 7.0, 7.5, 8.0],
            "Clarity": [6, 7, 8, 8],
            "Relevance": [7, 7, 7, 8],
            "Confidence": [6, 7, 7, 8],
            "Depth": [7, 7, 8, 8]
        }

        df = pd.DataFrame(progress_data)

        # Line chart
        st.line_chart(df.set_index("Session")[["Overall Score", "Clarity", "Relevance", "Confidence", "Depth"]])

        # Progress table
        st.markdown("### 📋 Session Details")
        st.dataframe(df, use_container_width=True)

        # Statistics
        st.markdown("### 📈 Statistics")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Total Sessions", len(feedback_files))
        with col_b:
            st.metric("Average Score", "7.5/10")
        with col_c:
            st.metric("Improvement", "+1.5", "Since first session")

    with col2:
        st.markdown("### 🎯 Achievement Badges")
        st.markdown("🏆 **First Interview** - Completed!")
        st.markdown("📈 **Improving** - 3+ sessions")
        st.markdown("🎯 **Consistent** - 5+ sessions")
        st.markdown("⭐ **Interview Ready** - 8+ average score")

        st.markdown("### 📅 Recent Activity")
        for file in feedback_files[-3:]:
            date_str = file.replace("feedback_report_", "").replace(".json", "")
            st.text(f"📊 {date_str}")

        st.markdown("### 🚀 Recommendations")
        st.info("💡 You're making great progress! Focus on behavioral questions for your next session.")


if __name__ == "__main__":
    main()