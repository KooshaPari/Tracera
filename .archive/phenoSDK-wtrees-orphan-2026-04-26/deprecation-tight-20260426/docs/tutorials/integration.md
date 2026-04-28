# Integration Tutorial

This tutorial shows how to integrate the Pheno SDK with various systems and frameworks.

## Web Framework Integration

### Flask Integration

```python
from flask import Flask, request, jsonify
from pheno import PhenoSDK

app = Flask(__name__)
sdk = PhenoSDK()

@app.route('/process', methods=['POST'])
def process_data():
    data = request.json
    try:
        result = sdk.process_data(data)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
```

### Django Integration

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pheno import PhenoSDK

sdk = PhenoSDK()

@csrf_exempt
def process_data(request):
    if request.method == 'POST':
        data = request.json()
        try:
            result = sdk.process_data(data)
            return JsonResponse({'success': True, 'result': result})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
```

## Database Integration

### SQLAlchemy Integration

```python
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from pheno import PhenoSDK

Base = declarative_base()
sdk = PhenoSDK()

class ProcessedData(Base):
    __tablename__ = 'processed_data'
    
    id = Column(String, primary_key=True)
    original_data = Column(Text)
    processed_data = Column(Text)
    created_at = Column(String)

# Process and store data
def process_and_store(data):
    result = sdk.process_data(data)
    
    processed_item = ProcessedData(
        id=str(uuid.uuid4()),
        original_data=str(data),
        processed_data=str(result),
        created_at=datetime.now().isoformat()
    )
    
    session.add(processed_item)
    session.commit()
    
    return result
```

## API Integration

### REST API Client

```python
import requests
from pheno import PhenoSDK

class PhenoAPIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.sdk = PhenoSDK()
    
    def process_data(self, data):
        # Process locally first
        local_result = self.sdk.process_data(data)
        
        # Send to remote API
        response = requests.post(
            f"{self.base_url}/process",
            json={'data': data, 'local_result': local_result},
            headers={'Authorization': f'Bearer {self.api_key}'}
        )
        
        return response.json()
```

## Next Steps

- [API Reference](../api/)
- [Architecture Overview](../architecture/)
- [Examples](../examples/)

---

*This tutorial is automatically generated.*
