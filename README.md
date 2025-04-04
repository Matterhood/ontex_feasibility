# Packaging Evaluation Tool

A tool for evaluating packaging concepts using AI-powered analysis.

## Features

- Image analysis of packaging concepts
- Technical feasibility assessment
- Operational impact evaluation
- Human-in-the-loop feedback integration
- Comprehensive evaluation reports

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/packaging-evaluation-tool.git
cd packaging-evaluation-tool
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements-web.txt
```

4. Start the backend server:
```bash
python src/web/api.py
```

5. In a new terminal, start the Streamlit frontend:
```bash
streamlit run src/web/app.py
```

## Deployment

This application is deployed using Streamlit Cloud. To deploy your own version:

1. Fork this repository
2. Go to [Streamlit Cloud](https://share.streamlit.io/)
3. Click "New app"
4. Select your forked repository
5. Set the main file path to `src/web/app.py`
6. Add your environment variables in the Streamlit Cloud settings

## Environment Variables

- `API_URL`: The URL of your backend API (default: http://localhost:8000)
- `OPENAI_API_KEY`: Your OpenAI API key

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
