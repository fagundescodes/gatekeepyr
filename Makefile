build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v --rmi all

test:
	@echo "Testing gateway"
	@curl -s http://localhost:8000/health
	@echo "\n\nTesting proxy"
	@curl -s http://localhost:8000/proxy/
	@echo "\n\nChecking metrics"
	@curl -s http://localhost:8000/metrics
	@echo ""
