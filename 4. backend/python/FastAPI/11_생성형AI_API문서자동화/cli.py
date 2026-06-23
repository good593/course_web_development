import sys

from pipeline import run_diff, run_pipeline, save_collection
from services.document_generator import generate_api_docs, generate_postman_collection, generate_readme
from services.openapi_spec import fetch_openapi_spec
from services.storage import save_output


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "pipeline"
    server_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8001"

    if command == "pipeline":
        run_pipeline(server_url)

    elif command == "docs":
        spec = fetch_openapi_spec(server_url)
        docs = generate_api_docs(spec)
        save_output(docs, "API_DOCS.md")

    elif command == "collection":
        spec = fetch_openapi_spec(server_url)
        raw = generate_postman_collection(spec)
        save_collection(raw)

    elif command == "readme":
        spec = fetch_openapi_spec(server_url)
        readme = generate_readme(spec)
        save_output(readme, "README.md")

    elif command == "diff":
        run_diff(server_url)

    else:
        print("사용법: python main.py [pipeline|docs|collection|readme|diff] [server_url]")
