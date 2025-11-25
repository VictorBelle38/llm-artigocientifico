## Chatbot Simples de Artigos Científicos (Ollama HTTP + Memória Curta)

Este repositório contém um chatbot simples em Python que:
- Responde perguntas básicas sobre artigos científicos
- Usa um modelo local via Ollama (sem chave de API)
- Possui memória curta de conversa (janela)

### Requisitos
- Python 3.10+ recomendado
- Ollama instalado e em execução (`https://ollama.com/download`)

### Instalação (Windows / PowerShell)
1) Criar e ativar venv:
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Instalar dependências:
```bash
pip install -r requirements.txt
```

3) Configurar variáveis de ambiente:
- Copie `example.env` para `.env`. (Se preferir, você também pode criar manualmente o arquivo `.env`.)
```bash
copy example.env .env
```
Edite `.env` e ajuste:
- `OLLAMA_MODEL` (padrão: llama3.1)
- `OLLAMA_BASE_URL` (padrão: http://localhost:11434)

4) Baixe o modelo local:
```bash
ollama pull llama3.1
```

### Executar o Chatbot (CLI)
```bash
python -m app.chatbot
```

Comandos no prompt:
- Digite sua pergunta e pressione Enter
- `exit` ou `sair` para encerrar
- `reset` para limpar a memória da conversa

### Como funciona
- O chatbot chama a API HTTP do Ollama (`/api/chat`) diretamente usando `requests`.
- Mantém uma memória curta das últimas interações (k=5) para dar contexto.
- Não usa RAG/embeddings nem depende de provedores externos.

### Usando modelo local (Ollama)
1) Instale o Ollama: `https://ollama.com/download`
2) No PowerShell, baixe o modelo:
```bash
ollama pull llama3.1
```
3) Certifique-se de que o serviço do Ollama está em execução (porta padrão `11434`).
4) No `.env`, use:
```
OLLAMA_MODEL=llama3.1
OLLAMA_BASE_URL=http://localhost:11434
```
5) Rode o chatbot normalmente:
```bash
python -m app.chatbot
```

### Estrutura
```
app/
  __init__.py
  chatbot.py
data/
  (coloque seus PDFs aqui)
example.env
requirements.txt
README.md
```

### Explicação do código (resumo)
- `app/chatbot.py`:
  - Carrega `.env` (dotenv) e prepara console colorido (colorama).
  - Define um prompt de sistema curto para orientar o assistente.
  - Implementa `ShortMemoryChat` (memória curta): guarda apenas as últimas k mensagens de usuário+assistente além do system.
  - Envia as mensagens para o endpoint `POST /api/chat` do Ollama com `stream=False` e imprime a resposta ao final.
  - Comandos: `reset` limpa a memória, `exit/sair` encerra.

### Por que pode demorar um pouco?
- Primeira chamada pode carregar o modelo na RAM/VRAM, o que leva alguns segundos.
- A geração é local e depende do hardware (CPU/GPU). Modelos maiores geram mais devagar.
- Com `stream=False`, a resposta aparece apenas ao final; com streaming (não habilitado aqui) a sensação de latência é menor.

### Dicas para acelerar
- Use um modelo menor (ex.: `mistral`, `llama3.2:3b`).
- Deixe o Ollama aberto para manter o modelo aquecido entre perguntas.
- Habilite streaming (alterando a chamada para `stream=True` e imprimindo tokens conforme chegam).


