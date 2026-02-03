# echolabs - Project Notes

## Project Overview

echolabs is a conversation improvement platform (similar to Bee or Plaud Notepin). Users wear a device with a microphone, and use a web app to view conversation transcripts and feedback on how to improve their speech—reducing filler words, improving confidence and tone, and (later) understanding how the other person receives their message.

---

## Naming Decisions

### Project Name: `echolabs_project`
- **echolabs** reflects the core idea: capturing the "echo" of your conversations and analyzing them in a lab-like environment for improvement.
- The `_project` suffix follows Django convention for the top-level configuration package that holds settings, URLs, and WSGI/ASGI config.

### App Name: `conversations`
- The core domain is **conversations**—each recording session is a conversation, and the transcripts and improvement notes are tied to conversations.
- This app will hold all models related to conversations, transcript segments, and improvement feedback.
- Keeps the structure clear and expandable (e.g., a future `users` or `devices` app could be added).

---

## Model Design & Justifications

### Conversation
- **Purpose**: Represents a single recorded conversation/session from the wearable device.
- **Relationships**: `user` → ForeignKey to Django's User model (on_delete=CASCADE).
- **on_delete=CASCADE**: When a user is deleted, their conversations are removed. This protects privacy and avoids orphaned data.

### TranscriptSegment
- **Purpose**: A single utterance/phrase within a conversation. Segments are ordered sequentially.
- **Relationships**: `conversation` → ForeignKey to Conversation (on_delete=CASCADE).
- **on_delete=CASCADE**: Deleting a conversation should remove all its transcript segments; they have no meaning without the parent.
- **UniqueConstraint**: `(conversation, segment_order)` ensures each segment has a unique order within a conversation—no duplicate segment numbers.

### ImprovementNote
- **Purpose**: Feedback or improvement suggestion for a transcript segment (filler words, confidence, tone).
- **Relationships**: `segment` → ForeignKey to TranscriptSegment (on_delete=CASCADE).
- **on_delete=CASCADE**: If a segment is deleted, its improvement notes go with it.

### References
- [Django Model Field Reference](https://docs.djangoproject.com/en/5.2/ref/models/fields/)

---

## Directory Structure

```
echolabs/
├── echolabs_project/     # Django project configuration
├── conversations/        # Core app: conversations, transcripts, feedback
├── manage.py
├── db.sqlite3
├── NOTES.md
├── er_diagram.png
└── er_diagram.dot        # DOT format (alternative)
```
