# Market Research Analysis Service

Python ML/NLP pipeline service for the Market Research Platform.

- **Ingestion**: Twitter (GetXAPI), YouTube (Data API v3)
- **Processing**: text cleaning, deduplication, embeddings (all-MiniLM-L6-v2)
- **ML Pipelines**: sentiment, emotions, topic clustering, trend detection, anomaly detection
- **Agents**: LangGraph orchestration with Gemini LLMs
- **API**: FastAPI with async endpoints
