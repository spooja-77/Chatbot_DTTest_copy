# ⚙️ DownBot — Factory Downtime Intelligence Chatbot

> An LLM + RAG-powered chatbot that lets you query your manufacturing downtime data in plain English.  
> Built with **Streamlit** · **Anthropic Claude** · deployable on **Streamlit Community Cloud** in minutes.

---

## 🚀 Live Demo

> After deployment, your link will look like:  
> `https://<your-app-name>.streamlit.app`

---

## ✨ Features

| Feature | Details |
|---|---|
| 🤖 **5 Personality Modes** | Analyst, Engineer, Executive, Teacher, Detective — each with a distinct answering style |
| 📊 **RAG Data Context** | Entire dataset summarised and injected into every LLM call for accurate, grounded answers |
| 💬 **Multi-turn Memory** | Full conversation history maintained across turns |
| 📂 **Upload Your Own CSV** | Drag-drop your downtime CSV and the chatbot re-indexes instantly |
| 📌 **Suggested Questions** | One-click starter questions to explore the data |
| 🎨 **Dark Industrial UI** | Custom CSS dark theme with animated KPI cards |
| ⚡ **Zero Server Setup** | Runs entirely on Streamlit Cloud — no backend, no DB |

---

## 🗂️ Project Structure

```
downtime-chatbot/
├── app.py                        # Main Streamlit application
├── downtime_data.csv             # Sample dataset (replace with yours)
├── requirements.txt              # Python dependencies
├── .streamlit/
│   ├── config.toml               # Theme & server config
│   └── secrets.toml.template     # Copy → secrets.toml and add your key
├── .github/
│   └── workflows/ci.yml          # GitHub Actions lint check
└── .gitignore
```

---

## 🏗️ Local Setup

```bash
# 1. Clone
git clone https://github.com/<your-username>/downtime-chatbot.git
cd downtime-chatbot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API key
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit secrets.toml and add your real key

# 4. Run
streamlit run app.py
```

Open http://localhost:8501

---

## ☁️ Deploy to Streamlit Community Cloud (Free)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/<you>/downtime-chatbot.git
   git push -u origin main
   ```

2. **Go to** [share.streamlit.io](https://share.streamlit.io) → **New app**

3. **Select** your repo / branch `main` / file `app.py`

4. **Add Secret** in the Streamlit Cloud dashboard:  
   `Settings → Secrets` → paste:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-api03-..."
   ```

5. **Deploy** — your shareable link is ready in ~60 seconds ✅

---

## 📊 Data Format

Your CSV must have these columns (column names are case-sensitive):

| Column | Type | Description |
|---|---|---|
| `ID` | int | Unique event ID |
| `Shift` | str | Shift1 / Shift2 / Shift3 |
| `Machine_ID` | int | Machine identifier |
| `type` | int | 3 = Unplanned, 4 = Planned |
| `Start_time` | datetime | Event start |
| `Stop_time` | datetime | Event end |
| `down_time` | int | Duration in **seconds** |
| `Breakdown_Reason` | str | Human-readable reason |
| `Global_reason` | str | Category: Man / Method / Material / Machine |

Extra columns are ignored.

---

## 🔐 Security Notes

- **Never commit** `.streamlit/secrets.toml` (it's in `.gitignore`)
- Use Streamlit Cloud's built-in secrets manager for production
- The app uses `claude-opus-4-5`; switch to `claude-haiku-4-5` in `app.py` to reduce API costs

---

## 🛠️ Customisation Tips

- **Swap model**: change `model="claude-opus-4-5"` in `chat()` to any Anthropic model
- **Add personalities**: extend the `PERSONALITIES` dict with new roles
- **Real database**: replace `load_data()` to connect to PostgreSQL/MySQL via `sqlalchemy`
- **Charts**: add `st.plotly_chart()` calls after the chat area for visual dashboards

---

## 📄 License

MIT — free to use and modify.
