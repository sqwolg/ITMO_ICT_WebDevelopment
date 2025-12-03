from rest_framework import serializers
from .models import *


class ProfessionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Profession
		fields = ["title", "description"]

class ProfessionCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=120)
    description = serializers.CharField()

    def create(self, validated_data):
       profession = Profession(**validated_data)
       profession.save()
       return Profession(**validated_data)

class WarriorSerializer(serializers.ModelSerializer):

  class Meta:
     model = Warrior
     fields = "__all__"


class SkillSerializer(serializers.ModelSerializer):

  class Meta:
     model = Skill
     fields = "__all__"

class WarriorDepthSerializer(serializers.ModelSerializer):

    class Meta:
        model = Warrior
        fields = "__all__"
        # добавляем глубину
        depth = 1

class WarriorWithProfessionSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer(read_only=True)
    race = serializers.CharField(source="get_race_display", read_only=True)

    class Meta:
        model = Warrior
        fields = "__all__"

class WarriorWithSkillsSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(many=True, read_only=True)
    race = serializers.CharField(source="get_race_display", read_only=True)

    class Meta:
        model = Warrior
        fields = "__all__"

class WarriorNestedSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer(read_only=True)
    skill = SkillSerializer(many=True, read_only=True)

    race = serializers.CharField(source="get_race_display", read_only=True)

    class Meta:
        model = Warrior
        fields = "__all__"

class WarriorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warrior
        fields = "__all__"