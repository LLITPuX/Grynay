# Технологічний Стек Grynya

> Цей ресурс є Grynya-адаптованою версією generic `references/technology-stacks.md`.
> Для порівняння з іншими стеками див. `references/technology-stacks.md`.

## Огляд Стеку

Grynya побудована на мінімалістичному, self-hosted стеку без зовнішніх залежностей:

```
┌──────────────────────────────────────────────────────┐
│                  AI Agent (LLM)                      │
│         Claude / Gemini CLI / інший LLM              │
├──────────────────────────────────────────────────────┤
│                MCP Bridge (Python)                   │
│         grynya-bridge Container                      │
│         stdin/stdout JSON ↔ Cypher                   │
├──────────────────────────────────────────────────────┤
│               FalkorDB (RedisGraph fork)             │
│         falkordb Container                           │
│         Cypher + Redis Protocol                      │
├──────────────────────────────────────────────────────┤
│              Docker Compose Network                  │
│         grynya-network                               │
└──────────────────────────────────────────────────────┘
```

## Компоненти

### FalkorDB (Графова БД)

- **Тип:** Property Graph Database (форк RedisGraph)
- **Протокол:** Redis Protocol + GRAPH.QUERY команди
- **Мова запитів:** Cypher (підмножина)
- **Контейнер:** `falkordb/falkordb:latest` → `falkordb`
- **Порт:** 6379 (Redis), 3000 (FalkorDB Browser)

**Можливості:**
- Cypher для створення, читання, оновлення, видалення вузлів та зв'язків
- MERGE для ідемпотентних операцій (запобігає дублікатам)
- Підтримка індексів на атрибутах
- In-memory виконання для швидких запитів

**Обмеження FalkorDB:**
- Немає вбудованого vector search (на відміну від Neo4j 5.11+)
- Немає GDS-бібліотеки (community detection, centrality — потрібно реалізовувати вручну)
- Обмежена підтримка Cypher (деякі Neo4j функції відсутні)
- Однопотокове виконання запитів (Redis-модель)
- Немає вбудованого RBAC (role-based access control)

**Практичні наслідки для графа Grynya:**
- Entity Resolution робиться на рівні агента (перед записом), не на рівні БД
- Community Detection потрібно реалізувати Cypher-запитами або зовнішнім скриптом
- Vector similarity search (для RAG) потребує окремого сервісу в майбутньому

### MCP Bridge (Оркестрація)

- **Тип:** Custom Python pipeline (не LangChain, не LlamaIndex)
- **Протокол:** MCP (Model Context Protocol) — stdin/stdout JSON
- **Контейнер:** `grynya-bridge`
- **Скрипт:** `memory_bridge.py`

**Як працює:**
1. Агент формує JSON payload згідно з `grynya-schema.md`
2. JSON записується у тимчасовий файл → `docker cp` → контейнер
3. `memory_bridge.py` парсить JSON → генерує Cypher → виконує через FalkorDB Python driver
4. Результат повертається через stdout

**Чому Custom Pipeline, а не LangChain:**
- Повний контроль над Cypher-запитами
- Немає overhead фреймворку
- Простота деплою (один Python-скрипт)
- Агент-агностичність (будь-який LLM може сформувати JSON)

### Docker Compose (Інфраструктура)

- **Мережа:** `grynya-network` (bridge)
- **Сервіси:** `falkordb`, `grynya-bridge`
- **Persistence:** Docker volumes для даних FalkorDB
- **Деплой:** Локальний (Windows host)

## Порівняння з Reference Архітектурами

| Аспект | Grynya | Rapid Prototyping (Neo4j) | Production Hybrid |
|--------|--------|---------------------------|-------------------|
| Граф DB | FalkorDB | Neo4j | Neo4j |
| Vector DB | Немає | Neo4j Vector | Pinecone |
| Оркестрація | Custom MCP | LangChain | Custom |
| LLM | Будь-який | GPT-4 | Claude/GPT-4 |
| BД для пошуку | Тільки граф | Граф + вектор | Граф + вектор |
| Складність | Мінімальна | Низька | Висока |

## Плани Розвитку Стеку

1. **Vector Search Layer** — додати Qdrant або pgvector для semantic similarity
2. **Multi-Agent Support** — Gemini CLI як другий агент у тій самій мережі
3. **Індексація** — додати індекси на `id` та `name` для прискорення запитів
4. **Monitoring** — метрики виконання запитів, розмір графа, latency

## Зв'язок зі Схемою

> Еталонна схема графа: `c:\Antigarvity_workspace\.agent\skills\memory-manager\grynya-schema.md`
> Docker Compose: `c:\Antigarvity_workspace\docker-compose.yml`
> MCP Bridge: `c:\Antigarvity_workspace\falkordb-service\scripts\memory_bridge.py`
