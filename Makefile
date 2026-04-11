.PHONY: run setup-env run-backend run-frontend

run: setup-env run-backend run-frontend

setup-env:
	@if [ -z "$$OPENAI_API_KEY" ]; then \
		echo ""; \
		read -p "Enter your OpenAI API key: " key; \
		export OPENAI_API_KEY=$$key; \
		echo "export OPENAI_API_KEY=$$key" >> ~/.zshrc; \
		echo "✅ OPENAI_API_KEY set"; \
	else \
		echo "✅ OPENAI_API_KEY already set"; \
	fi
	@if [ -z "$$OPENAI_BASE_URL" ]; then \
		echo ""; \
		read -p "Enter OpenAI base URL (press enter to skip): " url; \
		if [ -n "$$url" ]; then \
			export OPENAI_BASE_URL=$$url; \
			echo "export OPENAI_BASE_URL=$$url" >> ~/.zshrc; \
			echo "✅ OPENAI_BASE_URL set"; \
		else \
			echo "⏭️  OPENAI_BASE_URL skipped"; \
		fi \
	else \
		echo "✅ OPENAI_BASE_URL already set"; \
	fi

run-backend:
	@echo ""
	@echo "📦 Installing backend dependencies..."
	@cd backend && pip install -r requirements.txt -q
	@python -m spacy download en_core_web_sm
	@echo "🚀 Starting backend..."
	@cd backend && python main.py &

run-frontend:
	@echo ""
	@echo "🎨 Starting frontend..."
	@cd frontend && yarn && yarn dev
