## Initial

```bash
python -m venv .venv

.venv\Scripts\activate

pip freeze > requirements.txt

pip install -r requirements.txt

pip install python-dotenv
pip install jupyter
pip install langgraph langchain-openai
pip install langchain_community
pip install langgraph-prebuilt
pip install langgraph-checkpoint-sqlite
pip install psycopg psycopg-pool langgraph-checkpoint-postgres
pip install pymongo langgraph-checkpoint-mongodb
pip install trustcall
pip install langmem
pip install langgraph-supervisor
pip install langgraph-swarm
```

## ENV

```python
from dotenv import load_dotenv

load_dotenv()
```

## LLM

```python
ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct", temperature=0)
ChatOpenAI(model="Qwen/Qwen3-8B", temperature=0)
OpenAIEmbeddings(model="BAAI/bge-m3")
```

```python
import os
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(
    model="qwen3-max-2026-01-23",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0,
)
```
