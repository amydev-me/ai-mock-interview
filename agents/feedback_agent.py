# agents/feedback_agent.py (UPDATED VERSION)

from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate

from agents.base_agent import BaseAgent
from mcp_servers.file_server import FileSystemMCPServer
import json
from typing import Dict, Any, List
from datetime import datetime  # Ensure datetime is imported
import traceback
import re

class FeedbackAgent(BaseAgent):
    """Agent that provides feedback on interview answers"""

    def __init__(self):
        self.file_server = FileSystemMCPServer()

        tools = [
            Tool(
                name="load_interview_session",
                description="Load interview session data for analysis. Input is the filename of the session (e.g., 'interview_session_YYYYMMDD_HHMMSS.json').",
                func=self._load_interview_session
            ),
            Tool(
                name="analyze_answer",
                description="Analyze a specific answer and provide structured feedback including scores (Clarity, Relevance, Depth, Confidence). Input is a JSON string with 'question' and 'answer' keys.",
                func=self._analyze_answer_llm
            ),
            Tool(
                name="generate_overall_feedback_content",  # Keep this name
                description="""Generates a comprehensive overall feedback report as a JSON object. 
                            Input is a JSON string of the 'recorded_answers' list from an interview session.
                            The output is a JSON object matching the required feedback report structure.
                            This tool returns ONLY the JSON object, nothing else.
                            """,
                func=self._generate_overall_feedback_llm
            ),
            Tool(
                name="save_feedback_report",
                description="Save feedback report to file. Input is a JSON string of the feedback data.",
                func=self._save_feedback_report
            )
        ]

        system_prompt = """
               You are a Feedback Agent specializing in generating comprehensive interview performance reports.

               Your ONLY task is to take a JSON string of recorded interview answers, generate a full feedback report for them, and return ONLY that report as a JSON object.

               Follow this strict process:
               1. When given interview answers (as a JSON string), IMMEDIATELY use the 'generate_overall_feedback_content' tool.
               2. Return the exact JSON output from 'generate_overall_feedback_content' directly.

               NO PREAMBLES, NO CONVERSATIONAL TEXT, NO MARKDOWN FENCES (```json), NO EXPLANATIONS. JUST THE RAW JSON OBJECT.

               The feedback report must be a JSON object with keys like 'total_score', 'performance_level', 'key_strengths', 'priority_improvements', 'next_steps', 'clarity_score', 'relevance_score', 'confidence_score', 'depth_score'.
               """

        super().__init__(
            agent_name="feedback_agent",
            system_prompt=system_prompt,
            tools=tools
        )

    def _load_interview_session(self, session_file: str) -> str:
        """Load interview session data"""
        result = self.file_server.read_file(session_file)
        if result.get("success"):
            return result["content"]
        else:
            return f"❌ Could not load session: {result.get('error')}"

    def _generate_overall_feedback_llm(self, recorded_answers_json: str) -> str:
        """Generate comprehensive feedback for entire interview using LLM."""
        raw_llm_output = ""  # Initialize here for error messages
        json_string_to_parse = ""  # Initialize here for error messages

        try:
            recorded_answers = json.loads(recorded_answers_json)
            if not isinstance(recorded_answers, list):
                raise ValueError("Expected recorded_answers to be a JSON list.")

            if not recorded_answers:  # Handle case with no answers gracefully
                return json.dumps({
                    "total_score": "0/10",
                    "performance_level": "No answers provided",
                    "key_strengths": [],
                    "priority_improvements": ["No answers were recorded for analysis."],
                    "next_steps": ["Complete a mock interview with answers."],
                    "clarity_score": "N/A", "relevance_score": "N/A", "confidence_score": "N/A", "depth_score": "N/A"
                })

            answers_detail = []
            for i, qa in enumerate(recorded_answers):
                # Ensure getting 'question' and 'answer' with defaults
                answers_detail.append(
                    f"--- Question {i + 1} ---\nQ: {qa.get('question', 'N/A')}\nA: {qa.get('answer', 'N/A')}\n")
            answers_summary = "\n".join(answers_detail)

            MAX_SUMMARY_LENGTH = 3000  # Adjust based on your model's context window
            if len(answers_summary) > MAX_SUMMARY_LENGTH:
                answers_summary = answers_summary[:MAX_SUMMARY_LENGTH] + "\n... (summary truncated due to length)"
                print(f"DEBUG_FEEDBACK: Answers summary truncated to {MAX_SUMMARY_LENGTH} characters.")

            llm_prompt_template = ChatPromptTemplate.from_messages([
                ("system", """
                You are an expert interview performance evaluator. Your goal is to provide a comprehensive and actionable feedback report for a candidate's mock interview.

                You must provide an overall score (X/10), a performance level, key strengths, priority improvements, and actionable next steps.
                Additionally, provide average scores for Clarity, Relevance, Confidence, and Depth, each on a scale of 1-10 (e.g., "7/10").

                Consider the following criteria for scoring and feedback:
                -   **Clarity**: How easy was the answer to understand? Was it well-structured?
                -   **Relevance**: Did the answer directly address the question?
                -   **Depth**: Was the answer comprehensive? Did it provide sufficient detail, examples, or technical understanding?
                -   **Confidence**: Did the answer sound assured and well-prepared?
                -   **STAR Method**: For behavioral questions, was the Situation-Task-Action-Result structure used effectively? (If applicable)

                **VERY IMPORTANT INSTRUCTION:**
                Respond ONLY with a valid JSON object. Do NOT include any preambles, conversational text, explanations, or markdown fences (```json).
                Ensure ALL specified keys are present in the JSON, even if you put "N/A" or "0/10" if data is insufficient.

                Example JSON Structure (fill with actual analysis):
                {{ # <-- DOUBLE CURLY BRACES HERE
                    "total_score": "8.5/10",
                    "performance_level": "Good - Ready for interviews with minor improvements",
                    "key_strengths": ["Clear communication", "Strong technical examples", "Good problem-solving approach"],
                    "priority_improvements": ["Quantify achievements more (use numbers)", "Improve STAR method application", "Research company-specific examples more"],
                    "next_steps": ["Practice 3 more behavioral questions using STAR", "Review company values and recent news", "Record and self-review next mock interview"],
                    "clarity_score": "8/10",
                    "relevance_score": "9/10",
                    "confidence_score": "7/10",
                    "depth_score": "8/10"
                }} # <-- DOUBLE CURLY BRACES HERE
                """),
                ("user",
                 f"Analyze the following interview session answers and provide an overall feedback report:\n\n{answers_summary}")
            ])

            try:
                chain = llm_prompt_template | self.llm.bind(response_format={"type": "json_object"})
                response = chain.invoke({"recorded_answers": recorded_answers})
                raw_llm_output = response.content
            except Exception as llm_e:
                print(f"DEBUG_FEEDBACK: ERROR during LLM chain.invoke: {llm_e}")
                traceback.print_exc()  # Print inner traceback
                return json.dumps({
                    "total_score": "Error", "performance_level": "LLM Chain Failure",
                    "key_strengths": ["AI model failed to respond correctly."],
                    "priority_improvements": ["Check console for LLM chain errors."],
                    "next_steps": ["Ensure API key is valid and model is available."],
                    "clarity_score": "Error", "relevance_score": "Error", "confidence_score": "Error",
                    "depth_score": "Error",
                    "llm_error_message": str(llm_e)
                })

            print(f"DEBUG_FEEDBACK: Raw LLM Output for overall feedback:\n{raw_llm_output}")

            json_string_to_parse = raw_llm_output  # Default to whole output

            # --- SUPER ROBUST JSON EXTRACTION USING REGEX ---
            match = re.search(r'(\{.*?})', raw_llm_output, re.DOTALL)
            if match:
                json_string_to_parse = match.group(1)  # Get the matched group (the JSON string)
            else:
                print(f"DEBUG_FEEDBACK: Regex failed to find a JSON object. Attempting to parse raw output.")
                json_string_to_parse = raw_llm_output
                # --- END SUPER ROBUST JSON EXTRACTION ---

            # --- CRITICAL CHANGE: Default the overall_feedback dict structure BEFORE trying to parse LLM output ---
            # THIS BLOCK SHOULD BE OUTSIDE THE 'else' FROM THE REGEX MATCH
            overall_feedback = {
                "total_score": "N/A", "performance_level": "Not Provided",
                "key_strengths": [], "priority_improvements": [], "next_steps": [],
                "clarity_score": "N/A", "relevance_score": "N/A", "confidence_score": "N/A", "depth_score": "N/A"
            }
            # --- END CRITICAL CHANGE ---

            try:  # Try to load from LLM, and update the default dictionary
                parsed_llm_output = json.loads(json_string_to_parse)
                if isinstance(parsed_llm_output, dict):
                    overall_feedback.update(parsed_llm_output)  # Update with what LLM provided
                else:
                    raise ValueError("LLM output was not a dictionary after JSON parsing.")
            except json.JSONDecodeError as e:
                print(
                    f"DEBUG_FEEDBACK: JSON Decode Error after extraction: {e}. Attempted to parse: '{json_string_to_parse}'. Raw LLM output: '{raw_llm_output}'")
                traceback.print_exc()
                overall_feedback.update({"total_score": "Error", "performance_level": "JSON Format Error"})
            except ValueError as e:
                print(
                    f"DEBUG_FEEDBACK: Structure Error after JSON parsing: {e}. Parsed: {parsed_llm_output}. Raw LLM output: '{raw_llm_output}'")
                traceback.print_exc()
                overall_feedback.update({"total_score": "Error", "performance_level": "Structure Error"})

            # Ensure all scores are strings (e.g., "7/10") if they come as numbers for consistency
            score_keys = ["total_score", "clarity_score", "relevance_score", "confidence_score", "depth_score"]
            for key in score_keys:
                if key in overall_feedback and isinstance(overall_feedback[key], (int, float)):
                    overall_feedback[key] = f"{overall_feedback[key]}/10"
                elif key in overall_feedback and not isinstance(overall_feedback[key], str):
                    overall_feedback[key] = "N/A"  # Ensure it's a string, if not int/float, make N/A

            # Ensure lists are lists
            for key in ["key_strengths", "priority_improvements", "next_steps"]:
                if key in overall_feedback and not isinstance(overall_feedback[key], list):
                    overall_feedback[key] = [str(overall_feedback[key])] if overall_feedback[
                        key] else []  # Wrap if non-list but not empty
                elif key not in overall_feedback:
                    overall_feedback[key] = []  # Ensure it's an empty list if missing

            return json.dumps(overall_feedback, indent=2)

        except Exception as e:  # This is the outermost catch for unforeseen errors
            print(f"DEBUG_FEEDBACK: General Error in _generate_overall_feedback_llm (Outer Catch): {e}")
            traceback.print_exc()
            return json.dumps({
                "total_score": "Error", "performance_level": "Uncaught Error",
                "key_strengths": ["An unexpected error occurred."],
                "priority_improvements": ["Check console for traceback."],
                "next_steps": ["Report this issue."],
                "clarity_score": "Error", "relevance_score": "Error", "confidence_score": "Error",
                "depth_score": "Error"
            })
    def _save_feedback_report(self, feedback_data: str) -> str:
        """Save feedback report to file"""
        import datetime  # Ensure this is imported here if not at top
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"feedback_report_{timestamp}.json"

        result = self.file_server.write_file(filename, feedback_data)
        if result.get("success"):
            print(f"💾 FeedbackAgent: Report saved as {filename}")
            return f"📊 Feedback report saved as {filename}"
        else:
            print(f"❌ FeedbackAgent: Error saving report {filename}: {result.get('error')}")
            return f"❌ Error saving report: {result.get('error')}"
    def _analyze_answer_llm(self, answer_data_json: str) -> str:
        """Analyze a specific answer and provide detailed feedback using LLM."""
        try:
            answer_data = json.loads(answer_data_json)
            question = answer_data.get("question", "N/A")
            answer = answer_data.get("answer", "N/A")

            llm_prompt_template = ChatPromptTemplate.from_messages([
                ("system", """
                You are an expert interview feedback analyst.
                Evaluate the provided answer based on Clarity, Relevance, Depth, and Confidence (1-10 scale, integers only).
                Provide strengths, improvements, and actionable suggestions specific to this answer.

                **IMPORTANT INSTRUCTION:**
                Respond ONLY with a valid JSON object.
                Example format: {"scores": {"clarity": 7, "relevance": 8, "depth": 6, "confidence": 7}, "strengths": ["Good point"], "improvements": ["Be more specific"], "suggestions": ["Use STAR method"]}.
                DO NOT include any other text, preambles, explanations, or markdown fences (```json).
                """),
                ("user", f"Question: {question}\nAnswer: {answer}")
            ])

            chain = llm_prompt_template | self.llm  # Removed .bind(response_format...) for debug
            response = chain.invoke({"question": question, "answer": answer})

            raw_llm_output = response.content
            print(f"DEBUG_FEEDBACK: Raw LLM Output for single answer analysis:\n{raw_llm_output}")
            json_string_to_parse = raw_llm_output # Default to whole output
            match = re.search(r'(\{.*?})', raw_llm_output, re.DOTALL)
            if match:
                json_string_to_parse = match.group(1)  # Get the matched group (the JSON string)
            else:
                # If the regex fails to find a JSON object, fall back to trying the whole string
                print(f"DEBUG_FEEDBACK: Regex failed to find a JSON object. Attempting to parse raw output.")
                json_string_to_parse = raw_llm_output
                # Robust JSON extraction
            json_start = raw_llm_output.find('{')
            json_end = raw_llm_output.rfind('}')

            if json_start != -1 and json_end != -1 and json_end > json_start:
                json_string_to_parse = raw_llm_output[json_start: json_end + 1]
            else:
                # If the regex fails to find a JSON object, fall back to trying the whole string
                print(f"DEBUG_FEEDBACK: Regex failed to find a JSON object. Attempting to parse raw output.")
                json_string_to_parse = raw_llm_output
                # --- END CRITICAL FIX ---
                # --- CRITICAL CHANGE: Default the overall_feedback dict structure BEFORE trying to parse LLM output ---
                # >>> THIS LINE AND THE FOLLOWING ARE INDENTED INCORRECTLY <<<
                overall_feedback = {
                    "total_score": "N/A", "performance_level": "Not Provided",
                    "key_strengths": [], "priority_improvements": [], "next_steps": [],
                    "clarity_score": "N/A", "relevance_score": "N/A", "confidence_score": "N/A", "depth_score": "N/A"
                }

            feedback = json.loads(json_string_to_parse)
            if not isinstance(feedback, dict) or "scores" not in feedback:
                raise ValueError("LLM did not return expected feedback JSON structure.")

            return json.dumps(feedback, indent=2)

        except json.JSONDecodeError as e:
            print(
                f"DEBUG_FEEDBACK: JSON Decode Error in _analyze_answer_llm: {e}. Attempted to parse: '{json_string_to_parse}'")
            return f"Error analyzing answer (JSON issue): {str(e)}. Raw LLM: {raw_llm_output}"
        except json.JSONDecodeError as e:
            print(
                f"DEBUG_FEEDBACK: JSON Decode Error in _analyze_answer_llm: {e}. Attempted to parse: '{json_string_to_parse}'. Raw LLM: '{raw_llm_output}'")
            traceback.print_exc()  # <--- FIX HERE
            return f"Error analyzing answer (JSON issue): {str(e)}. Raw LLM: {raw_llm_output}"
        except Exception as e:
            print(f"DEBUG_FEEDBACK: General Error in _analyze_answer_llm: {e}")
            traceback.print_exc()  # <--- FIX HERE
            return f"Error analyzing answer: {str(e)}"

# Test the Feedback Agent (UPDATED TEST BLOCK)
if __name__ == "__main__":
    feedback_agent = FeedbackAgent()

    print("📊 Testing Feedback Agent with LLM...")

    # Simulate a recorded_answers list from an interview session
    mock_answers = [
        {"question": "Tell me about your experience with Python.",
         "answer": "I've been using Python for about 3 years, mainly for web development with Flask and Django. I built a REST API for a small e-commerce site and also some data processing scripts. I'm comfortable with its syntax and common libraries."},
        {"question": "How do you handle technical disagreements with team members?",
         "answer": "I try to understand their perspective first. Then, I present my reasoning with data or examples. If we still disagree, I suggest a small proof-of-concept or escalate to a tech lead for a decision. It's important to keep the team's goal in mind."},
        {"question": "Describe a challenging project you worked on.",
         "answer": "I once worked on migrating a legacy database system. It was challenging because of schema inconsistencies and downtime constraints. I designed a phased migration plan, wrote custom scripts, and coordinated with the ops team. We reduced downtime by 50% compared to initial estimates, and data integrity was maintained."}
    ]

    print("\nGenerating overall feedback...")
    # Call the tool directly to test its LLM functionality
    overall_feedback_result = feedback_agent._generate_overall_feedback_llm(json.dumps(mock_answers))
    print(f"\nOverall Feedback from LLM:\n{overall_feedback_result}")

    print("\nAnalyzing a single answer...")
    single_answer_data = {"question": "What is polymorphism?",
                          "answer": "Polymorphism is when an object can take on many forms. Like a function can take different types of arguments and work with them."}
    single_analysis_result = feedback_agent._analyze_answer_llm(json.dumps(single_answer_data))
    print(f"\nSingle Answer Analysis from LLM:\n{single_analysis_result}")
