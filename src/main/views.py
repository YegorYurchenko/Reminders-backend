""" Main views """
import asyncio
import websockets
import datetime
import random
from django.shortcuts import render

def main(request):
    return render(request, 'main/main.html')
