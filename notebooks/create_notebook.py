import json


# Define the notebook structure
notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["# CrewAI LLM Test\n", "\n", "This notebook demonstrates how to create and use a CrewAI LLM."],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import os\n",
                "import sys\n",
                "\n",
                "# Add the project root to the Python path\n",
                "sys.path.append('..')\n",
                "\n",
                "# Import our modules\n",
                "from src.llm.llm_factory import LLMFactory, LLMType\n",
                "\n",
                "# Create an LLM using the factory\n",
                "llm = LLMFactory.create_llm(LLMType.LOCAL_FAST)  # or CLOUD_FAST if you have an API key\n",
                "\n",
                "# Test the LLM\n",
                'response = llm.invoke("Hello, this is a test.")\n',
                'print(f"LLM Response: {response}")',
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Create a CrewAI agent using the LLM\n",
                "from crewai import Agent\n",
                "\n",
                "# Create a simple agent\n",
                "agent = Agent(\n",
                '    role="Medical Assistant",\n',
                '    goal="Assist healthcare professionals with patient information",\n',
                '    backstory="You are an AI assistant specialized in healthcare.",\n',
                "    llm=llm,\n",
                "    verbose=True\n",
                ")\n",
                "\n",
                "# Test the agent\n",
                'result = agent.execute("Summarize the following medical text: The patient presents with a 3-day history of headache.")\n',
                'print(f"Agent Result: {result}")',
            ],
        },
    ],
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.13.0",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 2,
}

# Write the notebook to a file
with open("crewai_llm_test.ipynb", "w") as f:
    json.dump(notebook, f, indent=1)

print("Notebook created successfully: crewai_llm_test.ipynb")
