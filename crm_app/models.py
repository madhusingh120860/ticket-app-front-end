from enum import Enum
from uuid import uuid4


def generate_Models(db):
    class TicketStatus(Enum):
        OPEN = "Open"
        IN_PROGRESS = "In Progress"
        RESOLVED = "Resolved"
        CLOSED = "Closed"

    class TicketPriority(Enum):
        LOW = "Low"
        MEDIUM = "Medium"
        HIGH = "High"
        URGENT = "Urgent"

    
    class Tickets(db.Model):
        __tablename__ = "tickets"
        id = db.Column(db.Integer, primary_key=True)
        ticket_id = db.Column(
            db.String(80),
            unique=True,
            nullable=False,
            default=lambda: f"TCK-{uuid4().hex[:12].upper()}",
        )
        customer_name = db.Column(db.String(120), nullable=False)
        customer_email = db.Column(db.String(120), nullable=False)
        ticket_status = db.Column(
            db.Enum(TicketStatus, values_callable=lambda enum: [member.value for member in enum]),
            nullable=False,
        )
        ticket_priority = db.Column(
            db.Enum(TicketPriority, values_callable=lambda enum: [member.value for member in enum]),
            nullable=False,
        )
        ticket_subject = db.Column(db.String(200), nullable=False)

        issue_description = db.Column(db.Text, nullable=False)
        created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
        updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


        def __init__(self, customer_name, customer_email, ticket_status, ticket_priority, ticket_subject, issue_description):
            self.customer_name = customer_name
            self.customer_email = customer_email
            self.ticket_status = ticket_status
            self.ticket_priority = ticket_priority
            self.ticket_subject = ticket_subject
            self.issue_description = issue_description
        
        def to_dict(self):
            return {"id": self.id, "ticket_id": self.ticket_id, "customer_name": self.customer_name, "issue_description": self.issue_description, "customer_email": self.customer_email, "ticket_status": self.ticket_status.value, "ticket_priority": self.ticket_priority.value, "ticket_subject": self.ticket_subject}

    class Notes(db.Model):
        __tablename__ = "notes"
        id = db.Column(db.Integer, primary_key=True)
        ticket_id = db.Column(db.String(80), db.ForeignKey('tickets.ticket_id'), nullable=False)
        note_content = db.Column(db.Text, nullable=False)
        created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
        updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

        def __init__(self, ticket_id, note_content):
            self.ticket_id = ticket_id
            self.note_content = note_content
        
        def to_dict(self):
            return {"id": self.id, "ticket_id": self.ticket_id, "note_content": self.note_content}

    return Tickets, Notes