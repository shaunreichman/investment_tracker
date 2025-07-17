# Web App Development Tasks: Investment Tracker (React + Flask)

## Overview
This document outlines the tasks for building a local web-based application to manage and view investment data, modeled after the Alceon spreadsheet's UI/UX. **All data, calculations, and business logic will come from the existing Python codebase and database, exposed via a Flask API. The frontend will be built in React for a modern, interactive experience.**

The project will be developed in multiple stages:
- **Stage 1:** Project Setup (Flask API + React Frontend)
- **Stage 2:** Summary Dashboard (All Funds Overview)
- **Stage 3:** Fund Detail Page (Individual Fund View)
- **Stage 4:** Integration, Testing, and Enhancements

---

## Stage 1: Project Setup

### Goal
Establish a robust project structure for a Flask backend API and a React frontend, ready for development and integration.

### Tasks
1. **Backend (Flask API) Setup**
   - [x] Set up a new Flask project (or extend existing backend)
   - [x] Configure CORS to allow requests from the React frontend
   - [x] Add a health check endpoint (`/api/health`) that returns JSON
   - [x] Test Flask API is running and accessible from browser/curl
   - [ ] Organize backend code for API endpoints (e.g., `src/api/`)

2. **Frontend (React) Setup**
   - [x] Scaffold a new React app (using Create React App with TypeScript)
   - [x] Set up project structure (components, pages, services, etc.)
   - [x] Create a simple component that fetches from the Flask API health endpoint and displays the result
   - [ ] Configure environment variables for API base URL
   - [ ] Install dependencies (axios/fetch, UI library if desired)

3. **Development Workflow**
   - [ ] Set up scripts for running backend and frontend concurrently (e.g., with `concurrently` or separate terminals)
   - [x] Document setup and run instructions in README (in progress)

---

## Stage 2: Summary Dashboard (All Funds Overview)

### Goal
Build a React page that displays a summary table of all funds within a company, closely mirroring the "Summary" sheet in the spreadsheet for layout and content, but sourcing all data and calculations from the Flask API.

### Tasks
1. **Backend (Flask API)**
   - [ ] Design and implement an API endpoint to return summary data for all funds (e.g., `/api/funds/summary`)
   - [ ] Ensure all calculations and aggregations match the logic in the Python codebase
   - [ ] (Optional) Add filtering/searching by fund name, type, etc.

2. **Frontend (React)**
   - [ ] Design a summary dashboard page with a table layout matching the spreadsheet's summary columns (Name, Type, Entity, Commitment, Balance, IRR, etc.)
   - [ ] Fetch summary data from the Flask API
   - [ ] Render summary data in a responsive, sortable, and filterable table (consider using a table library)
   - [ ] Add links/buttons to view individual fund details (for Stage 3)
   - [ ] (Optional) Add export/download functionality

3. **Testing & Validation**
   - [ ] Validate that summary data matches what would be expected from the backend logic
   - [ ] User acceptance test: ensure usability and clarity

---

## Stage 3: Fund Detail Page (Individual Fund View)

### Goal
Build a React page for each fund, displaying detailed information and transactions, similar to the individual fund sheets in the spreadsheet, but powered by backend/database data and logic.

### Tasks
1. **Backend (Flask API)**
   - [ ] Design and implement an API endpoint to return detailed data for a specific fund (e.g., `/api/funds/<fund_id>`)
   - [ ] Ensure all relevant fields and transactions are included, and calculations match backend logic

2. **Frontend (React)**
   - [ ] Design a fund detail page to display fund metadata (name, type, entity, commitment, etc.)
   - [ ] Render a table of transactions/events (capital calls, distributions, NAV updates, etc.)
   - [ ] Show calculated fields (balances, IRR, returns, etc.)
   - [ ] Add navigation back to the summary dashboard
   - [ ] (Optional) Add editing or data entry features

3. **Testing & Validation**
   - [ ] Validate that fund detail data matches what would be expected from the backend logic
   - [ ] User acceptance test: ensure clarity and completeness

---

## Stage 4: Integration, Testing, and Enhancements

### Goal
Ensure smooth integration between frontend and backend, robust testing, and plan for future enhancements.

### Tasks
1. **Integration**
   - [ ] Test end-to-end data flow from backend to frontend
   - [ ] Handle API errors and loading states gracefully in the UI
   - [ ] Ensure CORS and environment configuration are correct

2. **Testing**
   - [ ] Write unit and integration tests for backend API endpoints
   - [ ] Write component and integration tests for React frontend
   - [ ] Validate data consistency and UI correctness

3. **Documentation**
   - [ ] Update README with setup, run, and usage instructions
   - [ ] Document API endpoints and data contracts

4. **Future Enhancements (Optional)**
   - User authentication
   - Data editing and entry
   - Multi-company support
   - Visualization (charts, graphs)
   - Import/export improvements
   - Deployment for multi-user access

---

*This document will be updated as requirements evolve or new features are requested.* 