"""
使用 search 和 get 检索记忆
"""

import uuid
from langgraph.store.memory import InMemoryStore

in_memory_store = InMemoryStore()

user_id = "example_user"
namespace_for_user_data = (user_id, "user_info")

memory_key = str(uuid.uuid4())

memory_value = {"user_name": "Example User"}

in_memory_store.put(namespace_for_user_data, memory_key, memory_value)

print(f"记忆已保存，键为{memory_key}，命名空间为{namespace_for_user_data}")


all_user_memories = in_memory_store.search(namespace_for_user_data)
print("命名空间中的所有用户记忆：")
for record in all_user_memories:
    print(record.dict())

retrieved_memory_record = in_memory_store.get(namespace_for_user_data, memory_key)
print(f"\n使用键 '{memory_key}' 检索到的记忆：")
print(retrieved_memory_record.dict())
