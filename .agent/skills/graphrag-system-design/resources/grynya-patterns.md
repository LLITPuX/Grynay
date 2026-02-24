# Патерни Проєктування Графа Grynya

> Цей ресурс є Grynya-адаптованою версією generic `references/domain-patterns.md`.
> Для порівняння з іншими доменами див. `references/domain-patterns.md` (Enterprise секція).

## Основний Патерн: Activity-Centric Memory Agent

Grynya використовує патерн **Activity-Centric Knowledge Graph**, адаптований з Enterprise domain:
активність (взаємодія агента з користувачем) є першокласною сутністю, що з'єднує людей, артефакти та рішення.

```
(:Session)─[:NEXT]─>(:Session)             ← Хронологія сесій
    │
    ├─[:PART_OF]── (:Request)               ← Запит користувача
    │                  │
    │                  └─[:NEXT]─> (:Response) ← Відповідь агента
    │                                  │
    │                                  └─[:NEXT]─> (:Analysis) ← Самоаналіз
    │
    ├─[:INVOLVES]── (:Entity)               ← Сутності теми
    │
    ├─[:LAST_EVENT]── (останній вузол)      ← Поточна позиція
    │
    └─[:HAPPENED_AT]── (:Day)─[:MONTH]── (:Year) ← Хронологія

```

## Патерн 1: Хронологічний Ланцюг (Temporal Chain)

**Суть:** Усі вузли всередині сесії з'єднані `[:NEXT]`, формуючи строгий хронологічний ланцюг. Сесії також з'єднані `[:NEXT]` між собою.

**Навіщо:**
- Відтворення контексту: агент може "пройти" весь діалог
- Верифікація цілісності: розрив ланцюга = помилка протоколу
- Темпоральний пошук: "що було перед/після цього рішення?"

**Правила реалізації:**
1. `[:NEXT]` session_N → session_N+1 (верифікація при `/db`)
2. `[:NEXT]` всередині сесії: Request → Response → Analysis → Feedback → Response → Analysis...
3. `[:LAST_EVENT]` ЗАВЖДИ вказує на останній Analysis (Правило Тріади)

## Патерн 2: Тріада Вузлів (Node Triad)

**Суть:** Кожна взаємодія створює рівно три вузли — ніколи менше.

```
/db → Request + Response + Analysis
/sa → Feedback + Response + Analysis
/ss → (Feedback) + Response + Analysis (session_summary)
```

**Навіщо:**
- Граф ніколи не залишається в "проміжному" стані
- Кожен Response має Analysis — агент завжди рефлексує
- LAST_EVENT надійно вказує на фінальний вузол тріади

**Наслідки для схеми:**
- Response без Analysis = помилка протоколу (CAUTION в SKILL.md)
- Analysis.type: `response_analysis` (для /db, /sa) або `session_summary` (для /ss)

## Патерн 3: Entity Extraction та Linking

**Суть:** Сутності (`:Entity`) — це "мости" між сесіями. Їх витяг — безперервний процес.

**Правила:**
1. Session `[:INVOLVES]` Entity — зв'язок на рівні теми
2. Request/Response/Feedback/Analysis `[:MENTIONS]` Entity — зв'язок на рівні конкретного повідомлення
3. Entity.id має бути стабільним: `ent_falkordb`, не `ent_001`
4. Entity.name: CamelCase (`FalkorDB`, `ProtocolTriad`)
5. Entity.type: `Technology`, `Concept`, `Project`, `Person`, `Rule`
6. Дублікати Entity — це помилка. Перед створенням перевіряй чи вже існує.

**Entity Resolution (ручний, на рівні агента):**
```cypher
// Перед створенням перевір
MATCH (e:Entity) WHERE e.name = 'FalkorDB' RETURN e.id
// Якщо існує — використай наявний id замість створення нового
```

## Патерн 4: Multi-Source Integration (Майбутнє)

**Поточний стан:** Єдине джерело — діалог агента з користувачем.

**Планована еволюція:**
```
Рівень 1: Діалоги           ← ЗАРАЗ
Рівень 2: + Файли проєкту    ← Entity Extraction з .md, .py, .json
Рівень 3: + Зовнішні API     ← GitHub Issues, CI/CD результати
Рівень 4: + Multi-Agent       ← Gemini CLI, інші агенти пишуть у той самий граф
```

**Наслідки для схеми:**
- Потрібен `source` атрибут на вузлах (dialog / file / api / agent_name)
- Entity Resolution стане критичним при множинних джерелах
- Потрібен Trust Layer: діалогові дані vs автоматично витягнуті

## Патерн 5: Self-Evolving Graph

**Суть:** Граф пам'яті має покращуватися з кожною взаємодією.

**Механізми самопокращення:**
1. **Analysis.lessons** — агент фіксує уроки, які впливають на майбутню поведінку
2. **Entity.description** — оновлюється при кожному новому згадуванні
3. **Аудит** — `grynya-methodology.md` дає чек-лист для виявлення проблем
4. **Schema Evolution** — нові типи вузлів/зв'язків додаються через `grynya-schema.md`

## Порівняння з Enterprise Патернами

| Enterprise Pattern | Grynya Аналог | Адаптація |
|-------------------|---------------|-----------|
| Activity-Centric KG | Session → Events → Entities | Активність = діалогова взаємодія |
| Organizational KG | Entity Network | Сутності = технології, концепти, проєкти |
| Multi-Source Integration | Поки лише діалог | Плановано: файли, API, мульти-агенти |
| Compliance & Audit | Analysis + HAPPENED_AT | Самоаналіз замість regulatory compliance |

## Анти-Патерни (Чого Уникати)

1. ❌ **Flat Log** — зберігати лише текст без структури → втрата зв'язків
2. ❌ **Entity per Message** — створювати окрему Entity для кожної згадки → дублікати
3. ❌ **Skip Analysis** — пропускати Analysis для "простих" відповідей → розрив тріади
4. ❌ **Orphan Sessions** — сесії без NEXT-зв'язку → розрив хронології
5. ❌ **Generic IDs** — `ent_001` замість `ent_falkordb` → нечитабельний граф
