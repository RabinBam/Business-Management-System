# Install Byapari on your PC

Each person installs their own copy and supplies their own API key. The app opens
in a web browser on that PC. It is a local web application, not a Windows .exe.

## 1. Install the prerequisite

Install [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/).
Follow its WSL 2 setup instructions, restart Windows if requested, and start Docker
Desktop. Wait for the engine to say it is running. Use Linux containers. You do not
need to install Python or Node.js when using Docker.

## 2. Get the project

Use the supplied **Byapari-PC.zip** for this completed version. Extract it into a local folder
such as `C:\Byapari`, or clone it:

```powershell
git clone https://github.com/RabinBam/Business-Management-System.git Byapari
cd Byapari
```

Make sure your copy includes `Start-Byapari.cmd` and the OpenRouter setting in
`.env.example`. Changes from a local development copy must be shared or pushed
before another PC can download them from GitHub.

## 3. Put your key in .env

In the project folder, copy `.env.example` to `.env`. Windows Explorer may hide file
extensions: enable **View → Show → File name extensions** so the file is not named
`.env.txt`. Open `.env` in a text editor. You can also use PowerShell:

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

For an offline showcase, leave `AI_PROVIDER=mock`. All workflow stages work without
credentials, using deterministic sample outputs.

For real OpenRouter generation, change these lines in `.env`:

```dotenv
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=replace-with-your-own-key
AI_PRIMARY_MODEL=nvidia/nemotron-3-super-120b-a12b:free
AI_WORKER_MODEL=nvidia/nemotron-3-super-120b-a12b:free
AI_TIMEOUT_SECONDS=60
```

Create your key in [OpenRouter's key settings](https://openrouter.ai/settings/keys).
Choose a model ID from the [model catalog](https://openrouter.ai/models) whose
provider supports structured outputs. The app requests JSON schema support;
unsupported model/provider combinations fail visibly rather than switching to
mock data. See [OpenRouter's structured-output guide](https://openrouter.ai/docs/guides/features/structured-outputs).
Leave `AI_WORKER_MODEL` blank to use the primary model for workers too.

The key stays in the backend environment; it is not sent to the browser or stored
in SQLite. `.env` is excluded from Git. It is still a plain-text file on your PC:
do not share it, include it in a ZIP, or show it in a presentation. Never put a key
in a `NEXT_PUBLIC_` variable. Each recipient creates their own `.env`.

Real AI mode sends workflow content to OpenRouter and its selected provider and
may incur charges. The workflow business budget is an estimated planning budget;
it does not cap API spending. Set an appropriate credit limit on your provider key.

## 4. Start the app

Double-click **Start-Byapari.cmd**. Keep the first installation online while Docker
downloads dependencies and builds the app. This may take several minutes.

Alternatively, run this from the project folder:

```powershell
docker compose -f docker-compose.yml up -d --build --wait --wait-timeout 180
```

The explicit file name selects the production build and avoids the automatic
development override. Open:

- App: [http://localhost:3000](http://localhost:3000)
- Backend health: [http://localhost:8000/health](http://localhost:8000/health)
- API reference: [http://localhost:8000/docs](http://localhost:8000/docs)

Both services bind to this PC only. Closing the browser does not stop the app.
Double-click **Stop-Byapari.cmd** to stop it. Run the start file again to resume.

After changing a key or model, run the start file again (or the same Compose `up`
command) to recreate the backend environment. A simple container restart does not
load changed `.env` values.

## 5. Present the complete workflow

1. Open Command Center. Enter your own objective, budget and deadline. Leave
   **Employees submit work; AI reviews it** selected for employee participation.
   Optional revenue history must be consecutive monthly amounts, oldest first.
2. Create the workflow and run it to prepare the AI plan. All six employees receive
   distinct tasks, experience-tailored instructions, acceptance criteria and
   department handoff notes. Open **Tasks & teams** to inspect assignments.
3. Open **Employee workspace**, select a name, read the assigned work, paste the
   completed deliverable and press **Submit for review**. Prerequisite tasks must
   be submitted first. Repeat for the assigned employees. This local selector
   does not provide private employee accounts or authentication.
4. Return to the workflow and choose **Review submitted work**. AI checks the
   deliverables. If revisions are requested, employees amend and resubmit those
   tasks. Approved work stays approved. Completion tracks reviewed tasks.
5. After approval, open Reports, Marketing and Executive Summary. Marketing uses
   team deliverables and the remaining planning budget. Save any marketing edits,
   then refresh the CEO summary to incorporate the updated plan.
6. Record actual income and expenses in **Money**. These are bookkeeping entries,
   not payments. Reports allocate 60% of the objective budget to estimated task
   costs and cap marketing at the remaining 40%. Employee salaries and actual
   income are never invented. Sales forecasts require your monthly revenue data.
7. Stop and start the app to verify that saved work persists. For an AI-written
   showcase, choose **AI generates written deliverables** when creating a separate
   objective. This generates drafts, not external business actions.

The free model has provider availability and usage limits. Keep both model IDs
ending in `:free`; there is no automatic switch to a paid model. An entire AI-run
workflow uses several calls and can take several minutes. Planning and reviews
are batched, and handoff context is capped to limit tokens. Employee mode avoids
six automatic worker-writing calls. Mock mode is explicitly simulated offline AI.

## Troubleshooting and data

- **Docker connection error:** start Docker Desktop, wait for its Linux engine,
  then run the start file again.
- **Backend does not start:** check your provider, key, and model settings. Run
  `docker compose -f docker-compose.yml logs --tail 80 backend`.
- **AI request fails:** check key validity, remaining credits, model availability,
  structured-output support, and internet access. Correct the configuration,
  rerun the start file, then use **Retry Workflow** for a failed workflow.
- **Port in use:** stop the conflicting app or change `FRONTEND_PORT`,
  `BACKEND_PORT`, `FRONTEND_ORIGIN`, and `NEXT_PUBLIC_API_URL` together in `.env`,
  keeping the browser URLs consistent, then rerun the start file.
- **Verify containers:** `docker compose -f docker-compose.yml ps` should show
  the backend healthy and the frontend running.
- **Data:** SQLite is in `/app/data/aegisflow.db` in the backend container, backed
  by the `backend_data` Docker volume. Stop the app before copying the database
  with `docker compose -f docker-compose.yml cp backend:/app/data/aegisflow.db ./aegisflow-backup.db`.
  Keep backups private. Do not use `docker compose down -v` or delete Docker volumes
  unless you intend to erase the stored workflows.

For native Python/Node development, see the root README. For a shared public
deployment, add organizational authentication and HTTPS before exposing the app.

## Presentation reset and quick completion

AI Workforce has **Quick complete tasks (demo)**. Prepare a workflow first; the
button marks its tasks complete and bypasses review, clearly labeling all simulated
results. Continue the workflow to generate reports, marketing and the CEO summary.

Each Start-Byapari launch recreates the app and resets saved work and money.
Employees and API keys are preserved. The database is backed up before reset in
the Docker data volume as byapari-before-launch-*.db. Browser refresh does not reset
data. To retain work across launches, set RESET_DEMO_ON_START=false in .env.
