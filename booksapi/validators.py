from rest_framework import serializers
from datetime import datetime

def year_not_from_future(passed_year):
    current_year = datetime.now().year
    print(current_year)
    if passed_year > current_year:
        raise serializers.ValidationError('You cannot give a future year.')