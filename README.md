## Overview

This project utilizes a Retrieval-Augmented Generation (RAG) approach to recommend underground music artists. Users provide a text prompt describing their desired musical style or mood, and the system retrieves relevant information from a database of underground artists. This information is then used to generate a personalized list of artist recommendations.

## Features

*   **Prompt-Based Recommendations:** Users can input a text prompt to describe the type of music they are looking for.
*   **Underground Focus:** The system is specifically designed to recommend lesser-known, underground artists.
*   **RAG Architecture:** Leverages a RAG model to combine information retrieval with text generation.
* **Database:** Uses a database of underground artists.

## Getting Started

### Prerequisites

*   Python 3.x
*   Dependencies listed in `requirements.txt`

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/aidanschneider17/underground-music-picker.git
    ```
2.  Navigate to the project directory:
    ```bash
    cd underground-music-picker
    ```
3.  Install the required dependencies:
    ```bash
    pip3 install -r requirements.txt
    ```

### Setting Up Google Cloud

- Make sure to install Google Cloud CLI: https://cloud.google.com/sdk/docs/install-sdk
- Set up the Application Default Credentials: https://cloud.google.com/docs/authentication/provide-credentials-adc#how-to
- Enable Vertex APIs: https://console.cloud.google.com/vertex-ai

In `embed_albums.py` change the MODEL_ID and REGION_ID to your configuration.

### Usage

1.  Run the main script:
    ```bash
    python3 main.py
    ```
2.  Enter your prompt when requested.
3.  The system will generate a list of recommended artists.

## License

This project is licensed under the MIT License.

