# YouTube Analysis with Streamlit

Welcome to the YouTube Analysis with Streamlit project! This project is designed to analyze and visualize data from YouTube using Streamlit, a Python library for creating web applications with interactive dashboards.

## Overview

The goal of this project is to provide insights into YouTube data, including information about video views, likes, comments, and more. The analysis is presented in an interactive and user-friendly way using Streamlit.

## Data

The dataset used for this project is retrieved from the YouTube Data API using a Google API key. The data includes information about YouTube videos, such as views, likes, comments, and upload dates.

## Usage

To run the Streamlit app for YouTube analysis, follow these steps:

1. **Obtain Google API Key:**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project or select an existing project.
   - Enable the YouTube Data API v3 for your project.
   - Create credentials (API key) and restrict it for usage with the YouTube Data API.

2. **Set Up Environment Variables:**
   - Create a `.env` file in the project root.
   - Add your Google API key to the `.env` file:

    ```
    YOUTUBE_API_KEY=your_api_key_here
    ```

3. Run the Streamlit app:

    ```bash
    streamlit run app.py
    ```

4. Open the provided URL in your web browser to interact with the YouTube analysis dashboard.


## Live Demo

You can explore the live dashboard [here](https://aloyfarera-youtube-analysis-streamlit-main-olf4ce.streamlit.app/). Feel free to interact with the app and gain insights into YouTube data!
