# ChatbotHub

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)
![Django 4.2](https://img.shields.io/badge/django-4.2-0C4B33.svg)

ChatbotHub is a Django web app where people build chatbots and chat with them.
Each chatbot answers from its own knowledge base. For every message, the app
finds the most similar stored text with a vector search in PostgreSQL
([pgvector](https://github.com/pgvector/pgvector)) and hands it to an OpenAI
model as context.

It was built during the Torob Bootcamp 1402.

**Contents:** [What it does](#what-it-does) · [How an answer is produced](#how-an-answer-is-produced) ·
[Run it with Docker Compose](#run-it-with-docker-compose) · [Run it without Docker](#run-it-without-docker) ·
[Settings](#settings) · [Adding knowledge in bulk](#adding-knowledge-in-bulk) ·
[Web routes](#web-routes) · [Project layout](#project-layout) · [Known issues](#known-issues)

## What it does

- Users register, log in and chat with any active chatbot. Conversations are
  saved, and each one gets a title written by the model.
- A chatbot has a name, a description, a custom system prompt, a photo and an
  active switch.
- Each chatbot has its own knowledge base: text snippets, each stored with a
  1536-dimension embedding (`text-embedding-ada-002`) in PostgreSQL.
- Feedback on answers: a like is counted once per message. A dislike asks the
  model for a new answer, and the first answer can be shown again.
- Full-text search inside a conversation, using PostgreSQL.
- Roles come from Django admin groups. Superusers and the `torob-admin` group
  see every chatbot and its content. The `chatbot-admin` group manages only its
  own chatbots and content. Everyone else can only chat.

## How an answer is produced

```
user message
  -> embedding (text-embedding-ada-002)
  -> nearest snippet of this chatbot (pgvector, L2 distance)
  -> saved in the conversation as a "context" message
  -> prompt: the chatbot's system prompt, a rule to answer truthfully or say
     "Sorry, I don't know", the conversation so far, the context, the question
  -> gpt-3.5-turbo (temperature 0.6)
```

## Run it with Docker Compose

```bash
docker compose up --build
docker compose exec web python manage.py createsuperuser
```

This starts PostgreSQL with pgvector and the web app, and applies the database
migrations. Open <http://localhost:8000>. The admin site is at `/admin/`. Set
`CHATBOTHUB_PORT` if port 8000 is taken.

Anything that calls OpenAI needs a key:

```bash
OPENAI_KEY=your-api-key docker compose up --build
```

Without a key the app starts and its pages load, but the features that call OpenAI
(conversations and embeddings) do not work. Set `OPENAI_BASEURL` to use an OpenAI-compatible service
other than OpenAI.

To get a first chatbot, sign in to `/admin/`, add a chatbot (with a photo) and add
content to it. Then open `/chatbots/`.

Stop the app and delete its database with `docker compose down -v`.

The compose file is for trying the app on your machine: it uses example
passwords and Django's development server.

## Run it without Docker

You need Python 3.11 and a PostgreSQL server with the pgvector extension. The
a migration creates the extension, so the database user must be allowed to
create extensions.

```bash
cd chatbothub
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then edit the values
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Settings

The app reads these environment variables. A `.env` file next to `manage.py` is
loaded too ([`.env.example`](chatbothub/.env.example)). All of them must be set,
or the app stops at start-up with a `KeyError`.

| Variable | Meaning |
|---|---|
| `OPENAI_KEY` | API key. May be empty if you never call OpenAI. |
| `OPENAI_BASEURL` | API address, for example `https://api.openai.com/v1`. |
| `DEBUG` | Plain text, not a yes/no value: any non-empty value turns debug mode on, even `False`. Leave it empty to turn debug mode off. |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | PostgreSQL login. |
| `DB_HOST`, `DB_PORT` | PostgreSQL address. |

## Adding knowledge in bulk

`chatbothub/content-adder.py` and `chatbothub/test-dataset.py` take no
arguments. Open the file, set the chatbot id and the JSONL path on its last line
(both are `7` and `data/data.jsonl` today), then run it inside the Django shell:

```bash
cd chatbothub
python manage.py shell < content-adder.py
# with Docker Compose, from the repository root:
docker compose exec -T web python manage.py shell < chatbothub/content-adder.py
```

Each line of the JSONL file is an object such as
`{"id": 1, "question": "...", "doc": "..."}`.

- `content-adder.py` stores every `doc` as a snippet of the chatbot, with its
  embedding. It sends one OpenAI request per line.
- `test-dataset.py` embeds every `question`, looks for the nearest snippet by
  maximum inner product, and counts how often it is the line's own `doc`.

`chatbothub/data/data.jsonl` holds 580 lines to try this with.
`chatbothub/dataset_result/` holds saved outputs of such runs for cosine
distance, L2 distance and maximum inner product.

## Web routes

| Route | Purpose |
|---|---|
| `/` | Home page |
| `/register/`, `/login/`, `/logout/` | Account |
| `/chatbots/` | List of active chatbots |
| `/start-conversation/` | Open a conversation with a chatbot |
| `/chat-details/<id>/` | One conversation (accepts `?search_query=`) |
| `/send-message/<id>/` | Send a message |
| `/chat-history/` | Your conversations |
| `/like-dislike-message/<id>/<action>/` | Like or dislike an answer (POST) |
| `/switch_content/<id>/` | Show the first or the regenerated answer |
| `/admin/` | Django admin: chatbots, content, users, groups |

## Project layout

```
chatbothub/
  manage.py, requirements.txt, Dockerfile
  chatbothub/        settings and URLs
  chatbot/           models, views, OpenAI and vector-search code, admin, migrations
  templates/         HTML pages
  data/              sample dataset
  dataset_result/    saved outputs of retrieval experiments
  content-adder.py   load a dataset into a chatbot
  test-dataset.py    measure retrieval quality
docker-compose.yml   local trial run
.gitlab-ci.yml       image build and deploy pipeline
Blogpost.pdf         write-up of the project
```

## Known issues

- `SECRET_KEY` and `ALLOWED_HOSTS` are fixed values in `settings.py`. Change them
  before any real deployment.
- The Dockerfile has no start command. The compose file supplies one.
- The model names (`gpt-3.5-turbo`, `text-embedding-ada-002`) are fixed in
  `chatbot/services.py`.
- `requirements.txt` pins `httpx` to 0.27.2 because `openai` 1.3.4 does not start
  with `httpx` 0.28 or newer.

## Authors and acknowledgements

Amirerfan Teimouri. Thanks to the Torob Bootcamp 1402 team for guidance and
mentorship.

## License

MIT. See [LICENSE](LICENSE).
