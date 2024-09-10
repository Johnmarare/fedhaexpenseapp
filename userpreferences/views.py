from django.shortcuts import render
import os
import json
from django.conf import settings
# Create your views here.


def index(request):
    currency_data=[]

    file_path=os.path.join(settings.BASE_DIR, 'currencies.json')
    
    with open(file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

        for k,v in data.items():
            currency_data.append({'name': k, 'value': v})
        

    return render(request, 'preferences/index.html', {'currencies': currency_data})