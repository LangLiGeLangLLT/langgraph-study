"""
使用 BGE-M3 向量化模型配置 InMemoryStore 以进行语义搜索
"""

from langchain_openai.embeddings import OpenAIEmbeddings
from langgraph.store.memory import InMemoryStore

from dotenv import load_dotenv

load_dotenv()

embeddings = OpenAIEmbeddings(model="BAAI/bge-m3")

store_with_semantic_search = InMemoryStore(
    index={
        "embed": embeddings.embed_documents,
        "dims": 1024,
        "fields": ["memory_content"],
    }
)

store_with_semantic_search.put(
    ("user_789", "food_memories"),
    "memory_1",
    {"memory_content": "我真的很喜欢辛辣的印度咖喱。"},
)

store_with_semantic_search.put(
    ("user_789", "system_metadata"),
    "memory_2",
    {"memory_content": "用户入职已完成。", "status": "completed"},
    index=False,
)

store_with_semantic_search.put(
    ("user_789", "restaurant_reviews"),
    "memory_3",
    {
        "memory_content": "服务很慢，但食物很好。",
        "context": "对 'The Italian Place' 餐厅的评论",
    },
    index=["context"],
)

search_query = "该用户喜欢哪种食物？"
semantic_memory_results = store_with_semantic_search.search(
    ("user_789", "food_memories"), query=search_query, limit=2
)

print("查询的语义搜索结果：", search_query)
for record in semantic_memory_results:
    print(f"记忆键：{record.key}，相似度评分：{record.score}")
    print(f"记忆内容：{record.value}")
    print("=" * 30)
