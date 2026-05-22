# pip install -qU langchain "langchain[google-genai]"
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model="google_genai:gemini-2.5-flash-lite",
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
    checkpointer=InMemorySaver(),
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]},
   {"configurable": {"thread_id": "1"}},
)
print(result["messages"][-1].content_blocks)


chat_history=[]

agent_response = agent.invoke({"messages": chat_history}, {"configurable": {"thread_id": "1"}})
chat_history.append({"role": "assistant", "content": agent_response})
