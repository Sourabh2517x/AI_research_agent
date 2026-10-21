#  AI Research Assistant

An AI-powered research assistant built with **Python, LangChain, Groq, Tavily, and Streamlit** that automates the process of researching a topic, gathering web content, generating a structured report, and evaluating the final output.

##  Features

- **Web Search:** Finds relevant web sources using the Tavily Search API.
- **Web Scraping:** Extracts readable text from webpages using Requests and BeautifulSoup.
- **AI Research Agents:** Uses LangChain agents to coordinate web search and content extraction.
- **Automated Report Generation:** Generates structured research reports with an introduction, key findings, conclusion, and sources.
- **Critic Agent:** Reviews the generated report and provides a score, strengths, areas for improvement, and a verdict.
- **Interactive UI:** Provides a Streamlit interface for submitting research topics and viewing results.
- **Report Export:** Supports downloading the generated report in Markdown format.

##  Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| LangChain | Agent orchestration and LLM chains |
| Groq | Large language model inference |
| Tavily | Web search |
| Requests | HTTP requests for webpage retrieval |
| BeautifulSoup | HTML parsing and text extraction |
| Streamlit | Interactive web interface |
| python-dotenv | Environment variable management |

##  How It Works

The research pipeline consists of four steps:

1. **Web Search Agent** — searches the web for information relevant to the user's topic.
2. **Reader Agent** — selects a relevant URL and extracts webpage content.
3. **Writer Chain** — combines search results and scraped content to generate a structured research report.
4. **Critic Chain** — evaluates the report and provides constructive feedback.

The results are returned by the pipeline and displayed through the Streamlit interface.

##  Project Structure

```text
AI-Research-Assistant/
├── agents.py          # LLM, agents, writer and critic chains
├── tools.py           # Tavily search and webpage scraping tools
├── pipelines.py       # Four-step research pipeline
├── app.py             # Streamlit user interface
├── requirements.txt   # Python dependencies
├── .gitignore         # Excluded files and secrets
└── .streamlit/
    └── config.toml    # Streamlit theme configuration
```

##  Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Sourabh2517x/AI_research_agent
cd AI-Research-Assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Obtain your API keys from:

- [Groq Console](https://console.groq.com/)
- [Tavily](https://tavily.com/)

### 5. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal to use the application.

##  Example Use Case

Enter a topic such as:

> Recent developments in Generative AI

The application searches for relevant web sources, extracts webpage content, generates a research report, and evaluates the report using an AI critic.

##  Learning Outcomes

This project provided practical experience with:

- Building tool-using agents with LangChain.
- Integrating LLMs through Groq.
- Performing web search and webpage scraping.
- Connecting multiple LLM stages into a research pipeline.
- Building interactive applications with Streamlit.
- Generating and evaluating AI-written reports.