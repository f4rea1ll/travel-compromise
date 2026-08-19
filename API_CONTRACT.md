# API Contract — Travel Compromise

Base URL (dev): `http://localhost:8000`

## POST /session/create
Создаёт новую сессию на двоих.

**Response 200:**
```json
{
  "session_id": "a1b2c3d4",
  "participant_1_link": "/session/a1b2c3d4/join/1",
  "participant_2_link": "/session/a1b2c3d4/join/2"
}
```

## POST /session/{session_id}/join/{participant_number}
Отправка данных одного участника. `participant_number` — 1 или 2.

**Request body:**
```json
{
  "origin_city": "Москва",
  "budget": 15000,
  "vibe_tags": ["chill", "food"],
  "must_haves": ["no_transfers"],
  "departure_date": "2026-09-05",
  "return_date": "2026-09-07"
}
```
`vibe_tags` — из списка: `chill`, `adventure`, `culture`, `food`, `nature`, `budget`
`must_haves` — из списка: `no_transfers`, `budget_stay`, `food_nearby`

**Response 200:**
```json
{"status": "ok", "message": "Данные участника 1 сохранены"}
```

## GET /session/{session_id}/status
Проверка, кто уже заполнил анкету (без раскрытия данных).

**Response 200:**
```json
{
  "session_id": "a1b2c3d4",
  "participant_1_submitted": true,
  "participant_2_submitted": false
}
```

## GET /session/{session_id}/result
Возвращает топ-3 направления с разбивкой по каждому участнику. Требует, чтобы оба участника уже отправили анкету.

**Response 200:**
```json
{
  "session_id": "a1b2c3d4",
  "matches": [
    {
      "city": "Ярославль",
      "total_score": 1.6,
      "participant_1": {
        "transport_price": 805.0,
        "within_budget": true,
        "vibe_match": 0.5
      },
      "participant_2": {
        "transport_price": 2903.38,
        "within_budget": true,
        "vibe_match": 0.5
      }
    }
  ]
}
```

**Response 400:** если один из участников ещё не заполнил анкету.
**Response 404:** если не найдено ни одного подходящего направления.