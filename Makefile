
.PHONY: all frontend backend clean

all: frontend backend

frontend:
	@echo "Starting frontend..."
	@cd Frontend && streamlit run frontend.py &

backend:
	@echo "Starting backend..."
	@cd Backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &

clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -r {} + || true
	@find . -type f -name "*.pyc" -delete || true
