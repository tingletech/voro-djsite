from django.db import models

class ContactUsMessage(models.Model):
    ISSUE_TYPES = (
        ('SP', 'Search Page'),
        ('BP', 'Browse Page'),
        ('SR', 'Search Results'),
        ('EAD', 'EAD View'),
        ('MARC', 'MARC View'),
        ('METS', 'METS View'),
        ('CF', 'Comments Feature'),
        ('SP', 'Static Page'),
        ('AI', 'Admin Interface'),
        ('PDF', 'PDF View'),
        ('X', 'To assign'),
    )
    STATUS = (
        ('N', 'New'),
        ('P', 'In-process'),
        ('W', 'Waiting'),
        ('D', 'Duplicate'),
        ('C', "Completed"),
        ('T', "Move to Trac"),
        ('F', "Move to FootPrints"),
        ('DFR', "Defer"),
        ('B', "Bogus"),
        ('X', "To assign"),
    )
    CATEGORIES = (
        ('D', 'Defect'),
        ('E', 'Enhancement'),
        ('C', 'Data clean up'),
        ('U', 'Design Change'),
        ('X', 'To assign'),
    )
    PRIORITIES = (
        ('B', 'Blocker'),
        ('C', 'Critical'),
        ('G', 'Major'),
        ('P', 'Minor'),
        ('T', 'Trivial'),
        ('S', 'Gravy'),
        ('X', 'To assign'),
    )
    ASSIGNEE_GROUPS = (
        ('U', 'User Experience Design'),
        ('W', 'Web Production'),
        ('P', 'Programming/Developemnt'),
        ('D', 'Data Acqs/Metadata Coordination'),
        ('O', 'Operations'),
        ('X', 'To assign'),
    )
    RELEASES = (
        ('0', 'OAC-L 3.9.3'),
        ('394', '3.94'),
        ('395', '3.95'),
        ('396', '3.96'),
        ('40', '4.0'),
        ('41', '4.1'),
        ('4', '4.XX'),
        ('X', 'Unknown'),
    )
    SOURCES = (
        ('E', 'Existing Record'),
        ('AT', "Archivist's Toolkit"),
        ('X', 'To assign'),
    )

    url_refer = models.URLField(verify_exists=False, max_length=255, blank=True)
    user_agent = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    open = models.BooleanField(default=True)
    type_of_issue = models.CharField(max_length=4, blank=True,
                                     choices=ISSUE_TYPES, default='X')
    status = models.CharField(max_length=4, blank=True,
                              choices=STATUS, default='N')
    duplicate = models.ForeignKey('self', null=True, blank=True,
                                  related_name='duplicates')
    category = models.CharField(max_length=4, blank=True,
                                choices=CATEGORIES, default='X')
    priority = models.CharField(max_length=4, blank=True,
                                choices=PRIORITIES, default='X')
    assigned_group = models.CharField(max_length=4, blank=True,
                                      choices=ASSIGNEE_GROUPS, default='X')
    source = models.CharField(max_length=4, blank=True,
                              choices=SOURCES, default='X')
    release = models.CharField(max_length=4, blank=True,
                              choices=RELEASES, default='X')
    dependencies = models.TextField(blank=True)
    next_steps = models.TextField(blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def message_display(self):
        msg = self.message[0:127]
        if len(self.message) > 128:
            msg += '... (%d more characters)' % (len(self.message) - 128)
        return msg

    def __unicode__(self):
        return self.subject

    class Meta:
        ordering = ['-created_at', '-url_refer']
