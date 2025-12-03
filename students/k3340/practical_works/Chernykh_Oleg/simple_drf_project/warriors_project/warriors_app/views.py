from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .serializers import (
    WarriorSerializer, SkillSerializer, ProfessionSerializer, ProfessionCreateSerializer, 
    WarriorCreateSerializer, WarriorWithProfessionSerializer, WarriorWithSkillsSerializer,
    WarriorNestedSerializer
)
from .models import Warrior, Skill, Profession


class WarriorAPIView(APIView):
   def get(self, request):
       warriors = Warrior.objects.all()
       serializer = WarriorSerializer(warriors, many=True)
       return Response({"Warriors": serializer.data})

class ProfessionCreateView(APIView):

   def post(self, request):
       print("REQUEST DATA", request.data)
       profession = request.data.get("profession")
       print("PROF DATA", profession)

       serializer = ProfessionCreateSerializer(data=profession)
       if serializer.is_valid(raise_exception=True):
           profession_saved = serializer.save()

       return Response({"Success": "Profession '{}' created succesfully.".format(profession_saved.title)})


class WarriorListAPIView(generics.ListAPIView):
   serializer_class = WarriorSerializer
   queryset = Warrior.objects.all()

class WarriorCreateAPIView(generics.CreateAPIView):
   serializer_class = WarriorCreateSerializer
   queryset = Warrior.objects.all()
   # permission_classes = [permissions.AllowAny]


   def perform_create(self, serializer):
       serializer.save(owner=self.request.user) 

class ProfessionCreateAPIView(generics.CreateAPIView):
   serializer_class = ProfessionCreateSerializer
   queryset = Profession.objects.all()

class SkillAPIView(APIView):
   def get(self, request):
       skills = Skill.objects.all()
       serializer = SkillSerializer(skills, many=True)
       return Response({"Skills": serializer.data})

   def post(self, request):
       serializer = SkillSerializer(data=request.data)
       if serializer.is_valid(raise_exception=True):
           skill_saved = serializer.save()
       return Response({"Success": "Skill '{}' created successfully.".format(skill_saved.title)})

class WarriorWithProfessionAPIView(APIView):
    def get(self, request):
        warriors = Warrior.objects.all()
        serializer = WarriorWithProfessionSerializer(warriors, many=True)
        return Response({"Warriors": serializer.data})

class WarriorWithSkillsAPIView(APIView):
    def get(self, request):
        warriors = Warrior.objects.all()
        serializer = WarriorWithSkillsSerializer(warriors, many=True)
        return Response({"Warriors": serializer.data})

class WarriorDetailAPIView(APIView):
    def get(self, request, pk):
        warrior = get_object_or_404(Warrior, pk=pk)
        serializer = WarriorNestedSerializer(warrior)
        return Response({"Warrior": serializer.data})

    def put(self, request, pk):
        warrior = get_object_or_404(Warrior, pk=pk)
        serializer = WarriorSerializer(warrior, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"Success": "Warrior updated successfully.", "Warrior": serializer.data})

    def patch(self, request, pk):
        warrior = get_object_or_404(Warrior, pk=pk)
        serializer = WarriorSerializer(warrior, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"Success": "Warrior updated successfully.", "Warrior": serializer.data})

    def delete(self, request, pk):
        warrior = get_object_or_404(Warrior, pk=pk)
        warrior.delete()
        return Response({"Success": "Warrior deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
