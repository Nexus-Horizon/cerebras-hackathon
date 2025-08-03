# Qwen API Configuration

## Overview
The application uses a Qwen model for AI task classification. The API can be configured in several ways:

## Configuration Options

### 1. Local API Endpoint (Default)
- **URL**: `http://localhost:8000/qwen/predict`
- **Status**: ✅ Implemented
- **Usage**: The default configuration uses a local FastAPI endpoint
- **API Key**: Not required for local endpoint

### 2. Environment Variable Override
- **Variable**: `QWEN_API_URL`
- **Example**: `export QWEN_API_URL="https://your-qwen-api.com/predict"`
- **Usage**: Override the default endpoint for external APIs

### 3. API Key Configuration
- **Variable**: `QWEN_API_KEY`
- **Example**: `export QWEN_API_KEY="your_api_key_here"`
- **Usage**: Required for external API services
- **Security**: API key is automatically added to Authorization header

### 4. External Qwen API
To use an external Qwen API service:

1. Set the environment variables:
   ```bash
   export QWEN_API_URL="https://your-qwen-api.com/predict"
   export QWEN_API_KEY="your_api_key_here"
   ```

2. Ensure the API accepts the following request format:
   ```json
   {
     "prompt": "string",
     "max_tokens": 100,
     "temperature": 0.7
   }
   ```

3. The API should return:
   ```json
   {
     "response": "string",
     "latency": 0.1234,
     "model": "qwen-api"
   }
   ```

4. **Security**: The API key is automatically included in the Authorization header as `Bearer {api_key}`

## Current Implementation

### Local API (`/qwen/predict`)
- **Endpoint**: `POST /qwen/predict`
- **Function**: Simple rule-based task classification
- **Fallback**: Uses keyword matching when external API is unavailable

### Error Handling
- API failures fall back to local model
- Local model failures fall back to mock classification
- All failures default to "Other" task type

## API Key Setup

### For Local Development
```bash
# No API key required for local endpoint
export QWEN_API_URL="http://localhost:8000/qwen/predict"
```

### For External APIs
```bash
# Set your API key
export QWEN_API_KEY="your_actual_api_key_here"
export QWEN_API_URL="https://your-qwen-service.com/predict"
```

### Environment File Setup
1. Copy the example file:
   ```bash
   cp backend/env.example backend/.env
   ```

2. Edit `.env` with your actual values:
   ```bash
   QWEN_API_KEY=your_actual_api_key_here
   QWEN_API_URL=https://your-qwen-service.com/predict
   ```

## Testing the API

### Health Check
```bash
curl http://localhost:8000/qwen/health
```

### Prediction Test (Local)
```bash
curl -X POST http://localhost:8000/qwen/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Extract text from this image"}'
```

### Prediction Test (External with API Key)
```bash
curl -X POST https://your-qwen-service.com/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key_here" \
  -d '{"prompt": "Extract text from this image"}'
```

## Troubleshooting

### Common Issues
1. **Connection refused**: Ensure the backend server is running
2. **Timeout errors**: Check network connectivity to external APIs
3. **Invalid response format**: Verify API response structure

### Debug Mode
Enable debug logging by setting:
```bash
export DEBUG_QWEN=1
```

## Future Enhancements
- Add authentication for external APIs
- Implement caching for repeated requests
- Add rate limiting
- Support for different model versions 