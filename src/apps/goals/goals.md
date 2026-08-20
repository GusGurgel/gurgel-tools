You are a Senior Fullstack Developer specializing in Python (FastAPI, SQLModel)
and Frontend (HTML5, Vanilla JS, Pico CSS).

I am building a project called gurgel-tools, a hub of various tools. The backend
serves HTML files and exposes a REST API. The technology stack is:

  - Backend: FastAPI with SQLModel (for database persistence).
  - Frontend: Pure HTML, Pico CSS (styling), and Lucide (icons). No JS
    frameworks, only Vanilla JS.

PROJECT ARCHITECTURE: Each app in the hub consists of two main files:

1.  goals.py: Contains SQLModel classes, Pydantic schemas, and a main
    function goals(app: FastAPI) that registers the routes.
2.  goals.html: The UI, using Pico CSS and Lucide.

CURRENT GOAL: Develop an application called "Goals". This app allows users to track integer-based objectives (e.g., "Solve 40 security questions", "Model 5 houses", "4 hours reading") by adding increments over time.

DATABASE MODELING (SQLModel):
Create the following models with their respective relationships:

1. Goal:
   - `id`: Primary key.
   - `name`: String.
   - `target`: Integer (The value the user wants to reach).
   - `metric`: String (What the value represents, e.g., "questions", "hours", "models". Used for UI like "10/30 models").
   - `created_at`: Datetime.
   - `updated_at`: Datetime.
   - `completed_at`: Datetime, nullable (If null, goal is open. If populated, it holds the datetime when the goal was marked as completed).
   - Relationship: One-to-many with Increments. (A Goal's current progress is the sum of the `value` of all its increments).

2. Increment:
   - `id`: Primary key.
   - `goal_id`: Foreign key.
   - `value`: Integer (Required. The amount added to the goal).
   - `image_url`: String, nullable (Optional URL for an image attached to the increment).
   - `created_at`: Datetime.

BACKEND REQUIREMENTS:
  - Implement full CRUD for Goals and Increments.
  - Endpoints to create, edit (name and target), and fetch goals.
  - Endpoints to create, edit (value, image_url), and delete increments.
  - Sorting Logic: When fetching the list of goals, they MUST be ordered by the `created_at` date of their LATEST increment in descending order. For example: if Goal A had an increment on Aug 13, and Goal B had one on Aug 10, Goal A appears first. Goals with no increments go to the bottom.
  - Goal Completion Endpoint: A route to mark a goal as completed (setting `completed_at` to the current datetime). Validate that the sum of its increments is >= `target`.
  - Motivational Quotes feature: 
    - Hardcode a list of 100 motivational quotes in English (from Stoic philosophers and the Bible).
    - Create a GET route that returns ONE quote. 
    - The quote selection must be tied to the current calendar date (e.g., using a modulo operation based on the day of the year) so that no matter how many times the endpoint is called on a given day, it returns the exact same quote, changing only on the next day.

FRONTEND REQUIREMENTS:
  - Dark layout.
  - Local Assets: You MUST use local paths for CSS and JS. Do not use CDNs.
      - CSS: <link rel="stylesheet" href="css/pico.min.css" />
      - JS: <script src="static/lucide.js"></script>
  - UI Layout: Clean, responsive design using Pico CSS.
  - Dynamic Icons: Render Lucide icons dynamically based on user input. Always call `lucide.createIcons()` after DOM mutations.
  - Daily Quote: Display the daily motivational quote fetched from the API at the top of the screen.
  - Main Goal List: 
    - Display all goals in a summarized card format showing: Name, Progress Text (e.g., "10/30 models"), and a Progress Bar showing the percentage completed.
    - Elapsed Time Display: Format as `{DAYS}d {HOURS}h` (e.g., `2d 10h`). 
      - If completed: Calculate time between `created_at` and `completed_at`.
      - If NOT completed: Calculate dynamically in JS between `created_at` and `Date.now()`.
  - Goal Interaction & Timeline:
    - The increment timeline is hidden by default. When the user clicks on a Goal card, expand it to show its timeline of increments (newest to oldest).
    - If the goal is NOT completed, show the "Add Increment" form inside the expanded view: a numeric input for the value, a text input for the optional image URL, and an "Add" button. Upon clicking "Add", submit to API, reset inputs to empty/zero, and refresh the UI.
    - Each increment in the timeline should display:
      - The text formatted as `+{value} {metric}` (e.g., "+2 questions").
      - The image, rendered if `image_url` is provided.
      - Edit/Delete buttons (allowing the user to change the value or image).
  - Goal Actions:
    - Provide a button to edit the Goal's name and target.
    - Provide a "Complete Goal" button. This button MUST be visually disabled/unclickable unless the current sum of increments is >= the target.
    - If a goal is marked as completed, the "Add Increment" form must be hidden/removed. The timeline remains visible for historical purposes.

BACKEND REFERENCE CODE: Follow this dependency injection and routing pattern:

from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Field, Session, SQLModel, select
from apps.engine import get_session # Use this exact import for the session
from typing import Annotated

SessionDep = Annotated[Session, Depends(get_session)]

def goals(app: FastAPI):
    # Your routes here using @app.post, @app.get, etc.
