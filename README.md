# Gatekeepyr

API Gateway with load balancing and circuit breaker.

## Run
```bash
docker compose up
curl http://localhost:8000/proxy/
```

Gateway starts with 4 backends. One fails randomly to test circuit breaker behavior.

## What it does

- Round-robin load balancing
- Circuit breaker isolates failing backends
- Health checks remove dead backends from rotation
- Auto-recovery after 30 seconds

## Test
```bash
# Load balancing
for i in {1..10}; do curl http://localhost:8000/proxy/; done

# metrics
curl http://localhost:8000/metrics

# Logs (circuit breaker open/close)
docker compose logs -f gateway
```

## Config

Copy `.env.example` to `.env` if needed. Defaults work fine.


Based on [samwho.dev/load-balancing](https://samwho.dev/load-balancing/)

---

# Gatekeepyr (PT-BR)

API Gateway com load balancing e circuit breaker.

## Como rodar
```bash
docker compose up
curl http://localhost:8000/proxy/
```

Gateway inicia com 4 backends. Um deles falha randomicamente pra testar o circuit breaker.

## Como funciona

- Balanceamento com round-robin
- Circuit breaker isola os backends com falha
- Health checks removem os backends mortos da rotação
- Recuperação é feita de forma automática após 30 segundos

## Testar
```bash
# Balanceamento
for i in {1..10}; do curl http://localhost:8000/proxy/; done

# Métricas
curl http://localhost:8000/metrics

# Logs (ircuit breaker abre/fecha)
docker compose logs -f gateway
```

## Config

Copia `.env.example` pra `.env` se necessário. O padrão funciona.


Based on [samwho.dev/load-balancing](https://samwho.dev/load-balancing/)
