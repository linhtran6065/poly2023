<div align="left">
    <h1>Echoes app</h1>
</div>

<!-- ![alt text](network/media/echoes.png) -->
<img src="network/media/echoes.png" alt="isolated" width="800"/>

## Table Of Contents
-  [Description](#description)
-  [Features](#features)
-  [Project details](#project-details)
-  [Requirements](#requirements)
-  [Installation](#installation)
-  [Citation](#citation)

## Description   
Echoes is a new social networking site that addresses mental health issues. By utilizing AI to create age-, personality-, and skill-based communities, we reduce social media's harmful effects by personalizing and supporting users.

## Features
- Using chatGPT's API and pretrained NLP models on huggingface such as personalities detection, mental-illness detection, and sentiment analysis.
- Web development using Django and HTML/CSS/Javascript.
- Forming communities based on users' personalities and skills.
- Reducing toxic material and cyberbullying by checking posts and comments.
- Connecting with Mental Health Professionals if needed.

## Usecase diagram

![alt text](network/media/use_case.png)
## Project details
- For code and AI models explanation, read my blog at ...
- For installation guide, go to this link ...
- For demo video, go to this link: https://drive.google.com/file/d/1y4rOoA9je63n6BqlAEhnpeBtxOSyuacq/view?usp=sharing
## Requirements
- Django, transformers, torch, numpy, scipy, Pillow

## Installation
First, clone and set up virtual environment

```bash
# clone project   
git clone https://github.com/linhtran6065/poly2023.git
cd poly2023

# set up virtual env   
python3 -m venv echoes

# activate the env
source echoes/bin/activate  # for Unix/Linux
captionize\Scripts\activate  # for Windows
```   
Second, install dependencies.   

```bash
pip install -r requirements.txt
```  
Next, download the AI models

- Go to the link: https://drive.google.com/file/d/1MtiU-XQxl36Av3kvYmjB1CR4m6vvJ4zH/view?usp=sharing

- Download and move it inside this folder **AI_models/** 

Now run the app
```bash
# run django app
python manage.py runserver
```   

### Citation   
```
@{article{Anh Pham, Linh Tran},
  title={Echoes app},
  author={Anh Pham, Linh Tran},
  year={2023}
}
```   

