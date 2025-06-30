from langchain.tools import Tool
from agents.base_agent import BaseAgent
from mcp_servers.file_server import FileSystemMCPServer
from typing import List, Dict, Any
import datetime
import json
from langchain.prompts import ChatPromptTemplate

class QuestionGeneratorAgent(BaseAgent):
    """Agent that generates tailored interview questions"""

    def __init__(self):
        # Initialize MCP server
        self.file_server = FileSystemMCPServer()

        # Create tools
        tools = [
            Tool(
                name="load_research_data",
                description="Load company and role research data from 'research_data.json'. This data is crucial for tailoring questions. Returns a JSON string of the research data. This tool takes NO input arguments from the LLM.",
                func=self._load_research_data,
                args_schema=None  # <-- THIS MUST BE HERE
            ),
            Tool(
                name="generate_and_save_questions",
                description="""Generate a specified number and mix of technical, behavioral, and company-specific interview questions for a given role and company. 
                       Requires a JSON input with keys: 'role' (str), 'company_name' (str), 'num_questions' (int), 'question_types' (list of str, e.g., ["Technical Questions", "Behavioral Questions"]).
                       It uses the LLM to generate questions and then saves them to 'interview_questions.json'. Returns the generated questions as a JSON list.
                       """,
                func=self._generate_and_save_questions_llm
            ),
            Tool(
                name="save_questions_to_file",  # Renamed for clarity, less conflict with internal method
                description="Save a list of generated questions to 'interview_questions.json'. Input is a JSON string representing a list of questions.",
                func=self._save_questions_to_file
            )
        ]

        system_prompt = """
            You are a Question Generator Agent. Your primary goal is to generate a comprehensive set of interview questions.

            Follow this strict multi-step process:
            1. **Load Research Data**: FIRST, use the 'load_research_data' tool to get company and role context. This is crucial for tailoring questions.
            2. **Generate Questions**: THEN, use the 'generate_and_save_questions' tool. Provide it with the job role, company name, desired number of questions, and specific question types (e.g., "Technical Questions", "Behavioral Questions", "Company-Specific Questions"). The research data will be implicitly used.
            3. **Return Questions**: Finally, provide the generated list of questions back to the user.

            Ensure the generated questions are relevant to the company and role, varied in difficulty, and include the requested types.
        """

        super().__init__(
            agent_name="question_generator",
            system_prompt=system_prompt,
            tools=tools
        )

    def _load_research_data(self, filename: str = "research_data.json") -> str: # Keep 'filename' here
        """Load research data from file"""
        filename = "research_data.json" # Force it to look for this specific file
        result = self.file_server.read_file(filename)
        if result.get("success"):
            print("💾 Research data loaded successfully by QGA.") # Added print for debug
            return result["content"]
        else:
            print(f"⚠️ QGA: No research data found: {result.get('error')}. Using generic context.")
            # Your existing fallback
            return json.dumps({
                "timestamp": datetime.now().isoformat(),
                "company_data": {
                    "name": "Generic Tech Company",
                    "culture": "Collaborative, innovation-driven",
                    "values": "Teamwork, customer focus",
                    "interview_style": "Standard technical and behavioral",
                    "recent_news": "Continual growth",
                    "role_requirements": "Strong problem-solving, coding skills"
                }
            })

    def _generate_technical_questions(self, role: str) -> str:
        """Generate technical questions for specific role"""
        role_questions = {
            "software engineer": [
                "Explain the difference between a stack and a queue",
                "How would you reverse a linked list?",
                "What is the time complexity of binary search?",
                "Describe how you would design a URL shortener like bit.ly",
                "What are the differences between SQL and NoSQL databases?",
                "Explain REST API principles",
                "How would you handle race conditions in concurrent programming?"
            ],
            "data scientist": [
                "Explain overfitting and how to prevent it",
                "What is the difference between supervised and unsupervised learning?",
                "How would you handle missing data in a dataset?",
                "Explain the bias-variance tradeoff",
                "What evaluation metrics would you use for a classification problem?",
                "How would you approach A/B testing?",
                "Explain principal component analysis (PCA)"
            ],
            "product manager": [
                "How would you prioritize features for a product roadmap?",
                "Describe how you would launch a new product feature",
                "How do you measure product success?",
                "Walk me through how you would analyze user feedback",
                "How would you handle conflicting stakeholder requirements?",
                "Describe your experience with A/B testing",
                "How would you decide whether to build or buy a solution?"
            ]
        }

        # Default to software engineer if role not found
        questions = role_questions.get(role.lower(), role_questions["software engineer"])
        return json.dumps(questions[:5], indent=2)  # Return 5 technical questions

    def _generate_behavioral_questions(self, company_culture: str) -> str:
        """Generate behavioral questions based on company culture"""
        behavioral_questions = [
            "Tell me about a time when you had to work with a difficult team member",
            "Describe a situation where you had to learn something new quickly",
            "Give an example of when you had to make a decision with limited information",
            "Tell me about a time you failed and what you learned from it",
            "Describe a situation where you had to convince others of your idea",
            "Tell me about a time when you exceeded expectations",
            "Give an example of when you had to handle multiple priorities",
            "Describe a time when you received constructive criticism",
            "Tell me about a project you're most proud of",
            "Give an example of when you had to adapt to change"
        ]

        return json.dumps(behavioral_questions[:5], indent=2)  # Return 5 behavioral questions

    def _save_questions(self, questions_data: str) -> str:
        """Save generated questions to file"""
        result = self.file_server.write_file("interview_questions.json", questions_data)
        if result.get("success"):
            return "Questions saved successfully"
        else:
            return f"Error saving questions: {result.get('error')}"

    def generate_questions_for_ui(self, company_name: str, role: str, num_questions: int, question_types: list) -> list:
        """Simplified method for UI integration"""
        try:
            # Load research data
            research_result = self._load_research_data()

            questions = []

            if "Technical Questions" in question_types:
                tech_questions = [
                    f"Explain how you would architect a {role.lower()} solution for {company_name}",
                    "Walk me through your debugging process for a complex issue",
                    "Describe a challenging technical problem you solved recently",
                    "How do you stay updated with new technologies in your field?",
                    "What's your approach to code reviews and quality assurance?"
                ]
                questions.extend(tech_questions[:max(1, num_questions // 2)])

            if "Behavioral Questions" in question_types:
                behavioral_questions = [
                    f"Why do you want to work at {company_name} specifically?",
                    "Tell me about a time you had to work with a difficult team member",
                    "Describe a situation where you had to learn something new quickly",
                    "How do you handle competing priorities and tight deadlines?",
                    "Give an example of when you had to convince others of your idea"
                ]
                questions.extend(behavioral_questions[:max(1, num_questions // 2)])

            if "Company-Specific Questions" in question_types:
                company_questions = [
                    f"How would you contribute to {company_name}'s mission?",
                    f"What do you know about {company_name}'s recent developments?",
                    f"How do you see yourself fitting into {company_name}'s culture?"
                ]
                questions.extend(company_questions[:max(1, num_questions // 4)])

            # Trim to requested number and add variety
            final_questions = questions[:num_questions]

            # Add some randomization for variety
            import random
            if len(final_questions) < num_questions:
                extra_questions = [
                    "What are your career goals for the next 5 years?",
                    "Describe your ideal work environment",
                    "How do you handle feedback and criticism?",
                    "What motivates you in your daily work?",
                    "Tell me about a project you're particularly proud of"
                ]
                random.shuffle(extra_questions)
                final_questions.extend(extra_questions[:num_questions - len(final_questions)])

            return final_questions[:num_questions]

        except Exception as e:
            # Fallback questions
            return [
                       f"Tell me about your background in {role}",
                       f"Why are you interested in this {role} position?",
                       "What's your greatest professional strength?",
                       "Describe a challenging project you worked on",
                       "How do you handle working under pressure?"
                   ][:num_questions]

    def _generate_and_save_questions_llm(self, input_json: str) -> str:
        """
        Generates and saves questions using the LLM based on input parameters.
        Input: JSON string with 'role' (str), 'company_name' (str), 'num_questions' (int), 'question_types' (list of str).
        """
        try:
            input_data = json.loads(input_json)
            role = input_data.get("role", "Software Engineer")
            company_name = input_data.get("company_name", "a tech company")
            num_questions = input_data.get("num_questions", 10)
            question_types = input_data.get("question_types", ["Technical Questions", "Behavioral Questions"])

            # Load actual research data for context
            research_data_str = self._load_research_data()
            research_data_obj = json.loads(research_data_str)
            company_info = research_data_obj.get("company_data", {})

            # Construct the comprehensive prompt for the LLM
            prompt_parts = []
            if "Technical Questions" in question_types:
                prompt_parts.append("technical")
            if "Behavioral Questions" in question_types:
                prompt_parts.append("behavioral")
            if "Company-Specific Questions" in question_types:
                # Make company-specific part more precise for prompt
                prompt_parts.append(f"company-specific for {company_name}")

            question_mix = ", ".join(prompt_parts)

            llm_prompt_template = ChatPromptTemplate.from_messages([
                ("system", f"""
                You are an expert interviewer for a {role} role at {company_name}.
                Company Culture: {company_info.get('culture', 'N/A')}.
                Company Values: {company_info.get('values', 'N/A')}.
                Interview Style: {company_info.get('interview_style', 'N/A')}.
                Role Requirements: {company_info.get('role_requirements', 'N/A')}.

                Your task is to generate interview questions.
                """),
                ("user", f"""
                Generate exactly {num_questions} interview questions.
                The questions must be a diverse mix of: {question_mix}.
                Ensure variety in difficulty (easy, medium, hard).

                **IMPORTANT INSTRUCTION:**
                Respond ONLY with a valid JSON array (list) of strings.
                Example format:
                ["Question 1?", "Question 2?", "Question 3?"]

                DO NOT include any other text, preambles, explanations, or markdown fences (```json).
                Just the raw JSON array.
                """)
            ])

            # The .bind(response_format={"type": "json_object"}) is good for newer OpenAI models,
            # but sometimes older models or specific outputs still need post-processing.
            chain = llm_prompt_template | self.llm  # Removed .bind(response_format...) for now to see raw output

            response = chain.invoke({
                "role": role,
                "company_name": company_name,
                "num_questions": num_questions,
                "question_types": question_types,
                "company_info": company_info
            })

            raw_llm_output = response.content
            print(f"DEBUG: Raw LLM Output for questions:\n{raw_llm_output}")  # <-- Add this debug print!

            # --- Robust JSON extraction ---
            # Try to find the first and last bracket to isolate JSON,
            # or try direct parsing if it's clean.

            json_start = raw_llm_output.find('[')
            json_end = raw_llm_output.rfind(']')

            if json_start != -1 and json_end != -1 and json_end > json_start:
                json_string_to_parse = raw_llm_output[json_start: json_end + 1]
            else:
                json_string_to_parse = raw_llm_output  # Fallback to trying the whole string

            generated_questions = json.loads(json_string_to_parse)

            if not isinstance(generated_questions, list):
                raise ValueError("LLM did not return a JSON list of questions after extraction.")

            print(f"Generated {len(generated_questions)} questions after parsing.")

            # Save the generated questions to file
            self._save_questions_to_file(json.dumps(generated_questions))

            return json.dumps(generated_questions)  # Return the list as JSON string

        except json.JSONDecodeError as e:
            print(f"JSON Parsing Error: {e} - Attempted to parse: '{json_string_to_parse}'")
            return f"Error: Failed to parse LLM response as JSON. Please try again. Raw LLM output: {raw_llm_output}"
        except Exception as e:
            print(f"Error in _generate_and_save_questions_llm: {e}")
            # Ensure datetime is imported for the fallback if not already at top of file
            from datetime import datetime
            # Provide a fallback for the agent's response to keep the flow going
            return json.dumps([
                f"What is your experience with {role}?",
                f"Tell me about {company_name}'s values?",
                "Describe a project you worked on.",
                "How do you handle conflict?"
            ])

    def _save_questions_to_file(self, questions_data: str) -> str:  # Renamed for clarity
        """Save a list of generated questions (JSON string) to 'interview_questions.json'"""
        try:
            # Validate if questions_data is a JSON string representing a list
            parsed_questions = json.loads(questions_data)
            if not isinstance(parsed_questions, list):
                raise ValueError("Expected a JSON list of questions for saving.")

            # Add timestamp and wrap in a proper structure
            import datetime
            timestamp = datetime.datetime.now().isoformat()

            data_to_save = {
                "timestamp": timestamp,
                "questions": parsed_questions
            }

            result = self.file_server.write_file("interview_questions.json", json.dumps(data_to_save, indent=2))
            if result.get("success"):
                print(f"💾 Questions saved to interview_questions.json successfully!")
                return "Questions saved successfully"
            else:
                return f"Error saving questions: {result.get('error')}"
        except Exception as e:
            return f"Error processing/saving questions: {str(e)}"
# Test the Question Generator Agent
if __name__ == "__main__":
    question_gen = QuestionGeneratorAgent()

    print("❓ Testing Question Generator Agent...")
    result = question_gen.run(
        "Generate interview questions for a Software Engineer position at Google. "
        "Load the research data first, then create both technical and behavioral questions."
    )
    print(f"Generated questions:\n{result}")