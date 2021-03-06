from django.db import models
from django.utils.timezone import utc
from django.conf import settings
from bambu.webhooks import helpers
from datetime import datetime
import requests, logging

LOGGER = logging.getLogger('bambu.webhooks')

class Receiver(models.Model):
	user = models.ForeignKey('auth.User', related_name = 'webhooks')
	hook = models.CharField(max_length = 100, choices = helpers.get_hook_choices(), db_index = True)
	url = models.URLField(max_length = 255, db_index = True)
	last_called = models.DateTimeField(null = True, blank = True)
	
	def __unicode__(self):
		return self.action
	
	def cue(self, data, hash):
		if hash:
			self.actions.filter(hash = hash).delete()
		
		self.actions.create(
			hash = hash,
			data = data
		)
	
	class Meta:
		unique_together = ('url', 'hook', 'user')
		ordering = ('hook',)

class Action(models.Model):
	receiver = models.ForeignKey(Receiver, related_name = 'actions')
	hash = models.CharField(max_length = 100, null = True, blank = True, db_index = True)
	data = models.TextField(null = True, blank = True)
	
	def __unicode__(self):
		return self.hash or '(Unhashed)'
	
	def send(self):
		try:
			response = requests.post(self.receiver.url,
				data = {
					'_action': self.receiver.hook,
					'_hash': self.hash,
					'data': self.data
				}
			)
		except:
			LOGGER.warn('Unable to send webhook action "%s"' % self.receiver.hook,
				exc_info = {
					'url': self.receiver.url,
					'hash': self.hash
				}
			)
		
		self.receiver.last_called = datetime.now().replace(tzinfo = utc)
		self.receiver.save()
		
		self.delete()