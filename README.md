## Demo
![Demo](https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png)

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Introduction
AI-English-Tutor-Linebot is a personalized AI English tutor that integrates OpenAI and Google Text-to-Speech models. This project aims to provide an interactive and efficient way to learn English through a Line bot. We use multiple APIs to create a personalized AI English tutor. The teacher will record the students' learning status, regularly reflect on the students' learning status, and give more appropriate feedback to the students.
## Features
- Personalized English tutoring using AI.
- Text-to-speech functionality for pronunciation practice.
- Interactive learning sessions through the Line chat app.

## Project structure
```
files/
  └── .keep
src/
  ├── audio.py
  ├── models.py
  ├── speech.py
  ├── storage.py
tinydb/
  └── .keep
.gitignore
LICENSE
README.md
main.py
requirements.txt
```

## Project details
- API used:
    - OpenAI whisper1 API
    - OpenAI GPT-4o API
    - Google Cloud Text-to-Speech API
    - Line Developer Messaging API
- Deployment:
    - [Replit platform](https://replit.com/@132548t/AI-English-Tutor-Linebot?v=1#README.md)
- CronJob: Since Replit will automatically stop if there are no requests for a period of time, we need to set up a task to send requests regularly to keep the service running. This prevents LINE Bot from stopping due to no requests for a long time.

## Installation
To install and run this project, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/GuanRuLai/AI-English-Tutor-Linebot.git
    ```
2. Navigate to the project directory:
    ```bash
    cd AI-English-Tutor-Linebot
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
To start the Line bot, run the following command:
```bash
python main.py
```

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/GuanRuLai/AI-English-Tutor-Linebot/blob/main/LICENSE) file for details.

## Acknowledgements
Thanks to [explainthis.io's repository](https://github.com/TheExplainthis/ChatGPT-AI-English-Tutor) for providing inspiration and valuable resources to refer and modify.
