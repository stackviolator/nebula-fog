from smolagents import (
    CodeAgent,
    HfApiModel,
    GradioUI,
    DuckDuckGoSearchTool
)

if __name__ == "__main__":
    agent = CodeAgent(
        tools=[], model=HfApiModel(), max_steps=4, verbosity_level=1,
    )
    agent.run("Write a yaml file to deploy a domain controller with windows server 2022")