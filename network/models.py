from django.db import models

# Create your models here.
class Node(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)

class Edge(models.Model):
    prev_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="start_from", blank=True, null=True)
    next_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="come_in", blank=True, null=True)
