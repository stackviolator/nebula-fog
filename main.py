from smolagents import (
    CodeAgent,
    HfApiModel,
    ManagedAgent,
    DuckDuckGoSearchTool,
    OpenAIServerModel
)
from src.agents.task_gen_agent import TaskGeneratorAgent
from src.agents.environment_generator import EnvironmentGeneratorAgent, ValidateTerraformConfig, DeployTerraformToAws
import os

def kill_self():
    import sys
    sys.exit(0)

if __name__ == "__main__":
    hf_model = HfApiModel()
    openai_model = OpenAIServerModel(
        model_id="gpt-4o",
        api_base="https://api.openai.com/v1",
        api_key=os.environ["OPENAI_API_KEY"],
    )

    web_agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=hf_model)
    managed_web_agent = ManagedAgent(
        agent=web_agent,
        name="web_search",
        description="Runs web searches for you. Give it your query as an argument."
    )
    manager_agent = CodeAgent(
        tools=[], model=hf_model, managed_agents=[managed_web_agent]
    )

    # Agent set up
    task_gen_agent = TaskGeneratorAgent([], hf_model)
    env_gen_agent = EnvironmentGeneratorAgent([], openai_model)

    # Generate task reqs
    reqs = task_gen_agent.run("")

    # Create tf deployment
    env_gen_agent.run(reqs)

    print(ValidateTerraformConfig("./templates/active_directory_network.tf"))
    # print(DeployTerraformToAws("./templates"))