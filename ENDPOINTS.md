# API Endpoints Documentation

## Base URL
- Local Development: `http://localhost:8000`
- Production: Configure as needed

## Endpoints Summary

### Topics Endpoints

#### GET /api/topics/
List all available topics or filter by class level.

**Query Parameters:**
- `class_level` (optional): Filter by class (Class VIII, Class IX, Class X)

**Response:**
```json
[
  {
    "topic_id": "viii_crop_production",
    "topic_name": "Crop Production and Management",
    "class_level": "Class VIII",
    "chapter": "Chapter 1",
    "description": "NCERT Science topic: Crop Production and Management"
  }
]
```

#### GET /api/topics/classes
List all available class levels.

**Response:**
```json
["Class VIII", "Class IX", "Class X"]
```

#### GET /api/topics/{topic_id}
Get specific topic by ID.

**Response:**
```json
{
  "topic_id": "viii_crop_production",
  "topic_name": "Crop Production and Management",
  "class_level": "Class VIII",
  "chapter": "Chapter 1",
  "description": "NCERT Science topic: Crop Production and Management"
}
```

---

### Summary Endpoints

#### POST /api/summary/
Generate a summary for a topic.

**Request Body:**
```json
{
  "topic_id": "viii_crop_production",
  "topic_name": "Crop Production and Management",
  "class_level": "Class VIII"
}
```

**Response:**
```json
{
  "topic_id": "viii_crop_production",
  "topic_name": "Crop Production and Management",
  "summary": "Crop production is the process of growing crops...",
  "key_points": [
    "Crops are plants grown for food",
    "Different crops require different conditions",
    "Proper management ensures good yield"
  ]
}
```

---

### Chat Endpoints

#### POST /api/chat/
Send a chat message and get response.

**Request Body:**
```json
{
  "topic_id": "viii_crop_production",
  "topic_name": "Crop Production and Management",
  "messages": [
    {
      "role": "user",
      "content": "What is crop rotation?"
    }
  ]
}
```

**Response:**
```json
{
  "response": "Crop rotation is the practice of growing different crops...",
  "sources": [
    {
      "page_number": 15,
      "source": "class8.pdf",
      "class": "Class VIII"
    }
  ]
}
```

---

### Quiz Endpoints

#### POST /api/quiz/
Generate a quiz for a topic.

**Request Body:**
```json
{
  "topic_id": "viii_crop_production",
  "topic_name": "Crop Production and Management",
  "class_level": "Class VIII",
  "num_mcqs": 5,
  "num_fill_blank": 3,
  "num_short_answer": 2
}
```

**Response:**
```json
{
  "quiz_id": "uuid-here",
  "topic_id": "viii_crop_production",
  "topic_name": "Crop Production and Management",
  "questions": [
    {
      "question_id": "q1",
      "question_type": "mcq",
      "question": "What is the process of preparing soil?",
      "options": ["Ploughing", "Sowing", "Harvesting", "Irrigation"],
      "correct_answer": "Ploughing",
      "explanation": "Ploughing is the first step in soil preparation"
    },
    {
      "question_id": "q2",
      "question_type": "fill_blank",
      "question": "The process of _____ involves removing weeds.",
      "correct_answer": "weeding",
      "explanation": "Weeding removes unwanted plants"
    },
    {
      "question_id": "q3",
      "question_type": "short_answer",
      "question": "Explain the importance of irrigation.",
      "correct_answer": "Irrigation provides water to crops...",
      "explanation": "Irrigation ensures adequate water supply"
    }
  ],
  "total_questions": 10
}
```

#### GET /api/quiz/{quiz_id}
Retrieve a stored quiz.

**Response:** Same as POST /api/quiz/ response

---

### Evaluation Endpoints

#### POST /api/evaluation/upload-image
Upload an image for OCR text extraction.

**Request:** 
- Method: POST
- Content-Type: multipart/form-data
- Body: FormData with `file` field containing image

**Response:**
```json
{
  "file_id": "uuid-here",
  "extracted_text": "Q1: Ploughing\nQ2: weeding\nQ3: Irrigation is important...",
  "confidence": 0.92
}
```

#### POST /api/evaluation/evaluate
Evaluate quiz answers.

**Request Body:**
```json
{
  "quiz_id": "uuid-here",
  "answers": {
    "q1": "Ploughing",
    "q2": "weeding",
    "q3": "Irrigation provides water to crops"
  }
}
```

**Response:**
```json
{
  "quiz_id": "uuid-here",
  "total_questions": 10,
  "correct_count": 8,
  "score_percentage": 80.0,
  "question_results": [
    {
      "question_id": "q1",
      "is_correct": true,
      "feedback": "Correct! Ploughing is indeed the process of preparing soil.",
      "needs_review": false
    },
    {
      "question_id": "q2",
      "is_correct": true,
      "feedback": "Correct answer.",
      "needs_review": false
    },
    {
      "question_id": "q3",
      "is_correct": false,
      "feedback": "Your answer is partially correct, but you missed mentioning...",
      "needs_review": true
    }
  ],
  "topics_to_review": [
    "Irrigation methods",
    "Crop protection"
  ],
  "feedback": "Good effort! You answered most questions correctly. Focus on irrigation concepts for improvement."
}
```

#### GET /api/evaluation/{evaluation_id}
Retrieve stored evaluation.

**Response:** Same as POST /api/evaluation/evaluate response

---

## Error Responses

All endpoints may return the following error responses:

**400 Bad Request:**
```json
{
  "detail": "Error message here"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error message"
}
```

## Authentication

Currently, the API does not require authentication. For production, implement:
- API key authentication
- JWT tokens
- OAuth2

