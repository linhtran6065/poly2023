from django.apps import AppConfig


class NetworkConfig(AppConfig):
    name = 'network'

    #fix cứng 3 community
    def ready(self):
        from .models import Community

        
        catcommunity = Community(community_id=1, 
                                 name='Yoga For The Soul', 
                                 description='Positive Mental Health and Wellness Coaching', 
                                 cover='https://diendanyoga.vn/wp-content/uploads/2022/03/Yoga-ngoai-troi-scaled.jpg')
        catcommunity.save()


        b = Community(community_id=2, name='Cat Lover', 
                      description='A place for cat lovers to share their love for cats', 
                      cover='https://images.unsplash.com/photo-1519052537078-e6302a4968d4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=870&q=80')
        b.save()


        c = Community(community_id=3, 
                      name='Build A Habit', 
                      description='A place for people to share their habit building journey', 
                      cover='https://www.getorganizedwizard.com/wp-content/uploads/2023/05/Start-Small-Finish-Strong-How-Tiny-Habits-Can-Lead-to-Big-Changes-in-Your-Workspace-3.jpg')
        c.save()

        #Reset the amount message with chat bot to 0
        from .models import User
        users = User.objects.all()
        for user in users:
            user.messageAmountwithBot = 0
            user.save()
        

        pass