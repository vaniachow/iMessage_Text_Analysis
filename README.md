# Text Message Analysis

This project is designed to analyze text message data and provide insights into your interactions with friends. It includes sentiment analysis, contact information lookup, data visualization, and more.

## Features

- Clean and preprocess text messages.
- Perform sentiment analysis on messages.
- Analyze best friends and friend rankings based on message sentiment.
- Visualize sentiment distribution and message counts over time.
- Generate radar plots for individual friend analysis.
- Search and view sentiment analysis results for specific friends.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/text-message-analysis.git
2. Install the required dependencies 
    ```bash
   pip install -r requirements.txt
3. Download your iMessage texting data and save it in a folder under "imessage_export"
4. Download your contacts and save it as a csv

## Usage
1. Run the application:
   ```bash
      python app.py
2. Open a web browser and navigate to http://localhost:8050 to access the application.
3. Explore the text message analysis results and search for a friend's phone number to see data visualizations.

## Project Structure
The project has the following structure:

- app.py: The main application file that sets up the Dash app, defines callbacks, and specifies the layout. 
- complete.csv: The CSV file containing the processed text message data. 
- contacts.csv: The CSV file containing the contacts information. 
- imessage_export/: A folder to store the exported text message data. 
- static/: A folder to store static assets such as CSS stylesheets and image files. 
- templates/: A folder to store HTML templates.

## Dependencies
The project relies on the following Python libraries:
- pandas 
- dash 
- plotly 
- dash_bootstrap_components 
- re
- contractions
- nltk.stem.WordNetLemmatizer
- transformers
- datetime
- matplotlib
- nltk
- numpy
These dependencies are specified in the requirements.txt file.

## Licenses
This project is licensed under the MIT License.

## Contributing
Contributions are welcome! If you would like to contribute to this project, please follow these steps:

Fork the repository.
Create a new branch for your feature or bug fix.
Make your changes and commit them with descriptive commit messages.
Push your changes to your forked repository.
Submit a pull request explaining your changes.
