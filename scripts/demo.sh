#!/usr/bin/env bash
set -euo pipefail

echo "==================================================="
echo "  CreditPulse - Demo End-to-End"
echo "==================================================="

echo ""
echo ">> [1/4] Gerando samples de Open Finance..."
python data/samples/generate_samples.py

echo ""
echo ">> [2/4] Rodando testes..."
pytest tests/ -v

echo ""
echo ">> [3/4] Subindo API e chamando /v1/credit-decision..."
uvicorn api.app:app --host 0.0.0.0 --port 8000 &
API_PID=$!
sleep 5

echo ""
echo "--- Sample GOOD ---"
curl -s -X POST http://localhost:8000/v1/credit-decision \
     -H "Content-Type: application/json" \
     -d @data/samples/sample_good.json | python -m json.tool

echo ""
echo "--- Sample BAD ---"
curl -s -X POST http://localhost:8000/v1/credit-decision \
     -H "Content-Type: application/json" \
     -d @data/samples/sample_bad.json | python -m json.tool

echo ""
echo ">> [4/4] Encerrando API..."
kill $API_PID 2>/dev/null || true

echo ""
echo "==================================================="
echo "  Demo concluida com sucesso!"
echo "==================================================="
