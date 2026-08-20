You are a Senior Fullstack Developer specializing in Python (FastAPI, SQLModel)
and Frontend (HTML5, Vanilla JS, Pico CSS).

I am building a project called gurgel-tools, a hub of various tools. The backend
serves HTML files and exposes a REST API. The technology stack is:

  - Backend: FastAPI with SQLModel (for database persistence).
  - Frontend: Pure HTML, Pico CSS (styling), and Lucide (icons). No JS
    frameworks, only Vanilla JS.

PROJECT ARCHITECTURE: Each app in the hub consists of two main files:

1.  [app_name].py: Contains SQLModel classes, Pydantic schemas, and a main
    function [app_name](app: FastAPI) that registers the routes.
2.  [app_name].html: The UI, using Pico CSS and Lucide.

CURRENT GOAL:
Build an app called `prompt-templates`. This application allows users to create, manage, and use text templates with dynamic variables that are filled out before copying to the clipboard.

DATABASE MODELING (SQLModel):
Create a SQLModel class called `PromptTemplate`. It must include:
- `id`: Primary key (UUID or Integer).
- `name`: String.
- `description`: String (optional).
- `content`: String (the actual template text containing variables).
- `created_at`: Datetime (default to current UTC time).
- `updated_at`: Datetime (default to current UTC time, updated on edit).
- `last_copied_at`: Datetime (nullable, updated whenever the user copies the prompt).

BACKEND REQUIREMENTS :
- Implement full CRUD REST endpoints for `PromptTemplate` (GET, POST, PUT, DELETE).
- Create a specific endpoint (e.g., POST or PATCH `/prompt-templates/{id}/copied`) to update the `last_copied_at` timestamp.
- The GET endpoint returning all templates MUST order the list dynamically: items with the most recent `last_copied_at` date appear first. If `last_copied_at` is null, fallback to `created_at` or `updated_at` for sorting.

FRONTEND REQUIREMENTS :
- Theme: Force a dark theme UI (using Pico CSS data-theme="dark" attribute if necessary).
- Layout: 
  - A main list displaying ALL prompt templates. 
  - In the list, ONLY show the `name` and `description`. The `content` must be hidden by default.
  - When a user selects/clicks a prompt from the list, expand it to show its `content` and a dynamic form.
- Dynamic Variables Logic (Crucial):
  - Variables in the `content` are defined using double square brackets, e.g., `[[Variable Name]]`.
  - Use Vanilla JS regex to parse the content and find all unique variables.
  - For each variable found, generate a form input. 
  - Because variable contents can be very long, MUST use `<textarea>` elements (adequately sized) for these inputs, not single-line `<input type="text">`.
- Action - Edit Prompt (Crucial Logic):
  - Provide an "Edit" button (using a Lucide icon like `pencil`).
  - When clicked, allow the user to modify the `name`, `description`, and `content`.
  - Save changes via the backend PUT endpoint.
  - **VARIABLE RE-EVALUATION:** Keep in mind that during edits, variables might be added, removed, or renamed inside the `content`. The Vanilla JS MUST re-parse the newly saved `content` with the regex and entirely rebuild the dynamic `<textarea>` inputs to reflect the exact current state of the variables. Old/removed variables must disappear from the form, and new ones must be generated.
- Action - Copy to Clipboard:
  - Provide a "Copy" button using a Lucide icon.
  - When clicked, a JS function must:
    1. Read the values inputted by the user in the generated textareas. **CRUCIAL:** Preserve all line breaks (newlines / `\n`) entered by the user. If a user types a multi-line text (e.g., "Gustavo\nGurgel") into a variable's textarea, those exact line breaks must be maintained.
    2. Replace all `[[Variable Name]]` tags in the original content with the user's inputs, keeping the original formatting intact.
    3. Copy the final string to the user's clipboard using the `navigator.clipboard` API.
    4. Call the backend endpoint to update the `last_copied_at` timestamp for this template.
    5. Refresh/reorder the UI list so this recently copied template jumps to the top.
- Practical Example of the logic:
  - Content: "Hello, my name is [[Name]] and I am [[Age]] years old."
  - UI shows two textareas: "Name" and "Age".
  - User types "Gustavo" and "22".
  - On copy, clipboard receives: "Hello, my name is Gustavo and I am 22 years old."

- Local Assets: You MUST use local paths for CSS and JS. Do not use CDNs.
    - CSS: <link rel="stylesheet" href="css/pico.min.css" />
    - JS: <script src="static/lucide.js"></script>
- UI Layout: Clean, responsive design using Pico CSS.
- Dynamic Icons: Render Lucide icons dynamically based on user input. Example:
  <i data-lucide="copy"></i>. Always call lucide.createIcons() after DOM mutations.

BACKEND REFERENCE CODE: Follow this dependency injection and routing pattern:

from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Field, Session, SQLModel, select
from apps.engine import get_session # Use this exact import for the session
from typing import Annotated

SessionDep = Annotated[Session, Depends(get_session)]

def prompt_templates(app: FastAPI):
    # Your routes here using @app.post, @app.get, etc.

Create the app with the above specifications.
