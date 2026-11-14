import argparse

from src.web_app import create_server


def main():
    parser = argparse.ArgumentParser(
        description="Run the local AI reasoning evaluation application."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    options = parser.parse_args()

    server = create_server(options.host, options.port)
    print(
        "AI Reasoning Validator is running at "
        f"http://{options.host}:{options.port}"
    )
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping the application.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
