from flask import jsonify, request


def generate_Routes(app, db, Tickets, Notes):
    ticket_status_enum = Tickets.__table__.columns.ticket_status.type.enum_class
    ticket_priority_enum = Tickets.__table__.columns.ticket_priority.type.enum_class

    def enum_from_value(enum_class, value, field_name):
        try:
            return enum_class(value)
        except ValueError:
            valid_values = [member.value for member in enum_class]
            raise ValueError(f"{field_name} must be one of: {', '.join(valid_values)}")

    @app.route("/api/tickets", methods=["GET"])
    def get_tickets():
        tickets = Tickets.query.all()
        print("Printing Tickets:", tickets)
        return jsonify([t.to_dict() for t in tickets]), 200

    @app.route("/api/tickets", methods=["POST"])
    def create_ticket():
        data = request.get_json() or {}
        require_fields = ["customer_name", "customer_email", "ticket_status", "ticket_priority", "ticket_subject", "issue_description"]
        for field in require_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        if not data:
            return jsonify({"error": "No data provided"}), 400
        try:
            ticket = Tickets(
                customer_name=data["customer_name"],
                customer_email=data["customer_email"],
                ticket_status=enum_from_value(ticket_status_enum, data["ticket_status"], "ticket_status"),
                ticket_priority=enum_from_value(ticket_priority_enum, data["ticket_priority"], "ticket_priority"),
                ticket_subject=data["ticket_subject"],
                issue_description=data["issue_description"],
            )
        except (KeyError, ValueError) as error:
            return jsonify({"error": str(error)}), 400
        db.session.add(ticket)
        db.session.commit()
        return jsonify(ticket.to_dict()), 201


    @app.route("/api/tickets/<string:ticket_id>", methods=["GET"])
    def get_ticket(ticket_id):
        ticket = Tickets.query.filter_by(ticket_id=ticket_id).first_or_404()
        return jsonify(ticket.to_dict())


    @app.route("/api/tickets/<string:ticket_id>", methods=["PUT"])
    def update_ticket(ticket_id):
        ticket = Tickets.query.filter_by(ticket_id=ticket_id).first_or_404()
        data = request.get_json() or {}
        if not data:
            return jsonify({"error": "No data provided"}), 400
        try:
            if "ticket_status" in data:
                ticket.ticket_status = enum_from_value(ticket_status_enum, data["ticket_status"], "ticket_status")
            if "ticket_priority" in data:
                ticket.ticket_priority = enum_from_value(ticket_priority_enum, data["ticket_priority"], "ticket_priority")
            if "ticket_description" in data:
                ticket.issue_description = data["ticket_description"]
        except ValueError as error:
            return jsonify({"error": str(error)}), 400
        db.session.commit()
        return jsonify(ticket.to_dict())


    @app.route("/api/tickets/<string:ticket_id>", methods=["DELETE"])
    def delete_ticket(ticket_id):
        ticket = Tickets.query.filter_by(ticket_id=ticket_id).first_or_404()
        db.session.delete(ticket)
        db.session.commit()
        return jsonify({"message": f"Ticket {ticket_id} deleted"}), 200

    @app.route("/api/notes/<int:note_id>", methods=["GET"])
    def get_note(note_id):
        note = Notes.query.get_or_404(note_id)
        return jsonify(note.to_dict())
        # db.session.commit()
        # return jsonify(user.to_dict()), 201

    @app.route("/api/notes/<string:ticket_id>", methods=["POST"])
    def create_note(ticket_id):
        data = request.get_json() or {}
        require_fields = ["note_content"]
        for field in require_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        if not data:
            return jsonify({"error": "No data provided"}), 400
        note = Notes(ticket_id=ticket_id, note_content=data["note_content"])
        db.session.add(note)
        db.session.commit()
        return jsonify(note.to_dict()), 201

    @app.route("/api/notes", methods=["GET"])
    def get_notes():
        notes = Notes.query.all()
        return jsonify([n.to_dict() for n in notes])
        # return jsonify(user.to_dict())

    @app.route("/api/notes/<int:note_id>", methods=["DELETE"])
    def delete_note(note_id):
        note = Notes.query.get_or_404(note_id)
        db.session.delete(note)
        db.session.commit()
        return jsonify({"message": f"Note {note_id} deleted"}), 200