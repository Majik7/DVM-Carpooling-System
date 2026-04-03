from django.db import models

# Create your models here.
class Node(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

class Edge(models.Model):
    prev_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="outgoing", blank=True, null=True)
    next_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="incoming", blank=True, null=True)

    def __str__(self):
        return f"{self.prev_node} - {self.next_node}"

class ServiceStatus(models.Model):
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"active - {int(self.is_active)}"