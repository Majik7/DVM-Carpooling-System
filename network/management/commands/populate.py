from django.core.management.base import BaseCommand
from network.models import Node, Edge

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Node.objects.all().delete()
        Edge.objects.all().delete()

        # Create nodes
        a = Node.objects.create(name='A')
        b = Node.objects.create(name='B')
        c = Node.objects.create(name='C')
        d = Node.objects.create(name='D')
        e = Node.objects.create(name='E')
        f = Node.objects.create(name='F')
        g = Node.objects.create(name='G')
        h = Node.objects.create(name='H')
        i = Node.objects.create(name='I')
        j = Node.objects.create(name='J')

        # Main route: A -> B -> C -> D -> E
        Edge.objects.create(prev_node=a, next_node=b)
        Edge.objects.create(prev_node=b, next_node=c)
        Edge.objects.create(prev_node=c, next_node=d)
        Edge.objects.create(prev_node=d, next_node=e)

        # Alternate path: A -> F -> G -> D
        Edge.objects.create(prev_node=a, next_node=f)
        Edge.objects.create(prev_node=f, next_node=g)
        Edge.objects.create(prev_node=g, next_node=d)

        # Side branches for proximity testing
        Edge.objects.create(prev_node=b, next_node=h)
        Edge.objects.create(prev_node=h, next_node=i)
        Edge.objects.create(prev_node=c, next_node=j)

        # One-way connections back
        Edge.objects.create(prev_node=e, next_node=j)
        Edge.objects.create(prev_node=j, next_node=g)

        self.stdout.write(self.style.SUCCESS('Network populated!'))
