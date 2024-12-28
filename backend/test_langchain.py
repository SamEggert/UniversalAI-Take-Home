from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

def main():
    try:
        # Initialize ChatOpenAI using the API key from the environment
        llm = ChatOpenAI(temperature=0.7)
        response = llm.invoke("Hello, world!")
        print("Response:", response)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
