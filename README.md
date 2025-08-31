# Photocard-AI

Projeto pessoal que usa IA para reconhecer photocards de K-pop (começando com 3 membros) — protótipo em Python usando PyTorch, Transformers e FAISS.

## Funcionalidades
- Reconhecimento de membros dos photocards via embeddings.
- Adição automática ao banco.
- Binder virtual interativo (visualizador).
- Metadados registrados no `cards.json`.

## Como rodar
```bash
git clone https://github.com/Natalia-Araujo34/photocard-ai.git
cd photocard-ai
pip install -r requirements.txt
python recognition.py
