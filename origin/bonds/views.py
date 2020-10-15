from bonds.models import Bond
from bonds.serializers import BondSerializer

from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions

GLIEF_API_URL = "https://leilookup.gleif.org/api/v2/leirecords?lei="

class HomePage(APIView):
    def get(self, request):
        return Response("Try '/admin' for administrative privilages, or try '/bonds' for the bonds API")

class BondAPI(generics.ListCreateAPIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BondSerializer

    def perform_create(self, serializer):
        # set owner and get and set legal name
        serializer.save(owner=self.request.user)
        serializer.setLegalName()

    def get_queryset(self):
        # filter results by owner and any other args
        filter_dict = self.request.GET.dict()
        filter_dict['owner']=self.request.user
        queryset = Bond.objects.all().filter(**filter_dict)
        return queryset
