import os
import sys
import json
from typing import List, Dict

import requests
from dotenv import load_dotenv
from colorama import Fore, Style, init as colorama_init


def load_env() -> None:
    load_dotenv()


def make_system_prompt() -> str:
    return (
        "Você é um chatbot simples e objetivo sobre artigos científicos. "
        "Explique conceitos básicos, estruturas de artigos (introdução, métodos, resultados, discussão), "
        "métricas e noções gerais de metodologia. "
        "Se não tiver certeza, seja honesto e peça mais contexto."
    )


class ShortMemoryChat:
    def __init__(self, k: int = 5) -> None:
        self.k = k
        self.messages: List[Dict[str, str]] = [{"role": "system", "content": make_system_prompt()}]

    def clear(self) -> None:
        self.messages = [{"role": "system", "content": make_system_prompt()}]

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        # Mantém apenas as últimas k interações (user+assistant), além do system
        trimmed: List[Dict[str, str]] = [self.messages[0]]
        convo = self.messages[1:]
        if len(convo) > self.k * 2:
            convo = convo[-self.k * 2 :]
        trimmed.extend(convo)
        self.messages = trimmed

    def get(self) -> List[Dict[str, str]]:
        return list(self.messages)


def ollama_chat(
    base_url: str,
    model: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.2,
    stream: bool = False,
    timeout: int = 300,
) -> str:
    url = f"{base_url.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "keep_alive": "5m",
        "options": {"temperature": temperature},
    }
    if stream:
        text = ""
        with requests.post(url, json=payload, stream=True, timeout=timeout) as resp:
            resp.raise_for_status()
            print(f"{Fore.YELLOW}Bot:{Style.RESET_ALL} ", end="", flush=True)
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except Exception:
                    continue
                delta = (chunk.get("message") or {}).get("content", "") or chunk.get("response", "")
                if delta:
                    text += delta
                    print(delta, end="", flush=True)
            print()
        return text
    else:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return (data.get("message") or {}).get("content", "") or data.get("response", "")


def main() -> None:
    colorama_init(autoreset=True)
    load_env()

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.1")
    temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
    timeout = int(os.getenv("OLLAMA_TIMEOUT", "600"))
    use_stream = os.getenv("OLLAMA_STREAM", "true").lower() in {"1", "true", "yes", "y"}

    # Teste rápido do serviço (opcional)
    try:
        requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=5)
    except Exception:
        print(f"{Fore.RED}Não foi possível conectar ao Ollama em {base_url}. Abra o Ollama e tente novamente.{Style.RESET_ALL}")
        sys.exit(1)

    memory = ShortMemoryChat(k=5)

    print(f"{Fore.CYAN}Chatbot pronto. Digite sua pergunta!{Style.RESET_ALL}")
    print(f"{Style.DIM}Comandos: 'exit'/'sair' para sair, 'reset' para limpar memória.{Style.RESET_ALL}")

    while True:
        try:
            user_input = input(f"{Fore.GREEN}Você:{Style.RESET_ALL} ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo...")
            break

        if user_input.lower() in {"exit", "sair", "quit"}:
            print("Até mais!")
            break
        if user_input.lower() == "reset":
            memory.clear()
            print(f"{Style.DIM}Memória limpa.{Style.RESET_ALL}")
            continue
        if not user_input:
            continue

        memory.add("user", user_input)
        try:
            answer = ollama_chat(
                base_url,
                model,
                memory.get(),
                temperature=temperature,
                stream=use_stream,
                timeout=timeout,
            )
        except Exception as e:
            print(f"{Fore.RED}Erro ao consultar o Ollama: {e}{Style.RESET_ALL}")
            continue

        memory.add("assistant", answer or "")
        if not use_stream:
            print(f"{Fore.YELLOW}Bot:{Style.RESET_ALL} {answer}")


if __name__ == "__main__":
    main()


