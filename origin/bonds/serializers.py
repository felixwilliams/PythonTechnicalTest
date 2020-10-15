from rest_framework import serializers
from bonds.models import Bond
from django.http import JsonResponse
import requests

GLIEF_API_URL = "https://leilookup.gleif.org/api/v2/leirecords?lei="

class BondSerializer(serializers.ModelSerializer):

    owner = serializers.HiddenField(source='owner.username',default='error: no user')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner'].read_only = True

    class Meta:
        model = Bond
        fields = ['isin', 'size', 'currency','maturity','lei','legal_name','owner']
        read_only_fields = ['legal_name']

    def validate_isin(self, value):
        if len(value) != 12:
            raise serializers.ValidationError("Error: ISIN is not of length 12")
        return value

    def validate_size(self, value):
        if value <= 0:
            raise serializers.ValidationError("Error: Size must be at least 1")
        return value

    def validate_currency(self,value):
        if len(value) != 3:
            raise serializers.ValidationError("Error: Currency is not of length 3")
        return value

    def validate_lei(self,value):
        if len(value) != 20:
            raise serializers.ValidationError("Error: LEI is not of length 20")
        return value

    def setLegalName(self):
        try:
            lei = self.validated_data['lei']
            response = requests.get(GLIEF_API_URL+lei)
            legal_name = response.json()[0]['Entity']['LegalName']['$']
        except:
            raise serializers.ValidationError("Error: Legal Name corresponding to LEI could not be found through the GLIEF API")
        self.save(legal_name=legal_name)
