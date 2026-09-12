<template>
  <div class="shell">
    <header class="topbar">
      <div>
        <p class="kicker">OPERATIONS / SUPPORT</p>
        <h1>Service desk</h1>
      </div>
      <button class="button button-dark" @click="openCreate">New ticket <span>+</span></button>
    </header>

    <main>
      <section class="intro">
        <div>
          <p class="eyebrow">LIVE QUEUE</p>
          <h2>Keep every customer issue moving.</h2>
        </div>
        <p class="intro-copy">A focused view of your open work, recent decisions, and the people waiting for a response.</p>
      </section>

      <section class="metrics">
        <div class="metric"><span>Total tickets</span><strong>{{ tickets.length }}</strong></div>
        <div class="metric"><span>Open</span><strong>{{ countByStatus('Open') }}</strong></div>
        <div class="metric"><span>High priority</span><strong>{{ countHighPriority }}</strong></div>
        <div class="metric"><span>Resolved</span><strong>{{ countByStatus('Resolved') }}</strong></div>
      </section>

      <section class="workspace">
        <div class="queue-panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">TICKETS</p>
              <h3>Current queue</h3>
            </div>
            <select v-model="filterStatus" aria-label="Filter by status">
              <option value="All">All statuses</option>
              <option v-for="status in statuses" :key="status" :value="status">{{ status }}</option>
            </select>
          </div>
          <div v-if="loading" class="empty-state">Loading tickets...</div>
          <div v-else-if="error" class="error-state">{{ error }}</div>
          <div v-else-if="filteredTickets.length === 0" class="empty-state">No tickets match this view.</div>
          <div v-else class="ticket-list">
            <article v-for="ticket in filteredTickets" :key="ticket.ticket_id" class="ticket-row" :class="{ selected: selectedTicket && selectedTicket.ticket_id === ticket.ticket_id }" @click="selectTicket(ticket)">
              <div class="ticket-main">
                <div class="ticket-title-line"><span class="ticket-id">{{ ticket.ticket_id }}</span><span class="priority" :class="priorityClass(ticket.ticket_priority)">{{ ticket.ticket_priority }}</span></div>
                <h4>{{ ticket.ticket_subject }}</h4>
                <p>{{ ticket.customer_name }} · {{ ticket.customer_email }}</p>
              </div>
              <select class="status-select" :value="ticket.ticket_status" @click.stop @change="changeStatus(ticket, $event.target.value)">
                <option v-for="status in statuses" :key="status">{{ status }}</option>
              </select>
            </article>
          </div>
        </div>

        <aside class="detail-panel">
          <div v-if="selectedTicket">
            <div class="detail-top"><span class="eyebrow">TICKET DETAIL</span><button class="icon-button" title="Delete ticket" @click="removeTicket">×</button></div>
            <span class="ticket-id">{{ selectedTicket.ticket_id }}</span>
            <h3>{{ selectedTicket.ticket_subject }}</h3>
            <p class="detail-customer">{{ selectedTicket.customer_name }} · {{ selectedTicket.customer_email }}</p>
            <p class="description">{{ selectedTicket.issue_description }}</p>
            <div class="detail-controls">
              <label>Status<select :value="selectedTicket.ticket_status" @change="changeStatus(selectedTicket, $event.target.value)"><option v-for="status in statuses" :key="status">{{ status }}</option></select></label>
              <label>Priority<select :value="selectedTicket.ticket_priority" @change="changePriority(selectedTicket, $event.target.value)"><option v-for="priority in priorities" :key="priority">{{ priority }}</option></select></label>
            </div>
            <div class="notes">
              <div class="notes-heading"><h4>Notes</h4><span>{{ notes.length }}</span></div>
              <div v-for="note in notes" :key="note.id" class="note">
                <span>{{ note.note_content }}</span>
                <button class="note-delete" type="button" title="Delete note" @click="removeNote(note)">×</button>
              </div>
              <form class="note-form" @submit.prevent="addNote"><input v-model="noteContent" placeholder="Add a note..." required /><button class="button button-small">Add</button></form>
            </div>
          </div>
          <div v-else class="empty-detail"><span class="detail-mark">→</span><h3>Select a ticket</h3><p>Choose an item from the queue to inspect its details and notes.</p></div>
        </aside>
      </section>
    </main>

    <div v-if="showCreate" class="modal-backdrop" @click.self="showCreate = false">
      <form class="modal" @submit.prevent="createTicket">
        <div class="modal-head"><div><p class="eyebrow">NEW REQUEST</p><h3>Create ticket</h3></div><button type="button" class="icon-button" @click="showCreate = false">×</button></div>
        <label>Customer name<input v-model="form.customer_name" required /></label>
        <label>Email<input v-model="form.customer_email" type="email" required /></label>
        <div class="form-grid"><label>Status<select v-model="form.ticket_status"><option v-for="status in statuses" :key="status">{{ status }}</option></select></label><label>Priority<select v-model="form.ticket_priority"><option v-for="priority in priorities" :key="priority">{{ priority }}</option></select></label></div>
        <label>Subject<input v-model="form.ticket_subject" required /></label>
        <label>Issue description<textarea v-model="form.issue_description" rows="4" required></textarea></label>
        <p v-if="formError" class="form-error">{{ formError }}</p><button type="submit" class="button button-dark" :disabled="saving">{{ saving ? 'Submitting...' : 'Submit ticket' }}</button>
      </form>
    </div>
  </div>
</template>

<script>
const blankForm = () => ({ customer_name: '', customer_email: '', ticket_status: 'Open', ticket_priority: 'Medium', ticket_subject: '', issue_description: '' })

export default {
  data: () => ({ tickets: [], notes: [], selectedTicket: null, filterStatus: 'All', statuses: ['Open', 'In Progress', 'Resolved', 'Closed'], priorities: ['Low', 'Medium', 'High', 'Urgent'], loading: true, error: '', showCreate: false, saving: false, formError: '', form: blankForm(), noteContent: '' }),
  computed: {
    filteredTickets () { return this.filterStatus === 'All' ? this.tickets : this.tickets.filter((ticket) => ticket.ticket_status === this.filterStatus) },
    countHighPriority () { return this.tickets.filter((ticket) => ticket.ticket_priority === 'High' || ticket.ticket_priority === 'Urgent').length }
  },
  mounted () { this.loadTickets() },
  methods: {
    async request (url, options = {}) { const response = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...options }); const body = await response.json().catch(() => ({})); if (!response.ok) throw new Error(body.error || `Request failed (${response.status})`); return body },
    async loadTickets () { try { this.tickets = await this.request('/api/tickets'); if (this.tickets.length) await this.selectTicket(this.tickets[0]) } catch (error) { this.error = error.message } finally { this.loading = false } },
    async selectTicket (ticket) { this.selectedTicket = ticket; try { const allNotes = await this.request('/api/notes'); this.notes = allNotes.filter((note) => note.ticket_id === ticket.ticket_id) } catch (error) { this.notes = [] } },
    countByStatus (status) { return this.tickets.filter((ticket) => ticket.ticket_status === status).length },
    priorityClass (priority) { return `priority-${priority.toLowerCase()}` },
    openCreate () { this.form = blankForm(); this.formError = ''; this.showCreate = true },
    async createTicket () { this.saving = true; this.formError = ''; try { const ticket = await this.request('/api/tickets', { method: 'POST', body: JSON.stringify(this.form) }); this.tickets.unshift(ticket); this.showCreate = false; await this.selectTicket(ticket) } catch (error) { this.formError = error.message } finally { this.saving = false } },
    async updateTicket (ticket, changes) { const updated = await this.request(`/api/tickets/${ticket.ticket_id}`, { method: 'PUT', body: JSON.stringify(changes) }); Object.assign(ticket, updated); return updated },
    async changeStatus (ticket, status) { try { await this.updateTicket(ticket, { ticket_status: status }) } catch (error) { this.error = error.message } },
    async changePriority (ticket, priority) { try { const updated = await this.updateTicket(ticket, { ticket_priority: priority }); ticket.ticket_priority = updated.ticket_priority || priority } catch (error) { this.error = error.message } },
    async removeTicket () { if (!window.confirm(`Delete ${this.selectedTicket.ticket_id}?`)) return; try { await this.request(`/api/tickets/${this.selectedTicket.ticket_id}`, { method: 'DELETE' }); this.tickets = this.tickets.filter((ticket) => ticket.ticket_id !== this.selectedTicket.ticket_id); this.selectedTicket = this.tickets[0] || null; this.notes = [] } catch (error) { this.error = error.message } },
    async addNote () { if (!this.noteContent.trim()) return; try { const note = await this.request(`/api/notes/${this.selectedTicket.ticket_id}`, { method: 'POST', body: JSON.stringify({ note_content: this.noteContent }) }); this.notes.push(note); this.noteContent = '' } catch (error) { this.error = error.message } },
    async removeNote (note) { if (!window.confirm('Delete this note?')) return; try { await this.request(`/api/notes/${note.id}`, { method: 'DELETE' }); this.notes = this.notes.filter((item) => item.id !== note.id) } catch (error) { this.error = error.message } }
  }
}
</script>
