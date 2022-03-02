from Client import Client
import os

def main():
    file_path = os.path.dirname(__file__)
    workspace_dir = os.path.join(file_path, "..")
    os.environ["workspace"] = os.path.realpath(workspace_dir)
    
    client = Client()
    client.start()

if __name__ == "__main__":
    main()


