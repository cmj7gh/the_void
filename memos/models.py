from django.db import models

class VoiceMemo(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    audio_file = models.FileField(upload_to='voice_memos/')
    transcript = models.TextField(blank=True, null=True)
    summary = models.CharField(max_length=100, blank=True, null=True)
    llm_response = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.summary or f"Memo at {self.created_at}"
