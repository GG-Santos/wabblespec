# LangChain Framework

Loaded by Apply when langchain is detected in dependencies.

## Version baseline

LangChain 0.3.x (Python) or LangChain.js 0.3.x. LangChain 0.3 removed deprecated APIs from 0.1/0.2 — declare which version is in use.

## Core primitives

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Model
model = ChatAnthropic(model="claude-sonnet-4-6")

# Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{input}"),
])

# Chain (LCEL — LangChain Expression Language)
chain = prompt | model | StrOutputParser()

# Invoke
result = chain.invoke({"input": "What is 2+2?"})
```

## LCEL (LangChain Expression Language)

LCEL chains are lazy: `prompt | model | parser` creates a Runnable that is not executed until `.invoke()`, `.stream()`, or `.batch()` is called.

```python
# Parallel execution
from langchain_core.runnables import RunnableParallel

chain = RunnableParallel(
    summary=summarize_chain,
    keywords=keyword_chain,
)
result = chain.invoke(document)
# result: {"summary": "...", "keywords": [...]}

# Conditional routing
from langchain_core.runnables import RunnableBranch

router = RunnableBranch(
    (lambda x: x["type"] == "question", question_chain),
    (lambda x: x["type"] == "command", command_chain),
    default_chain,
)
```

## Structured output

```python
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic

class Sentiment(BaseModel):
    label: Literal["positive", "negative", "neutral"]
    confidence: float
    reasoning: str

model = ChatAnthropic(model="claude-sonnet-4-6")
structured_model = model.with_structured_output(Sentiment)

result: Sentiment = structured_model.invoke("I love this product!")
```

Prefer structured output over string parsing — it uses the model's tool-use to guarantee schema compliance.

## Retrieval (RAG)

```python
from langchain_community.vectorstores import Chroma
from langchain_anthropic import AnthropicEmbeddings

# Build index
vectorstore = Chroma.from_documents(documents, AnthropicEmbeddings())

# Retrieve + generate
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)
```

Spec must declare: embedding model, vector store, retrieval strategy (similarity, MMR), and k value.

## Tools and agents

```python
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor

@tool
def search_web(query: str) -> str:
    """Search the web for current information."""
    return search_api.search(query)

agent = create_tool_calling_agent(model, [search_web], prompt)
executor = AgentExecutor(agent=agent, tools=[search_web], max_iterations=5)
result = executor.invoke({"input": "What is the current date?"})
```

Spec must declare: all tools available to the agent, max_iterations, and what happens at iteration limit.

## Observability — LangSmith

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "..."
os.environ["LANGCHAIN_PROJECT"] = "my-project"
```

With tracing enabled, all chain invocations are logged to LangSmith. Spec must declare: whether LangSmith is used; if not, what alternative observability is in place.

## Anti-patterns

- Do not use deprecated chain classes (`LLMChain`, `ConversationalRetrievalChain`) — use LCEL
- Do not pass user input directly into prompt templates without sanitization
- Do not use `max_iterations` > 10 without explicit justification in spec
- Do not use `verbose=True` in production — it logs to stdout, not structured logs
