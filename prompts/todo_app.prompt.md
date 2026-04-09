# Build a Todo App

Build a clean, minimal todo list web application.

## Features
- Add a new task using a text input and "Add" button (also submit on Enter key)
- Display all tasks in a list with a checkbox, label, and delete button
- Mark tasks as complete by clicking the checkbox (completed tasks show strikethrough text)
- Delete individual tasks with a trash icon button
- Show a count of remaining incomplete tasks at the bottom ("3 tasks left")
- Filter tasks: All | Active | Completed (three tab-style buttons)
- "Clear completed" button to remove all done tasks at once
- Persist all tasks in localStorage so they survive page refresh

## Design
Clean, minimal white background. Blue (#3b82f6) accent for buttons and checkboxes.
Card-style layout centered on the page (max-width 500px). Smooth fade transitions
on add/remove. System sans-serif font.

## Technical
No backend needed. Pure HTML/CSS/JS with localStorage.
Split into three files: index.html, style.css, app.js
