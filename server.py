import uvicorn
from server.app import app

def main():
    """
    Convenience entry point for starting the FastAPI server.
    Matches the instructions in the README.MD
    """
    print("Starting Supply Chain Disruption Triage OpenEnv Server...")
    uvicorn.run(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()
