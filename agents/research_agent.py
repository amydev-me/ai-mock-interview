# agents/research_agent.py (Fixed version)
from langchain.tools import Tool
from agents.base_agent import BaseAgent
from mcp_servers.file_server import FileSystemMCPServer
from typing import Dict, Any
import json
import datetime

class ResearchAgent(BaseAgent):
    """Agent that researches companies and job roles"""

    def __init__(self):
        # Initialize MCP server
        self.file_server = FileSystemMCPServer()

        # Create tools
        tools = [
            Tool(
                name="search_company_info",
                description="Search for basic company information. Input should be the company name.",
                func=self._search_company_info
            ),
            Tool(
                name="save_research_data",
                description="Save research data to file. Input should be the JSON research data.",
                func=self._save_research_data
            ),
            Tool(
                name="load_research_data",
                description="Load company and role research data from 'research_data.json'. This data is crucial for tailoring questions. Returns a JSON string of the research data. No input is required for this tool.",
                func=self._load_research_data,
                args_schema=None  # <-- THIS IS CRITICAL
            ),
        ]

        system_prompt = """
        You are a Research Agent specialized in gathering information about companies and job roles.

        IMPORTANT: You MUST follow this exact process:
        1. Use search_company_info tool to find company information
        2. Use save_research_data tool to save the results
        3. Return a summary of what you found and saved

        When the user asks to research a company, extract the company name and use search_company_info first.
        Then immediately save the results using save_research_data.

        Example:
        User: "Research Google for Software Engineer"
        1. Call search_company_info with "Google"
        2. Call save_research_data with the returned company data
        3. Provide summary
        """

        super().__init__(
            agent_name="research_agent",
            system_prompt=system_prompt,
            tools=tools
        )

    def _search_company_info(self, company_name: str) -> str:
        """Search for company information"""
        print(f"🔍 Searching for company: {company_name}")

        company_data = {
            "google": {
                "name": "Google",
                "culture": "Innovation-focused, data-driven, collaborative",
                "values": "Focus on user, think big, strive for excellence",
                "interview_style": "Technical coding rounds, system design, behavioral",
                "recent_news": "Focus on AI and machine learning initiatives",
                "role_requirements": "Strong coding skills, system design knowledge, problem-solving"
            },
            "netflix": {
                "name": "Netflix",
                "culture": "High performance, freedom and responsibility",
                "values": "People over process, innovation, impact",
                "interview_style": "Behavioral questions, technical skills, culture fit",
                "recent_news": "Expanding globally, investing in original content",
                "role_requirements": "Scalability mindset, high-performance culture fit"
            },
            "amazon": {
                "name": "Amazon",
                "culture": "Customer obsession, ownership, invent and simplify",
                "values": "Leadership principles, customer first, long-term thinking",
                "interview_style": "Behavioral questions based on leadership principles, technical rounds",
                "recent_news": "AWS growth, sustainability initiatives",
                "role_requirements": "Leadership principles alignment, scalability focus"
            },
            "default": {
                "name": "Tech Company",
                "culture": "Innovation and collaboration focused",
                "values": "Quality, teamwork, continuous learning",
                "interview_style": "Mix of technical and behavioral questions",
                "recent_news": "Growing and hiring",
                "role_requirements": "Strong technical skills, team collaboration"
            }
        }

        # Find matching company
        company_key = company_name.lower().strip()
        for key in company_data.keys():
            if key in company_key or company_key in key:
                result = company_data[key]
                print(f"✅ Found data for: {result['name']}")
                return json.dumps(result, indent=2)

        # Default fallback
        result = company_data["default"]
        result["name"] = company_name  # Use the provided name
        print(f"✅ Using default template for: {company_name}")
        return json.dumps(result, indent=2)

    def _save_research_data(self, data: str) -> str:
        """Save research data to file"""
        try:
            # Parse the data if it's JSON string
            if data.startswith('{'):
                parsed_data = json.loads(data)
            else:
                parsed_data = {"raw_data": data}

            # Add timestamp
            import datetime
            timestamp = datetime.datetime.now().isoformat()

            research_record = {
                "timestamp": timestamp,
                "company_data": parsed_data
            }

            result = self.file_server.write_file(
                "research_data.json",
                json.dumps(research_record, indent=2)
            )

            if result.get("success"):
                print(f"💾 Research data saved successfully!")
                return f"✅ Research data saved successfully at {timestamp}"
            else:
                return f"❌ Error saving data: {result.get('error')}"

        except Exception as e:
            return f"❌ Error processing data: {str(e)}"

    def _load_research_data(self, filename: str = "research_data.json") -> str:  # Keep 'filename' here
        """Load research data from file"""
        filename = "research_data.json"  # Force it to look for this specific file
        result = self.file_server.read_file(filename)
        if result.get("success"):
            print("💾 Research data loaded successfully by QGA.")  # Added print for debug
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


# Test the fixed Research Agent
if __name__ == "__main__":
    research_agent = ResearchAgent()

    print("🔍 Testing Fixed Research Agent...")
    result = research_agent.run("Research Google for a Software Engineer position")
    print(f"\nAgent Response:\n{result}")

    # Check the saved file
    import os

    file_path = "data/research_data.json"
    if os.path.exists(file_path):
        print(f"\n📄 Checking saved file: {file_path}")
        with open(file_path, "r") as f:
            content = f.read()
            print(f"File contents:\n{content}")
    else:
        print(f"\n❌ File not found: {file_path}")