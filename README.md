# Keklik API 

[![Build Status](https://travis-ci.com/kiryanenko/keklik-api.svg?branch=master)](https://travis-ci.com/kiryanenko/keklik-api)

**API:** http://api.keklik.xyz

**Dev API:** https://keklik-api.herokuapp.com

# WebSocket API

## Общий порядок

1. Установить WebSocket соединение `ws://api.keklik.xyz/?session_key=<КЛЮЧ_СЕССИИ>`
2. Подписаться на издателей *(подписки, события, экшены, сигналы)*

    **Запрос:**
    
    ```json
    {
      "stream": "games",
      "payload": {
        "action": "subscribe",
        "pk": 1,
        "data": {
          "action": "Название экшена"
        },
        "request_id": "Идентификатор запроса (не обязательно)"
      }
    }
    ```
    
    **Ответ:**
    
    ```json
    {
      "stream": "games", 
      "payload": {
        "errors": [], 
        "data": {"action": "Название экшена"}, 
        "action": "subscribe", 
        "response_status": 200, 
        "request_id": "Идентификатор запроса"
      }
    }
    ```
    
3. Следить за приходом сообщений от издателей *(событий)*

    **Рассылка:**
    
    ```json
    {
      "stream": "games",
      "payload": {
        "action": "Название экшена",
        "pk": 1,
        "data": {}, 
        "model": "api.game"
      }
    }
    ```

## Экшены (запросы)

### Присоединиться к игре `join`

**Запрос:**

```json
{
  "stream": "games",
  "payload": {
    "action": "join",
    "pk": 1,
    "request_id": "Идентификатор запроса (не обязательно)"
  }
}
```

**Ответ:**

```json
{
  "stream": "games",
  "payload": {
    "errors": [], 
    "data": GAME_SNAPSHOT, 
    "action": "join", 
    "response_status": 200, 
    "request_id": "Идентификатор запроса"
  }
}
```

### Следующий вопрос `next_question`

**Запрос:**

```json
{
  "stream": "games",
  "payload": {
    "action": "next_question",
    "pk": 1,
    "request_id": "Идентификатор запроса (не обязательно)"
  }
}
```

**Ответ:**

```json
{
  "stream": "games",
  "payload": {
    "errors": [], 
    "data": GAME_SNAPSHOT, 
    "action": "next_question", 
    "response_status": 200, 
    "request_id": "Идентификатор запроса"
  }
}
```


### Сменить состояние на проверку ответов `check`

**Запрос:**

```json
{
  "stream": "games",
  "payload": {
    "action": "check",
    "pk": 1,
    "request_id": "Идентификатор запроса (не обязательно)"
  }
}
```

**Ответ:**

```json
{
  "stream": "games",
  "payload": {
    "errors": [], 
    "data": {
      "id": 6,
      "question": "string",
      "number": 1,
      "type": "single",
      "variants": [
        {
          "id": 32,
          "variant": "string"
        }
      ],
      "answer": [32],
      "players_answers": [],
      "timer": "00:00:00",
      "points": 10
    }, 
    "action": "check", 
    "response_status": 200, 
    "request_id": "Идентификатор запроса"
  }
}
```


## Подписки

### Обновление снапшота игры `update`

**Запрос:**

```json
{
  "stream": "games",
  "payload": {
    "action": "subscribe",
    "pk": 1,
    "data": {
      "action": "update"
    }
  }
}
```

**Рассылка:**

```json
{
  "stream": "games", 
  "payload": {
    "action": "join", 
    "pk": 1, 
    "data": GAME_SNAPSHOT, 
    "model": "api.game"
  }
}
```

### Присоединился игрок `join`

**Запрос:**

```json
{
  "stream": "games",
  "payload": {
    "action": "subscribe",
    "pk": 1,
    "data": {
      "action": "join"
    }
  }
}
```

**Рассылка:**

```json
{
  "stream": "games", 
  "payload": {
    "action": "join", 
    "pk": 1, 
    "data": {
      "id": 1, 
      "user": {
        "username": "string", "email": "", "phone": "", 
        "last_name": "", "first_name": "", "patronymic": "", 
        "gender": "", "birth_date": null, 
        "rating": 0
      }, 
      "created_at": "2018-10-16T20:18:34.007352Z", 
      "finished_at": null
    }, 
    "model": "Player"
  }
}
```

### Следующий вопрос `next_question`

**Запрос:**

```json
{
  "stream": "games",
  "payload": {
    "action": "subscribe",
    "pk": 1,
    "data": {
      "action": "next_question"
    }
  }
}
```

**Рассылка:**

```json
{
  "stream": "games", 
  "payload": {
    "action": "next_question", 
    "pk": 1, 
    "data": GAME_SNAPSHOT, 
    "model": "api.game"
  }
}
```


### Состояние проверки ответа `check`

**Запрос:**

```json
{
  "stream": "games",
  "payload": {
    "action": "subscribe",
    "pk": 1,
    "data": {
      "action": "check"
    }
  }
}
```

**Рассылка:**

```json
{
  "stream": "games", 
  "payload": {
    "action": "next_question", 
    "pk": 1, 
    "data": {
      "id": 6,
      "question": "string",
      "number": 1,
      "type": "single",
      "variants": [
        {
          "id": 32,
          "variant": "string"
        }
      ],
      "answer": [32],
      "players_answers": [],
      "timer": "00:00:00",
      "points": 10
    }, 
    "model": "api.generated_question"
  }
}
```


### Завершение игры `finish`

**Запрос:**

```json
{
  "stream": "games",
  "payload": {
    "action": "subscribe",
    "pk": 1,
    "data": {
      "action": "finish"
    }
  }
}
```

**Рассылка:**

```json
{
  "stream": "games", 
  "payload": {
    "action": "finish", 
    "pk": 1, 
    "data": GAME_SNAPSHOT, 
    "model": "api.game"
  }
}
```
