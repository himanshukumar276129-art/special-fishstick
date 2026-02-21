# Globle-1 API Documentation

## Overview
The **Globle-1 API** provides unified access to all 16+ AI tiers configured in GlobleXGPT through a single API key. It automatically handles fallback across all providers to ensure maximum uptime and reliability.

## Base URL
```
https://your-domain.com/api/v1
```

## Authentication
All API requests require an API key in the Authorization header:
```
Authorization: Bearer YOUR_API_KEY
```

---

## Endpoints

### 1. Generate API Key (Admin Only)
**POST** `/api/v1/generate-key`

Generate a new API key for external users.

**Request:**
```json
{
  "master_password": "GlobleX2026SecureAdmin!"
}
```

**Response:**
```json
{
  "success": true,
  "api_key": "globle-xxxxxxxxxxxxxxxxxxxxx",
  "message": "API key generated successfully. Store this securely - it won't be shown again.",
  "usage_example": {
    "curl": "...",
    "python": "..."
  }
}
```

---

### 2. Chat Completions (OpenAI Compatible)
**POST** `/api/v1/chat/completions`

Send a chat message and receive AI-generated response.

**Request:**
```json
{
  "model": "globle-1",
  "messages": [
    {
      "role": "user",
      "content": "What is the capital of France?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Response:**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1704067200,
  "model": "globle-1",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of France is Paris."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 8,
    "completion_tokens": 7,
    "total_tokens": 15
  },
  "system_info": {
    "model_used": "Tier 1 (OpenRouter - deepseek/deepseek-r1)",
    "globle_version": "1.0"
  }
}
```

---

### 3. List Models
**GET** `/api/v1/models`

List available models.

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "globle-1",
      "object": "model",
      "created": 1704067200,
      "owned_by": "globlexgpt",
      "description": "Multi-tier AI model with automatic fallback across 16+ providers"
    }
  ]
}
```

---

### 4. API Status (Public)
**GET** `/api/v1/status`

Check API health and availability (no authentication required).

**Response:**
```json
{
  "status": "operational",
  "version": "1.0",
  "model": "globle-1",
  "available_tiers": 16,
  "endpoints": {
    "chat": "/api/v1/chat/completions",
    "models": "/api/v1/models",
    "status": "/api/v1/status"
  }
}
```

---

## Usage Examples

### Python
```python
import requests

API_KEY = "globle-xxxxxxxxxxxxxxxxxxxxx"
API_URL = "https://your-domain.com/api/v1/chat/completions"

response = requests.post(
    API_URL,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "globle-1",
        "messages": [
            {"role": "user", "content": "Explain quantum computing in simple terms"}
        ],
        "temperature": 0.7
    }
)

result = response.json()
print(result['choices'][0]['message']['content'])
```

### cURL
```bash
curl https://your-domain.com/api/v1/chat/completions \
  -H "Authorization: Bearer globle-xxxxxxxxxxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "globle-1",
    "messages": [
      {"role": "user", "content": "Hello, Globle-1!"}
    ]
  }'
```

### JavaScript (Node.js)
```javascript
const axios = require('axios');

const API_KEY = 'globle-xxxxxxxxxxxxxxxxxxxxx';
const API_URL = 'https://your-domain.com/api/v1/chat/completions';

async function chat(message) {
  const response = await axios.post(API_URL, {
    model: 'globle-1',
    messages: [
      { role: 'user', content: message }
    ]
  }, {
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    }
  });
  
  return response.data.choices[0].message.content;
}

chat('What is AI?').then(console.log);
```

---

## Features

✅ **OpenAI Compatible** - Drop-in replacement for OpenAI API  
✅ **16+ Tier Fallback** - Automatic failover across all providers  
✅ **High Availability** - 99.9% uptime with redundant systems  
✅ **Secure Authentication** - SHA-256 hashed API keys  
✅ **Rate Limiting Ready** - Built-in support for usage tracking  
✅ **Real-time Status** - Monitor API health and tier availability  

---

## Error Codes

| Code | Description |
|------|-------------|
| 401  | Missing or invalid Authorization header |
| 403  | Invalid API key |
| 400  | Invalid request format |
| 503  | All AI tiers unavailable |
| 500  | Internal server error |

---

## Rate Limits
- **Free Tier**: 100 requests/day
- **Pro Tier**: Unlimited requests
- **Enterprise**: Custom limits

---

## Support
For API support, contact: support@globlexgpt.com
