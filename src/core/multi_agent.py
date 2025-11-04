from crewai import Agent, Task, Crew

from schemas.io_schema import AgentInput, AgentOutput


agents = [
    Agent(role="Decoder", goal="Decode scripts", backstory="Uses DIWA-15"),
    Agent(role="Forecaster", goal="Predict outcomes", backstory="Uses ChronoPredict"),
    Agent(role="Translator", goal="Translate languages", backstory="Uses TranslateGenius"),
]

crew = Crew(agents=agents)


def orchestrate(task: str):
    return crew.run(Task(description=task))
