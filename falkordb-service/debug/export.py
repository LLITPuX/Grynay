import json
from falkordb import FalkorDB

db = FalkorDB(host='falkordb', port=6379)
graph = db.select_graph('Grynya')
query = """
MATCH (n)-[rel:HAPPENED_AT]->(d:Day) 
WHERE (n)-[:PART_OF]->(:Session {id: 'session_002'}) 
AND NOT 'Analysis' IN labels(n)
AND NOT 'Entity' IN labels(n)
RETURN labels(n)[0] as type, n.id as id, n.author as author, n.text as text, n.full_text as full_text, rel.time as time 
ORDER BY rel.time
"""
res = graph.query(query)

out = []
out.append("# Сесія: mcp_server_spec_discovery\n")
out.append("**Дата:** 2026-02-23\n**Тема:** mcp_server_spec_discovery\n")
out.append("---\n")

for row in res.result_set:
    node_type = row[0]
    author = row[2]
    time = row[5]
    if node_type in ['Request', 'Feedback']:
        text = row[3] if row[3] else ""
        out.append(f"## {node_type} [{time}]")
        out.append(f"```\n{text}\n```")
    elif node_type == 'Response':
        full_text = row[4] if row[4] else ""
        out.append(f"### Відповідь агента [{time}]")
        out.append(f"{full_text}")
        out.append("\n---\n")

sum_query = "MATCH (n:Analysis)-[:SUMMARIZES]->(:Session {id: 'session_002'}) RETURN n.topics, n.tasks_completed, n.key_decisions, n.errors, n.lessons"
sum_res = graph.query(sum_query)
if sum_res.result_set:
    s = sum_res.result_set[0]
    out.append("## Підсумок сесії\n")
    out.append(f"### Обговорені теми:\n{s[0] or ''}\n")
    out.append(f"### Виконані завдання:\n{s[1] or ''}\n")
    out.append(f"### Ключові рішення:\n{s[2] or ''}\n")
    out.append(f"### Помилки:\n{s[3] or ''}\n")
    out.append(f"### Уроки:\n{s[4] or ''}\n")

out.append("\n---\n**Кінець сесії**\n")

with open('/tmp/log.md', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))
