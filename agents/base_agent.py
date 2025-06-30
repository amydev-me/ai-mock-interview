# agents/base_agent.py
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from typing import List, Dict, Any
from config import Config


class BaseAgent:
    """Base class for all agents"""

    def __init__(self, agent_name: str, system_prompt: str, tools: List[BaseTool] = None):
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.tools = tools or []

        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE,
            openai_api_key=Config.OPENAI_API_KEY
        )

        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create agent if tools are provided
        if self.tools:
            self.agent = self._create_agent()
        else:
            self.agent = None

    def _create_agent(self):
        """Create the agent with tools"""
        llm_with_tools = self.llm.bind_functions(self.tools)

        agent = (
                {
                    "input": lambda x: x["input"],
                    "agent_scratchpad": lambda x: format_to_openai_function_messages(
                        x["intermediate_steps"]
                    ),
                }
                | self.prompt
                | llm_with_tools
                | OpenAIFunctionsAgentOutputParser()
        )

        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    def run(self, input_text: str) -> str:
        """Run the agent with input"""
        if self.agent:
            result = self.agent.invoke({"input": input_text})
            return result["output"]
        else:
            # Simple LLM call without tools
            messages = self.prompt.format_messages(input=input_text, agent_scratchpad=[])
            result = self.llm.invoke(messages)
            return result.content


# Test the base agent
if __name__ == "__main__":
    # Test simple agent without tools
    test_agent = BaseAgent(
        agent_name="test_agent",
        system_prompt="You are a helpful assistant that answers questions briefly."
    )

    result = test_agent.run("What is Python?")
    print(f"Test result: {result}")