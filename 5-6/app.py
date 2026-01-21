"""
使用 put 方法保存记忆
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
