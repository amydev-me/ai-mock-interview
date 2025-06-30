# workflows/basic_workflow.py (Updated version)
from langgraph.graph import Graph, END
from agents.research_agent import ResearchAgent
from agents.question_generator import QuestionGeneratorAgent
from typing import Dict, Any


class InterviewPrepWorkflow:
    """Basic workflow that connects Research and Question Generator agents"""

    def __init__(self):
        self.research_agent = ResearchAgent()
        self.question_generator = QuestionGeneratorAgent()
        self.workflow = self._create_workflow()

    def _create_workflow(self):
        """Create the LangGraph workflow"""

        def research_step(state: Dict[str, Any]) -> Dict[str, Any]:
            """Research company and role"""
            query = state.get("user_input", "")
            print(f"🔍 Research Agent working on: {query}")

            # More explicit instruction to save data
            research_result = self.research_agent.run(
                f"Research {query}. "
                f"First use search_company_info to find information, "
                f"then use save_research_data to save the results to a file."
            )

            return {
                **state,
                "research_complete": True,
                "research_result": research_result
            }

        def question_generation_step(state: Dict[str, Any]) -> Dict[str, Any]:
            """Generate questions based on research"""
            query = state.get("user_input", "")
            print(f"❓ Question Generator working on: {query}")

            questions_result = self.question_generator.run(
                f"Generate interview questions for {query}. "
                "First load research data using load_research_data, "
                "then create technical and behavioral questions based on that data."
            )

            return {
                **state,
                "questions_complete": True,
                "questions_result": questions_result
            }

        def should_continue(state: Dict[str, Any]) -> str:
            """Determine next step"""
            if not state.get("research_complete", False):
                return "research"
            elif not state.get("questions_complete", False):
                return "questions"
            else:
                return END

        # Create workflow graph
        workflow = Graph()

        # Add nodes
        workflow.add_node("research", research_step)
        workflow.add_node("questions", question_generation_step)

        # Add edges
        workflow.add_conditional_edges(
            "research",
            should_continue,
            {
                "questions": "questions",
                END: END
            }
        )

        workflow.add_conditional_edges(
            "questions",
            should_continue,
            {
                END: END
            }
        )

        # Set entry point
        workflow.set_entry_point("research")

        return workflow.compile()

    def run(self, user_input: str) -> Dict[str, Any]:
        """Run the complete workflow"""
        initial_state = {
            "user_input": user_input,
            "research_complete": False,
            "questions_complete": False
        }

        print(f"🚀 Starting workflow for: {user_input}")
        result = self.workflow.invoke(initial_state)

        # Check if files were created
        import os
        print(f"\n📁 File check:")
        print(f"   research_data.json exists: {os.path.exists('data/research_data.json')}")
        print(f"   interview_questions.json exists: {os.path.exists('data/interview_questions.json')}")

        return result


# Test the workflow
if __name__ == "__main__":
    workflow = InterviewPrepWorkflow()

    # Test the complete workflow
    result = workflow.run("Google Software Engineer position")

    print("\n" + "=" * 50)
    print("📋 WORKFLOW COMPLETED")
    print("=" * 50)
    print(f"✅ Research Complete: {result.get('research_complete')}")
    print(f"✅ Questions Complete: {result.get('questions_complete')}")