You are a Senior Fullstack Developer specializing in Python (FastAPI, SQLModel) and Frontend (HTML5, Vanilla JS, Pico CSS).

I am building a project called `gurgel-tools`, a hub of various tools. The backend serves HTML files and exposes a REST API.
The technology stack is:
- Backend: FastAPI with SQLModel (for database persistence).
- Frontend: Pure HTML, Pico CSS (styling), and Lucide (icons). No JS frameworks, only Vanilla JS.

**PROJECT ARCHITECTURE:**
Each app in the hub consists of two main files:
1. `snippets.py`: Contains SQLModel classes, Pydantic schemas, and a main function `snippets(app: FastAPI)` that registers the routes.
2. `snippets.html`: The UI, using Pico CSS and Lucide.

**CURRENT GOAL:**
Create the "Snippets" app, a tool to store, organize, and quickly copy chunks of information. The app revolves around "Snippet Groups" and "Snippets".

**DATABASE MODELING (SQLModel):**
Create the following models (and their corresponding Create/Update schemas):
1. **SnippetGroup:**
   - `id`: Primary key.
   - `name`: String.
   - `created_at`: Datetime (default to current UTC time).
   - `last_copied_at`: Datetime (nullable, updated whenever a snippet inside this group is copied).
   - Relationship to `Snippet`.
2. **Snippet:**
   - `id`: Primary key.
   - `name`: String.
   - `content`: String (can be long/multiline).
   - `group_id`: Foreign key to `SnippetGroup`.
   - Relationship to `SnippetGroup`.

**BACKEND REQUIREMENTS:**
- **CRUD for Snippet Groups:** Create, Read (List), Delete.
- **CRUD for Snippets:** Create, Update (specifically the content), Delete.
- **List/Sort Logic:** When fetching groups for the initial load, return them sorted in descending order of usage. Order by `last_copied_at` DESC (most recently used first). If `last_copied_at` is null, fallback to `created_at` DESC.
- **Register Copy Action:** An endpoint (e.g., `POST /api/snippets/{id}/copy`) that updates the parent `SnippetGroup.last_copied_at` to the current timestamp.
- **Search Endpoint:** Allow searching by name. Accept a query parameter for the search term and a parameter for the search target (`type="snippet"` or `type="group"`). The default behavior should be searching by Snippet name.

**FRONTEND REQUIREMENTS:**
- **Local Assets:** You MUST use local paths for CSS and JS. Do not use CDNs.
  - CSS: `<link rel="stylesheet" href="css/pico.min.css" />`
  - JS: `<script src="static/lucide.js"></script>`
- **UI Layout:** Clean, responsive design using Pico CSS. Display Groups as cards or sections, showing the Group's `name` and `created_at` date. Inside each Group, list its Snippets.
- **Search Bar:** Placed at the top of the page. Include a text input and a `<select>` or radio buttons to choose the search scope ("Search by Snippet Name" [default] or "Search by Group Name").
- **Snippet Content & Auto-save:** 
  - The snippet `content` MUST be displayed inside a `<textarea>` because they can be very large and have multiple lines.
  - Implement an **auto-save on blur** mechanism: On `focus`, store the initial content value. On `blur`, compare the current value with the initial value. If it has changed, automatically make a PUT/PATCH request to save the new content to the database.
- **Actions (Buttons):**
  - **Copy Button:** Placed near each snippet. When clicked, use `navigator.clipboard.writeText()` to copy the textarea content. On success, call the backend "Register Copy Action" endpoint, and optionally show a brief visual feedback (like changing the icon temporarily).
  - **Delete Snippet:** A button near the snippet to delete it.
  - **Delete Group:** A button near the group header to delete the entire group.
- **Dynamic Icons:** Render Lucide icons dynamically. Use icons for copying (`copy`), deleting (`trash`), searching (`search`), etc. Always call `lucide.createIcons()` after DOM mutations.

**BACKEND REFERENCE CODE:**
Follow this dependency injection and routing pattern:
```python
from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Field, Session, SQLModel, select
from apps.engine import get_session # Use this exact import for the session
from typing import Annotated
from datetime import datetime, timezone

SessionDep = Annotated[Session, Depends(get_session)]

def snippets(app: FastAPI):
    # Your routes here using @app.post, @app.get, etc.
    # Route paths should probably be prefixed with /api/snippets and /api/snippet-groups


### O que foi feito/melhorado neste prompt:
1. **Modelagem de Dados bem definida:** Transformei o requisito de "last copied" em um campo `last_copied_at` no banco, com regras exatas de como o backend deve fazer a ordenação por default (fallback para data de criação caso nunca tenha sido copiado).
2. **Lógica de Auto-save isolada:** Expliquei para a IA a lógica exata do frontend no Vanilla JS (`focus` salva estado atual -> `blur` compara -> se diferente faz a chamada API). Isso evita que ela crie botões de "Salvar" desnecessários.
3. **Mecânica do Copy:** Instruí que o botão de copiar deve usar a API nativa do navegador (`navigator.clipboard.writeText`) e, no `.then()` do JS, disparar a requisição pro backend atualizar o `last_copied_at` do grupo.
4. **Search Bar estruturada:** Defini a criação de um `<select>` ou radio para alternar o escopo da busca, deixando explícito que o padrão é buscar por snippet. 
5. **Textarea:** Exigi explicitamente o uso de `<textarea>` no lugar de `<input>` para garantir que múltiplas linhas funcionem corretamente com o Pico CSS.
