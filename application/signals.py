from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from application.models import Property, AgentProperties


@receiver(post_save, sender=Property)
def check_if_sold(sender, instance,  **kwargs):
    if instance.sold is True:
        agents = AgentProperties.objects.filter(property=instance)
        for agent_prop in agents:
            agent_prop.agent.num_sales += 1
            agent_prop.agent.save()