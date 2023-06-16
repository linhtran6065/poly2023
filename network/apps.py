from django.apps import AppConfig


class NetworkConfig(AppConfig):
    name = 'network'

    #fix cứng 3 community
    def ready(self):
        from .models import Community
        catcommunity = Community(community_id=1, name='CatCommunity', description='Community for Cat Lovers', cover='https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2043&q=80')
        catcommunity.save()
        b = Community(community_id=2, name='b', description='Example', cover='https://images.unsplash.com/photo-1519052537078-e6302a4968d4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=870&q=80')
        b.save()
        c = Community(community_id=3, name='c', description='Example', cover='https://images.unsplash.com/photo-1494256997604-768d1f608cac?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=929&q=80')
        c.save()
        pass