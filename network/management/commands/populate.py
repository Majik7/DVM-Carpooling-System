from django.core.management.base import BaseCommand
from network.models import Node, Edge

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if Node.objects.exists():
            self.stdout.write('Network already populated, skipping.')
            return

        Node.objects.all().delete()
        Edge.objects.all().delete()

        node_names = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O']
        nodes = {}
        for name in node_names:
            nodes[name] = Node.objects.create(name=name)

        for i in range(len(node_names) - 1):
            src = node_names[i]
            dst = node_names[i + 1]
            Edge.objects.create(prev_node=nodes[src], next_node=nodes[dst])

        self.stdout.write(self.style.SUCCESS('Network populated'))