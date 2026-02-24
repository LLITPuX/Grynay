# Патерни Міркувань для Графа Пам'яті Grynya

> Цей ресурс є Grynya-адаптованою версією generic `references/reasoning-patterns.md`.
> Для ширшої теоретичної перспективи див. `references/reasoning-patterns.md`.

## Для Чого

Граф Grynya — це граф пам'яті AI-агента. Він відрізняється від класичних Knowledge Graphs тим, що:
- Зберігає **хронологію** взаємодій (сесії, запити, відповіді, аналізи)
- Має **тимчасову вісь** (`[:NEXT]`, `[:HAPPENED_AT]`, `:Day`, `:Year`)
- Містить **самоаналіз** агента (`:Analysis` з `verdict`, `errors`, `lessons`)
- Пов'язує все через **сутності** (`:Entity` — технології, концепти, проєкти)

Патерни міркувань нижче адаптовані саме під цю структуру.

## Патерн 1: Темпоральний Трейсинг (Temporal Tracing)

**Задача:** Відновити хронологію подій чи рішень.

**Як працює в Grynya:**
```cypher
// Хронологічний ланцюг подій конкретної сесії
MATCH path = (s:Session {id: 'session_005'})-[:NEXT*]->(event)
WHERE event:Request OR event:Response OR event:Feedback OR event:Analysis
RETURN [n IN nodes(path) | {id: n.id, type: labels(n)[0]}] AS chain
```

**Застосування:**
- "Як розвивалася дискусія про X?" → пройди NEXT-ланцюг сесії
- "Коли було прийнято рішення Y?" → знайди Analysis з відповідним verdict
- "Які помилки агент допустив у минулій сесії?" → фільтруй Analysis де `errors <> ''`

## Патерн 2: Сесійний Пошук (Session-Based Retrieval)

**Задача:** Знайти всі знання, пов'язані з конкретною темою/сесією.

**Як працює в Grynya:**
```cypher
// Повний контекст сесії: всі вузли та їхні сутності
MATCH (s:Session {id: 'session_006'})<-[:PART_OF]-(node)
OPTIONAL MATCH (node)-[:MENTIONS]->(e:Entity)
RETURN node.id, labels(node)[0] AS type, 
       COLLECT(DISTINCT e.name) AS entities
ORDER BY node.id
```

**Застосування:**
- "Що ми обговорювали у сесії про MCP?" → пошук Session за topic
- "Покажи всі рішення поточної сесії" → фільтруй Response та Analysis
- "Які Entity згадувалися найчастіше?" → агрегація MENTIONS

## Патерн 3: Крос-Сесійний Аналіз (Cross-Session Entity Linking)

**Задача:** Виявити зв'язки між сесіями через спільні сутності.

**Як працює в Grynya:**
```cypher
// Знайти сесії, що мають спільну Entity
MATCH (s1:Session)-[:INVOLVES]->(e:Entity)<-[:INVOLVES]-(s2:Session)
WHERE s1.id < s2.id
RETURN s1.id, s2.id, COLLECT(e.name) AS shared_entities
ORDER BY SIZE(COLLECT(e.name)) DESC
```

**Застосування:**
- "Де ще згадувався FalkorDB?" → знайди всі сесії з ent_falkordb
- "Які теми пов'язані між собою?" → граф спільних Entity
- "Яке рішення зі старої сесії релевантне зараз?" → крос-reference через Entity

## Патерн 4: Рефлексивний Аналіз (Self-Analysis Pattern)

**Задача:** Витягти уроки та помилки агента для покращення.

**Як працює в Grynya:**
```cypher
// Всі помилки та уроки з усіх сесій
MATCH (a:Analysis) WHERE a.errors <> '' AND a.errors IS NOT NULL
RETURN a.id, a.errors, a.lessons, a.verdict
ORDER BY a.id
```

**Застосування:**
- "Які помилки агент повторює?" → агрегація errors з усіх Analysis
- "Чи покращується якість відповідей?" → тренд verdict по часу
- "Які правила агент ігнорує?" → аналіз rules_used vs rules_ignored

## Патерн 5: Ланцюг Рішень (Decision Chain)

**Задача:** Відстежити, як формувалося конкретне архітектурне рішення.

**Як працює в Grynya:**
```cypher
// Ланцюг: Feedback → Response → Analysis для конкретної теми
MATCH (e:Entity {name: 'ProtocolTriad'})<-[:MENTIONS]-(node)
OPTIONAL MATCH (node)-[:RESPONDS_TO]->(trigger)
RETURN node.id, labels(node)[0] AS type, 
       trigger.id AS triggered_by,
       CASE WHEN node:Response THEN node.summary ELSE node.text END AS content
ORDER BY node.id
```

**Застосування:**
- "Чому ми обрали таку архітектуру?" → знайди Entity → сесії → рішення
- "Хто запропонував підхід X?" → Request.author + Entity зв'язки
- "Як змінювалося бачення проекту?" → хронологія Entity.description по сесіях

## Порівняння з Generic Reasoning Patterns

| Generic Патерн | Grynya Аналог | Відмінність |
|---------------|---------------|-------------|
| Multi-Step Chain Validation | Темпоральний Трейсинг | Ланцюг — це NEXT-зв'язки, не абстрактні reasoning steps |
| Pattern Matching | Сесійний Пошук | Шаблон — це структура Session→Event→Entity |
| Hypothesis Verification | Рефлексивний Аналіз | Верифікація — це перевірка Analysis.verdict |
| Causal Reasoning | Ланцюг Рішень | Причинність — це Feedback→Response→Analysis |

## Обмеження Поточної Моделі

1. **Немає RAG-шару:** Grynya поки не використовує vector similarity — тільки структурний пошук по графу
2. **Немає Knowledge Extraction з документів:** Сутності витягуються тільки з діалогу, не з файлів проєкту
3. **Однорівневий граф:** Немає розділення trust layers (все в одному рівні довіри)

Ці обмеження — відомі та заплановані для усунення у майбутніх ітераціях.
