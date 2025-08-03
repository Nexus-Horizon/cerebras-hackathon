# Cerebras Qwen Integration Guide

## Overview
This guide explains how to integrate and use Qwen models from Cerebras in your AI assistant application.

## What is Cerebras Qwen?

Cerebras provides optimized Qwen models that run on their specialized hardware for high-performance inference. The integration supports:

- **Qwen-7B**: Base model for general tasks
- **Qwen-14B**: Larger model for complex reasoning
- **Custom fine-tuned models**: Specialized for specific domains

## Setup Instructions

### 1. Get Cerebras API Access

1. **Sign up for Cerebras Cloud**:
   - Visit [Cerebras Cloud](https://cloud.cerebras.com)
   - Create an account and verify your email
   - Request API access for Qwen models

2. **Get your API credentials**:
   - Navigate to API Keys section
   - Generate a new API key
   - Note your API endpoint URL

### 2. Configure Environment Variables

Create or update your `.env` file:

```bash
# Enable Cerebras Qwen
USE_CEREBRAS_QWEN=true

# Cerebras API Configuration
CEREBRAS_API_URL=https://api.cerebras.com/v1/chat/completions
CEREBRAS_API_KEY=your_actual_cerebras_api_key_here
CEREBRAS_MODEL_NAME=qwen-7b

# Model Parameters
CEREBRAS_MAX_TOKENS=100
CEREBRAS_TEMPERATURE=0.7
CEREBRAS_TIMEOUT=30

# Debug Mode (optional)
DEBUG_CEREBRAS=true
```

### 3. Quick Setup Script

Run the setup script to configure Cerebras:

```bash
cd backend
python setup_cerebras.py
```

## Usage Examples

### Basic Task Classification

```python
from app.routers.cerebras_qwen import classify_task_with_cerebras_qwen

# Classify a task
task = classify_task_with_cerebras_qwen(
    question="Extract text from this image",
    image_context="Image contains handwritten text"
)
print(f"Classified task: {task}")
```

### Direct Model Calls

```python
from app.routers.cerebras_qwen import call_cerebras_qwen

# Generate text
response = call_cerebras_qwen("Explain quantum computing in simple terms")
print(response)
```

### Chat Format

```python
from app.routers.cerebras_qwen import call_cerebras_qwen_chat

messages = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": "What is machine learning?"}
]

response = call_cerebras_qwen_chat(messages)
print(response)
```

## API Endpoints

### Available Models

| Model Name | Description | Use Case |
|------------|-------------|----------|
| `qwen-7b` | Base Qwen model | General tasks, classification |
| `qwen-14b` | Larger Qwen model | Complex reasoning, analysis |
| `qwen-7b-chat` | Chat-optimized | Conversational AI |
| `qwen-14b-chat` | Large chat model | Advanced conversations |

### Request Format

```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Your question here"}
  ],
  "model": "qwen-7b",
  "max_tokens": 100,
  "temperature": 0.7
}
```

### Response Format

```json
{
  "choices": [
    {
      "message": {
        "content": "Model response here",
        "role": "assistant"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  }
}
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_CEREBRAS_QWEN` | `false` | Enable Cerebras Qwen |
| `CEREBRAS_API_URL` | Cerebras API | API endpoint |
| `CEREBRAS_API_KEY` | None | Your API key |
| `CEREBRAS_MODEL_NAME` | `qwen-7b` | Model to use |
| `CEREBRAS_MAX_TOKENS` | `100` | Max response length |
| `CEREBRAS_TEMPERATURE` | `0.7` | Response randomness |
| `CEREBRAS_TIMEOUT` | `30` | Request timeout |
| `DEBUG_CEREBRAS` | `false` | Enable debug logging |

### Model Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| `temperature` | 0.0-2.0 | Controls randomness |
| `max_tokens` | 1-4096 | Maximum response length |
| `top_p` | 0.0-1.0 | Nucleus sampling |
| `top_k` | 1-100 | Top-k sampling |
| `stop` | Array | Stop sequences |

## Performance Optimization

### 1. Batch Processing

For multiple requests, use batch processing:

```python
from app.routers.cerebras_qwen import CerebrasQwenClient, get_cerebras_config

config = get_cerebras_config()
client = CerebrasQwenClient(config)

# Batch multiple prompts
prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
results = []

for prompt in prompts:
    result = client.generate(prompt)
    results.append(result)
```

### 2. Caching

Implement response caching for repeated queries:

```python
import hashlib
import json
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_cerebras_call(prompt_hash: str):
    # Implementation with caching
    pass
```

### 3. Error Handling

```python
from app.routers.cerebras_qwen import call_cerebras_qwen

def safe_cerebras_call(prompt: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return call_cerebras_qwen(prompt)
        except Exception as e:
            if attempt == max_retries - 1:
                return f"Error after {max_retries} attempts: {e}"
            time.sleep(2 ** attempt)  # Exponential backoff
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```
   Error: API call failed with status 401
   ```
   **Solution**: Verify your API key is correct and has proper permissions

2. **Timeout Errors**
   ```
   Error: Request failed - timeout
   ```
   **Solution**: Increase `CEREBRAS_TIMEOUT` or check network connectivity

3. **Model Not Found**
   ```
   Error: Model 'qwen-7b' not found
   ```
   **Solution**: Check available models and use correct model name

4. **Rate Limiting**
   ```
   Error: API call failed with status 429
   ```
   **Solution**: Implement exponential backoff and respect rate limits

### Debug Mode

Enable debug logging:

```bash
export DEBUG_CEREBRAS=true
```

This will show:
- API requests and responses
- Model parameters
- Latency information
- Error details

### Testing Connection

Test your Cerebras setup:

```bash
# Test basic connectivity
curl -X POST https://api.cerebras.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}],
    "model": "qwen-7b",
    "max_tokens": 10
  }'
```

## Cost Optimization

### 1. Token Usage Monitoring

Monitor your token usage:

```python
def track_token_usage(response):
    usage = response.get("usage", {})
    print(f"Tokens used: {usage.get('total_tokens', 0)}")
    return usage
```

### 2. Efficient Prompting

- Use concise prompts
- Set appropriate `max_tokens`
- Implement caching for repeated queries
- Use streaming for long responses

### 3. Model Selection

Choose the right model for your use case:

- **qwen-7b**: Cost-effective for simple tasks
- **qwen-14b**: Better quality for complex reasoning
- **Custom models**: Optimized for specific domains

## Security Best Practices

1. **API Key Management**
   - Store keys in environment variables
   - Never commit keys to version control
   - Rotate keys regularly

2. **Input Validation**
   - Sanitize user inputs
   - Implement prompt injection protection
   - Set appropriate rate limits

3. **Output Filtering**
   - Filter sensitive information
   - Implement content moderation
   - Log and monitor usage

## Integration with Your Application

### 1. Update AI Classifier

The AI classifier automatically uses Cerebras when enabled:

```python
# This happens automatically when USE_CEREBRAS_QWEN=true
task = classify_task_with_qwen(question, image_context)
```

### 2. Custom Endpoints

Add custom endpoints for specific tasks:

```python
@router.post("/analyze-with-cerebras")
async def analyze_with_cerebras(request: AnalysisRequest):
    # Use Cerebras Qwen for analysis
    result = call_cerebras_qwen(request.prompt)
    return {"result": result, "model": "cerebras-qwen"}
```

### 3. Model Comparison

Compare different models:

```python
def compare_models(prompt: str):
    results = {}
    
    # Test Cerebras Qwen
    results["cerebras"] = call_cerebras_qwen(prompt)
    
    # Test other implementations
    results["local"] = call_qwen_model_local(prompt)
    
    return results
```

## Support and Resources

- **Cerebras Documentation**: [docs.cerebras.com](https://docs.cerebras.com)
- **API Reference**: [api.cerebras.com](https://api.cerebras.com)
- **Community Forum**: [community.cerebras.com](https://community.cerebras.com)
- **GitHub**: [github.com/cerebras](https://github.com/cerebras)

## Next Steps

1. Set up your Cerebras account and API key
2. Configure the environment variables
3. Test the integration with the provided examples
4. Monitor performance and costs
5. Optimize for your specific use case

Happy coding with Cerebras Qwen! 🚀 