# agents/interview_simulator.py (REVISED AND COMPLETE VERSION)

from langchain.tools import Tool
from agents.base_agent import BaseAgent
from mcp_servers.file_server import FileSystemMCPServer
import json
from typing import Dict, Any, List
from datetime import datetime  # Make sure datetime is imported
import os

class InterviewSimulatorAgent(BaseAgent):
    """Agent that conducts mock interviews"""

    def __init__(self):
        # Initialize MCP server
        self.file_server = FileSystemMCPServer()

        # Interview state
        self.current_question_index = 0
        self.questions = []  # This will now store the dynamically loaded questions
        self.answers = []

        # Create tools
        tools = [
            Tool(
                name="load_questions",
                description="Load interview questions from 'interview_questions.json' for the current session. No input required for this tool.",
                func=self._load_questions,
                args_schema=None
            ),
            Tool(
                name="ask_next_question",
                description="Ask the next interview question from the loaded list. No input required for this tool.",
                func=self._ask_next_question,
                args_schema=None
            ),
            Tool(
                name="record_answer",
                description="Record the candidate's answer for the current question. Input is the candidate's answer as a string.",
                func=self._record_answer
            ),
            Tool(
                name="save_interview_session",
                description="Save the complete interview session data. Input is the session name (optional string).",
                func=self._save_interview_session
            )
        ]

        # The system prompt focuses on its primary role, as the UI will handle orchestration for start/next.
        system_prompt = """
        You are an Interview Simulator Agent. Your role is to conduct mock interviews professionally.

        You will be instructed to:
        - Load questions (using 'load_questions' tool).
        - Ask specific questions (using 'ask_next_question' tool).
        - Record answers (using 'record_answer' tool).
        - Save the session (using 'save_interview_session' tool).

        When asking questions, preface them clearly, e.g., 'Question 1/5: ...'.
        When recording answers, provide a brief positive affirmation.
        """

        super().__init__(
            agent_name="interview_simulator",
            system_prompt=system_prompt,
            tools=tools
        )

    def _load_questions(self, *args, **kwargs) -> str:  # Add *args, **kwargs for robustness
        """Load interview questions from 'interview_questions.json'."""
        filename = "interview_questions.json"
        result = self.file_server.read_file(filename)
        if result.get("success"):
            try:
                content = json.loads(result["content"])
                if "questions" in content and isinstance(content["questions"], list):
                    self.questions = content["questions"]
                    self.current_question_index = 0
                    self.answers = []
                    print(f"🎤 InterviewSimulator: Loaded {len(self.questions)} questions from file.")
                    return f"✅ Questions loaded successfully. Ready to start interview with {len(self.questions)} questions!"
                else:
                    print("❌ InterviewSimulator: Invalid questions format in file.")
                    return "❌ Error: Invalid questions format in file. Using sample questions."
            except json.JSONDecodeError:
                print("❌ InterviewSimulator: Could not parse questions file (JSONDecodeError).")
                return "❌ Error: Could not parse questions file. Using sample questions."
        else:
            print(f"⚠️ InterviewSimulator: Questions file not found. {result.get('error')}. Using sample questions.")
            # Fallback to sample questions if file doesn't exist or error
            self.questions = [
                "Tell me about your most significant project and your role in it.",
                "How do you approach learning new programming languages or frameworks?",
                "Describe your experience with cloud platforms like AWS or Azure.",
                "What motivates you to work in software development?",
                "How do you handle code reviews, both giving and receiving?"
            ]
            self.current_question_index = 0
            self.answers = []
            return f"📝 Using sample questions as no generated questions found. Ready to start interview!"

    def _ask_next_question(self, *args, **kwargs) -> str:  # Add *args, **kwargs for robustness
        """Ask the next interview question."""
        if not self.questions:
            # If questions are somehow empty, attempt to load them
            load_status = self._load_questions()
            if "Error" in load_status:
                return load_status  # Return error if loading failed

        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            # Do NOT increment index here. Increment only after answer is recorded.
            return f"**Question {self.current_question_index + 1}/{len(self.questions)}:** {question}"
        else:
            return "🎉 **Interview Complete!** Thank you for your time. Please click 'Get Feedback' to see your performance."

    def _record_answer(self, answer: str) -> str:
        """Record the candidate's answer and move to the next question."""
        if not self.questions or self.current_question_index >= len(self.questions):
            return "Interview is either not started, no questions loaded, or already complete. Cannot record more answers."

        self.answers.append({
            "question_number": self.current_question_index + 1,
            "question": self.questions[self.current_question_index],
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })

        # Increment to the next question ONLY AFTER recording the answer
        self.current_question_index += 1

        # Provide encouraging feedback (optional, LLM can do this via prompt)
        encouragement = [
            "Great answer! Let's continue.",
            "Thank you for that insight. Moving on...",
            "Interesting perspective! Next question:",
            "Well explained! Let's proceed.",
            "Good example! Continuing..."
        ]
        import random
        feedback = random.choice(encouragement)
        return f"✅ Answer recorded. {feedback}"

    def _save_interview_session(self, session_name: str = "interview_session") -> str:
        """Save the complete interview session."""
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "total_questions_asked": len(self.answers),
            "questions_used": self.questions,
            "recorded_answers": self.answers,
            "status": "completed"
        }

        # Ensure the filename starts correctly for filtering later
        # Example: interview_session_20250627_103045.json
        filename = f"interview_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"  # <--- IMPORTANT: Ensure this format

        # Add a DEBUG print to explicitly show the generated filename
        print(
            f"DEBUG_SIMULATOR: Attempting to save interview session to filename: {filename}")  # <--- ADD THIS DEBUG PRINT

        result = self.file_server.write_file(filename, json.dumps(session_data, indent=2))

        if result.get("success"):
            print(f"💾 InterviewSimulator: Interview session saved successfully as {filename}")
            return f"💾 Interview session saved as {filename}"
        else:
            print(f"❌ InterviewSimulator: Error saving session to {filename}: {result.get('error')}")
            return f"❌ Error saving session: {result.get('error')}"

    def start_interview_sequence(self) -> str:
        """
        Explicitly triggers the loading of questions and then asks the first one.
        This method will be called directly by the Streamlit UI.
        """
        load_status = self._load_questions()
        if "Error" in load_status:
            return load_status  # Return error if loading failed

        if not self.questions:  # Fallback if _load_questions didn't populate self.questions
            return "❌ No questions available to start the interview. Please generate questions first."

        # Now, explicitly ask the first question
        return self._ask_next_question()


# Test the Interview Simulator (UPDATED TEST BLOCK for direct testing)
if __name__ == "__main__":
    # Ensure data directory exists for testing
    os.makedirs("data", exist_ok=True)

    simulator = InterviewSimulatorAgent()

    print("🎤 Testing Interview Simulator Agent...")

    # 1. Simulate initial setup: generate some questions first
    mock_interview_questions = {
        "timestamp": datetime.now().isoformat(),
        "questions": [
            "Tell me about a time you faced a difficult technical challenge.",
            "How do you approach learning new programming languages or frameworks?",
            "Describe your experience with cloud platforms like AWS or Azure.",
            "What motivates you to work in software development?",
            "How do you handle code reviews, both giving and receiving?"
        ]
    }
    with open("data/interview_questions.json", "w") as f:
        json.dump(mock_interview_questions, f, indent=2)
    print("Mock interview_questions.json created for testing.")

    # 2. Start interview sequence using the new method
    print("\nStarting the interview sequence...")
    first_question_response = simulator.start_interview_sequence()
    print(f"Initial Interviewer Response: {first_question_response}")

    if "Question 1" in first_question_response:
        print("\nSimulating answers...")
        # Simulate user answering and recording
        print(simulator._record_answer("My answer to question 1 is: 'I faced a memory leak... [details]'"))
        print(simulator._ask_next_question())  # Get next question

        print(simulator._record_answer("My answer to question 2 is: 'I approach learning by... [details]'"))
        print(simulator._ask_next_question())  # Get next question

        # Simulate ending the interview
        print(simulator._record_answer(
            "My answer to question 3 is: 'My experience with cloud is... [details]'"))  # Record last answer
        print(simulator._ask_next_question())  # This should now say "Interview Complete!"

        print("\nSaving interview session...")
        print(simulator._save_interview_session("test_session"))

    else:
        print("Interview sequence did not start as expected in direct test. Check logs for errors.")
