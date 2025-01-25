from smolagents import (
    CodeAgent,
    HfApiModel,
    ManagedAgent,
    DuckDuckGoSearchTool
)
from src.agents.task_gen_agent import TaskGeneratorAgent
from src.agents.environment_generator import EnvironmentGeneratorAgent

def kill_self():
    import sys
    sys.exit(0)

if __name__ == "__main__":
    model = HfApiModel()

    web_agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=model)
    managed_web_agent = ManagedAgent(
        agent=web_agent,
        name="web_search",
        description="Runs web searches for you. Give it your query as an argument."
    )
    manager_agent = CodeAgent(
        tools=[], model=model, managed_agents=[managed_web_agent]
    )

    # Agent set up
    task_gen_agent = TaskGeneratorAgent([], model)
    env_gen_agent = EnvironmentGeneratorAgent([], model)

    # Generate task reqs
    reqs = task_gen_agent.run("")

    print(reqs)
    print(type(reqs))
    kill_self()

    # Create tf deployment
    env_gen_agent.run(reqs)