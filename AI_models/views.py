from django.shortcuts import render
from django.http import HttpResponse, QueryDict, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from network.questions import radioQuestions, mentalQuestions
from .models import *


import torch
import numpy as np
from torch import nn
from transformers import XLNetForSequenceClassification, XLNetTokenizer,BertForSequenceClassification,BertTokenizer, RobertaForSequenceClassification,RobertaTokenizer
from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer
from scipy.special import softmax
from typing import Dict

# Create your views here.
model = BertForSequenceClassification.from_pretrained("AI_models/Personality_detection_Classification_Save", num_labels=5)#=num_labels)
model2 = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
model3 = AutoModelForSequenceClassification.from_pretrained("edmundhui/mental_health_trainer", use_auth_token=True)

tokenizer = BertTokenizer.from_pretrained('AI_models/Personality_detection_Classification_Save', do_lower_case=True) 
tokenizer2 = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
tokenizer3 = AutoTokenizer.from_pretrained("edmundhui/mental_health_trainer", use_auth_token=True)

model.config.label2id= {
    "Extroversion": 0,
    "Neuroticism": 1,
    "Agreeableness": 2,
    "Conscientiousness": 3,
    "Openness": 4,
}

model.config.id2label={
    "0": "Extroversion",
    "1": "Neuroticism",
    "2": "Agreeableness",
    "3": "Conscientiousness",
    "4": "Openness",}

mental_illness_dict = {0: "ADHD/Anxiety/Mood disorder",
                       1: "Aspergers/Schizophrenia",
                       2: "Depression/Bipolar disorder",
                       3: "OCD/Eating disorder/BDD",
                       4: "PTSD/BPD"}

def personality_detect(request):
    if request.method=="GET":
        convert_answer_dict = {
            1: "I disagree with the statement that",
            2: "I partially agree with the statement that",
            3: "I totally agree with the statement that"
        }
        user_answer = request.session.get("user_answer")

        final_answer = ""
        for index, key in enumerate(user_answer):
            if index != 0:
                question = radioQuestions[index-1]["question"]
                text_answer = convert_answer_dict[int(user_answer[key])]
                final_answer += f"{text_answer} {question}. "
        print(final_answer)

        personalities_output = AI_model1(final_answer)

        personalities_obj = PersonalityDetectionModel(personalities=personalities_output)
        personalities_obj.save()

        prediction = []
        for personality, percentage in personalities_output:
            formatted_trait = f"{personality} with {int(percentage*100)}% "
            prediction.append(formatted_trait)

        return render(request, "AI_models/result.html", {'prediction': prediction})
    else:
        return HttpResponse("Response message")


def mental_detect(request):
    if request.method=="GET":
        mental_answer = request.session.get("mental_answer")
        # print(mental_answer)
        final_answer = ""
        for index, key in enumerate(mental_answer):
            if index != 0:
                if int(mental_answer[key]) == 3:
                    question = mentalQuestions[index-1]["question"]
                    final_answer += f"{question}. "
        print(final_answer)
        mentals_output = AI_model_3(model3, tokenizer3, final_answer)

        mentals_obj = MentalHealthDetectionModel(mental_illness=mentals_output)

        return render(request, "AI_models/result2.html", {'prediction': mentals_output})
    else:
        return HttpResponse("Response message")


@csrf_exempt
def sentiment_analysis(request):
    if request.method=="POST":
        text = request.POST.get("content_text","")
        
        # Get prediction
        score = AI_model_2(model2, tokenizer2, text)
        score = score.tolist()

        return JsonResponse({'result': score})
    else:
        # return render(request, "AI_models/result2.html")   
        return JsonResponse({'error': 'Method must be POST.'})


def AI_model1 (model_input: str) -> Dict[str, float]:
    if len(model_input)<10:
        ret ={
            "Extroversion": float(0),
            "Neuroticism": float(0),
            "Agreeableness": float(0),
            "Conscientiousness": float(0),
            "Openness": float(0),}
        return ret
    else:
        # Encoding input data
        dict_custom={}
        Preprocess_part1=model_input[:len(model_input)]
        Preprocess_part2=model_input[len(model_input):]
        dict1=tokenizer.encode_plus(Preprocess_part1,max_length=1024,padding=True,truncation=True)
        dict2=tokenizer.encode_plus(Preprocess_part2,max_length=1024,padding=True,truncation=True)
        dict_custom['input_ids']=[dict1['input_ids'],dict1['input_ids']]
        dict_custom['token_type_ids']=[dict1['token_type_ids'],dict1['token_type_ids']]
        dict_custom['attention_mask']=[dict1['attention_mask'],dict1['attention_mask']]
        outs = model(torch.tensor(dict_custom['input_ids']), token_type_ids=None, attention_mask=torch.tensor(dict_custom['attention_mask']))
        b_logit_pred = outs[0]
        pred_label = torch.sigmoid(b_logit_pred)
        ret ={
            "Extroversion": float(pred_label[0][0]),
            "Neuroticism": float(pred_label[0][1]),
            "Agreeableness": float(pred_label[0][2]),
            "Conscientiousness": float(pred_label[0][3]),
            "Openness": float(pred_label[0][4]),}

        top5_output = sorted(ret.items(), key=lambda x: x[1], reverse=True)[:5]

        return top5_output

def AI_model_2(model, tokenizer, user_input):
    text = preprocess(user_input)
    encoded_input = tokenizer(text, return_tensors='pt')
    output = model(**encoded_input)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    return scores

def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)


def AI_model_3(model, tokenizer, user_input):
    inputs = tokenizer(user_input, return_tensors="pt")
    outputs = model(**inputs)[:1][0]
    proba = nn.functional.softmax(outputs, dim=-1)
    probas, indices = torch.topk(proba, k=5)
    top_probs = probas.tolist()[0]
    top_predict_values = indices.tolist()[0]
    # print(top_predict_values)
    mental_list = []
    for i in range(len(top_predict_values)):
        mental_list.append(f"{mental_illness_dict[int(top_predict_values[i])]} with {round(top_probs[i]*100, 2)}%")

    return mental_list