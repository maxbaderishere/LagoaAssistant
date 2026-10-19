# Lagoa

**Português** | [English](README.en.md) | [Русский](README.ru.md)

Um chat de código aberto para trabalhar com modelos de IA, feito para o Brasil.

## Sobre o projeto

A Lagoa reúne diferentes modelos de IA — na nuvem e locais — em uma única interface em português do Brasil. Ela lembra das suas conversas e deixa você escolher o modelo que melhor combina com cada tarefa.

- **Português em primeiro lugar:** a interface e os textos são pensados para o português brasileiro, e os modelos são escolhidos e avaliados pela qualidade com que lidam com o idioma.
- **Livre e aberta:** código aberto, modelos gratuitos sempre que possível e modelos locais via Ollama, que funcionam sem internet e mantêm seus dados no seu computador.
- **Fácil de hospedar:** qualquer pessoa pode rodar a própria Lagoa.

Você faz uma pergunta no chat, o backend envia a pergunta ao modelo junto com o contexto da conversa, salva a pergunta e a resposta no banco de dados e devolve a resposta. Cada pessoa tem a própria conta e quantas conversas quiser: em cada uma, a Lagoa lembra do que vocês já conversaram, e no próximo login todas as conversas são carregadas do banco.

Hoje a Lagoa funciona com **Groq** (padrão), **Google Gemini** e modelos locais via **Ollama**.

## Funcionalidades

- Chat com modelos de IA em uma interface web
- **Vários provedores de IA:** Groq, Gemini e modelos locais via Ollama; o modelo é escolhido logo abaixo do campo de mensagem
- **Funciona sem internet:** com o Ollama, a Lagoa responde com um modelo local no seu computador
- **Respostas rápidas:** quando o assistente faz uma pergunta, aparecem botões com opções de resposta
- **Botão de parar:** enquanto a resposta está sendo gerada, dá para cancelar o pedido; a pergunta volta para o campo de mensagem
- **Memória da conversa:** a Lagoa lembra do contexto das mensagens anteriores
- **Contas:** cadastro e login com usuário e senha
- **Várias conversas:** criar, renomear e excluir; as conversas são agrupadas por data, cada uma com seu próprio histórico e memória
- **Tela inicial viva:** a saudação, o subtítulo e as dicas no campo de mensagem mudam conforme a hora do dia
- Respostas com formatação (listas, negrito, blocos de código)
- Interface adaptada para computador e celular
- Interface em português, inglês, russo e espanhol, com menu de idiomas

## Como a Lagoa lembra do contexto

Os modelos de linguagem não guardam memória entre um pedido e outro, então o contexto é enviado junto com cada pergunta. Para que os pedidos não cresçam sem parar, o histórico é dividido em duas partes:

- **as mensagens mais recentes** (10 por padrão) vão para o modelo palavra por palavra;
- **as mensagens mais antigas** são condensadas em um resumo curto: fatos importantes sobre a pessoa, suas tarefas e combinados. O resumo fica no banco de dados, é enviado ao modelo como instrução de sistema e é atualizado aos poucos, conforme novas mensagens antigas se acumulam.

Assim o assistente lembra tanto dos detalhes recentes quanto do panorama geral, e os pedidos continuam pequenos. A quantidade de mensagens enviadas na íntegra e o tamanho do lote para o resumo ficam em `backend/config.py` (`keep_last` e `summarise_every`).

## Tecnologias

- **Python 3.14**
- **FastAPI** — API REST
- **Uvicorn** — servidor ASGI
- **SQLAlchemy 2** — ORM, banco de dados SQLite
- **groq** — cliente da API do Groq
- **google-genai** — cliente da API do Gemini
- **Ollama** + **httpx** — modelos locais sem internet
- **pwdlib (Argon2)** — hash de senhas
- **PyJWT** — tokens de acesso
- **python-dotenv** — carrega chaves e segredos do `.env`
- **HTML / CSS / JavaScript** — frontend sem frameworks
- **uv** — gerenciamento de dependências

## Estrutura do projeto

```
├── backend/
│   ├── main.py               # aplicação FastAPI, conecta todos os endpoints
│   ├── auth.py               # cadastro, login e a dependência get_current_user
│   ├── chats.py              # endpoints de conversas e mensagens
│   ├── security.py           # hash de senhas e tokens JWT
│   ├── schemas.py            # esquemas Pydantic de pedidos e respostas
│   ├── db.py                 # modelos do banco de dados e funções auxiliares
│   ├── config.py             # configurações e chaves de API do .env
│   └── ai/
│       ├── client.py         # classe abstrata do cliente de IA
│       ├── gemini_client.py  # cliente do Gemini
│       ├── groq_client.py    # cliente do Groq
│       ├── ollama_client.py  # cliente dos modelos locais do Ollama
│       ├── registry.py       # registro dos modelos disponíveis
│       └── setup.py          # monta o registro a partir do config.py
├── frontend/
│   ├── index.html            # página do chat
│   ├── login.html            # página de login e cadastro
│   ├── styles.css            # estilos
│   ├── i18n.js               # traduções da interface (RU / EN / PT / ES)
│   ├── greetings.js          # frases da tela inicial para cada idioma e hora do dia
│   ├── api.js                # endereço da API, token e pedidos autenticados
│   ├── auth.js               # lógica de login e cadastro
│   └── app.js                # lógica do chat
├── .env                      # chaves de API e segredos (fora do Git)
├── data.db                   # banco de dados SQLite (criado automaticamente, fora do Git)
└── pyproject.toml            # dependências
```

## Provedores de IA

Os clientes de IA herdam da classe abstrata `Client`. Para conectar um novo provedor, basta escrever uma classe com o método `generate`; o resto do código funciona com qualquer cliente da mesma forma.

Os modelos disponíveis ficam em `backend/config.py`:

```python
models = [
    {"provider": "groq", "model": "qwen/qwen3.8-27b", "name": "Qwen 3.8 27B"},
    {"provider": "gemini", "model": "gemini-3.6-flash", "name": "Gemini 3.6 Flash"},
    {"provider": "ollama", "model": "qwen3.5:4b", "name": "Qwen 3.5 4B"},
]
default_model = "qwen/qwen3.8-27b"
title_model = {"provider": "ollama", "model": "qwen3.5:4b"}
quick_reply_model = {"provider": "ollama", "model": "qwen3.5:4b"}
```

Ao iniciar, o `ModelRegistry` (`backend/ai/registry.py`) cria um cliente para cada modelo disponível: um modelo na nuvem, se a chave de API do provedor estiver configurada, e um modelo local, se o Ollama estiver rodando e o modelo tiver sido baixado. A pessoa escolhe o modelo abaixo do campo de mensagem, e a escolha fica salva no navegador. Para adicionar outro modelo do mesmo provedor, basta uma nova linha em `models`. Veja os nomes dos modelos na documentação do [Groq](https://console.groq.com/docs/models), do [Gemini](https://ai.google.dev/gemini-api/docs/models) e na [biblioteca do Ollama](https://ollama.com/library).

`title_model` é um modelo auxiliar que dá nome às novas conversas, para não gastar os limites dos modelos principais. Se ele não estiver disponível, o próprio modelo da conversa escolhe o nome.

`quick_reply_model` é um modelo local que sugere as respostas rápidas. Os modelos na nuvem não são usados para isso: sem um modelo local, os botões simplesmente não aparecem.

### Modelos locais (Ollama)

Com o [Ollama](https://ollama.com/download), a Lagoa funciona sem internet. Instale o Ollama e baixe um modelo:

```bash
ollama pull qwen3.5:4b
```

Depois reinicie o backend: os modelos baixados são verificados na inicialização. O servidor do Ollama usa `http://localhost:11434` por padrão; dá para mudar com `OLLAMA_URL` no `.env`. O modelo local roda no seu próprio computador, então, sem placa de vídeo, respostas longas podem levar um ou dois minutos.

## Como rodar

### 1. Clone o repositório

```bash
git clone https://github.com/maxbaderishere/LagoaAssistant.git
cd LagoaAssistant
```

### 2. Instale as dependências

É preciso ter o [uv](https://docs.astral.sh/uv/) instalado.

```bash
uv sync
```

### 3. Configure as chaves de API e o segredo dos tokens

Crie um arquivo `.env` na raiz do projeto. Das chaves de IA, basta a do provedor que você vai usar, mas o `JWT_SECRET` é obrigatório: ele assina os tokens de login.

```
GROQ_API_KEY=sua_chave_groq
GEMINI_API_KEY=sua_chave_gemini
JWT_SECRET=uma_string_longa_e_aleatoria
```

Para gerar um segredo:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

A chave do Groq fica no [console do Groq](https://console.groq.com/keys), e a do Gemini, no [Google AI Studio](https://aistudio.google.com/apikey).

### 4. Inicie o backend

```bash
uv run uvicorn backend.main:app --reload
```

A API fica disponível em http://localhost:8000, e a documentação interativa, em http://localhost:8000/docs.

### 5. Inicie o frontend

O frontend precisa rodar na porta 5500 (esse endereço está liberado nas configurações de CORS). Sirva apenas a pasta `frontend/`, por exemplo:

```bash
python -m http.server 5500 -d frontend
```

Depois abra http://localhost:5500/index.html. Com o Live Server do VS Code, abra o arquivo `frontend/index.html`. Sem login, o chat redireciona para a página de login e cadastro.

## API

| Método | Caminho                  | Descrição                                        |
|--------|--------------------------|--------------------------------------------------|
| POST   | `/auth/register`         | Cadastro; devolve um token de acesso             |
| POST   | `/auth/login`            | Login; devolve um token de acesso                |
| GET    | `/auth/me`               | A pessoa logada                                  |
| GET    | `/chats`                 | Conversas da pessoa, das mais recentes           |
| POST   | `/chats`                 | Criar uma conversa vazia                         |
| PATCH  | `/chats/{id}`            | Renomear uma conversa                            |
| DELETE | `/chats/{id}`            | Excluir uma conversa com todas as mensagens      |
| GET    | `/chats/{id}/messages`   | Mensagens de uma conversa                        |
| GET    | `/chats/{id}/suggestions`| Respostas rápidas para a última resposta         |
| POST   | `/chats/{id}/messages`   | Enviar uma pergunta; devolve a resposta          |
| GET    | `/models`                | Modelos disponíveis e o modelo padrão            |

Todos os endpoints, exceto cadastro, login e `/models`, exigem o cabeçalho `Authorization: Bearer <token>`.

Exemplo de pedido:

```bash
curl -X POST http://localhost:8000/chats/1/messages \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Olá! Quem é você?"}'
```

Resposta:

```json
{"answer": "Olá! Sou um modelo de linguagem..."}
```

## Limitações

- O token de login fica no `localStorage` do navegador: é simples, mas menos protegido contra XSS do que um cookie httpOnly.
- O resumo das mensagens antigas perde pequenos detalhes: o modelo lembra da essência, não das palavras exatas.
- Ao parar uma resposta, o modelo ainda termina de gerá-la em segundo plano; ela só não é salva.

## Próximos passos

- [x] Enviar o histórico da conversa ao modelo, para o assistente manter o contexto
- [x] Suportar vários provedores de IA (Groq, Gemini e Ollama)
- [x] Cadastro e login
- [x] Escolher o modelo direto na interface
- [x] Várias conversas por pessoa
- [x] Mais idiomas na interface (português e espanhol)
- [ ] Mensagens claras quando o modelo atinge o limite de uso, em vez de erro de conexão
- [ ] Repetir o pedido depois de um erro ou de parar a resposta
- [ ] Testes que avaliam de 0 a 100 o quanto cada modelo domina o português
- [ ] Mais modelos gratuitos com bom português
- [ ] Personalização: um estilo de conversa da pessoa que todos os modelos seguem
- [ ] Comandos no chat, como `/context`
- [ ] Testes automatizados
