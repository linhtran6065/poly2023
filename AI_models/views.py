from django.shortcuts import render
from django.http import HttpResponse, QueryDict
from network.questions import radioQuestions
from .models import *

from transformers import XLNetForSequenceClassification, XLNetTokenizer,BertForSequenceClassification,BertTokenizer, RobertaForSequenceClassification,RobertaTokenizer
import torch
from typing import Dict

# Create your views here.
model = BertForSequenceClassification.from_pretrained("AI_models/Personality_detection_Classification_Save", num_labels=5)#=num_labels)
tokenizer = BertTokenizer.from_pretrained('AI_models/Personality_detection_Classification_Save', do_lower_case=True) 
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

        top3_output = sorted(ret.items(), key=lambda x: x[1], reverse=True)[:3]

        return top3_output

   



