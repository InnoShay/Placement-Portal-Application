// CompanyApplications.vue.js
const CompanyApplicationsComponent = {
    template: `
    <div class="page-header"><h1 class="page-title">Manage Applications</h1><p class="page-subtitle">Review and manage student applications for your postings</p></div>
    <div v-if="!selectedJob" class="fade-in">
        <p style="color:var(--text-muted)" class="mb-3">Select a job posting to view its applications:</p>
        <div v-if="loadingJobs" class="portal-spinner"><div class="spinner"></div></div>
        <div v-else-if="jobs.length===0" class="empty-state"><i class="bi bi-briefcase"></i><h5>No job postings</h5></div>
        <div v-else class="row g-3">
            <div class="col-md-6 col-xl-4" v-for="j in jobs" :key="j.id">
                <div class="job-card" @click="selectJob(j)">
                    <div class="job-title" v-text="j.title"></div>
                    <div class="job-meta mt-2"><span><i class="bi bi-people"></i> {{j.total_applications||0}} applications</span><span class="badge-status" :class="'badge-'+j.status" v-text="j.status"></span></div>
                </div>
            </div>
        </div>
    </div>
    <div v-else class="fade-in">
        <button class="btn btn-portal btn-outline-portal mb-3" @click="selectedJob=null;apps=[]"><i class="bi bi-arrow-left"></i> Back to Jobs</button>
        <h5 class="mb-3" style="font-family:var(--font-heading)">Applications for: {{selectedJob.title}}</h5>
        <div v-if="loadingApps" class="portal-spinner"><div class="spinner"></div></div>
        <div v-else-if="apps.length===0" class="empty-state"><i class="bi bi-inbox"></i><h5>No applications yet</h5></div>
        <div v-else class="portal-table"><table class="table mb-0"><thead><tr><th>Student</th><th>Branch</th><th>CGPA</th><th>Applied</th><th>Status</th><th>Actions</th></tr></thead><tbody>
            <tr v-for="a in apps" :key="a.id">
                <td><div style="font-weight:600" v-text="a.student?.name||'—'"></div><div style="font-size:0.75rem;color:var(--text-muted)" v-text="a.student?.email||''"></div></td>
                <td v-text="a.student?.branch||'—'"></td><td v-text="a.student?.cgpa||'—'"></td>
                <td style="font-size:0.82rem" v-text="formatDate(a.application_date)"></td>
                <td><span class="badge-status" :class="'badge-'+a.status" v-text="a.status"></span></td>
                <td><div class="d-flex gap-1 flex-wrap">
                    <button v-if="a.status==='applied'" class="btn btn-sm btn-success-portal btn-portal" style="padding:4px 10px;font-size:0.75rem" @click="updateStatus(a.id,'shortlisted')">Shortlist</button>
                    <button v-if="a.status==='shortlisted'" class="btn btn-sm btn-portal" style="padding:4px 10px;font-size:0.75rem;background:rgba(114,9,183,0.12);color:var(--secondary)" @click="showInterviewModal(a)">Schedule Interview</button>
                    <button v-if="['shortlisted','interview'].includes(a.status)" class="btn btn-sm btn-success-portal btn-portal" style="padding:4px 10px;font-size:0.75rem" @click="updateStatus(a.id,'selected')">Select</button>
                    <button v-if="a.status!=='rejected'&&a.status!=='selected'" class="btn btn-sm btn-danger-portal btn-portal" style="padding:4px 10px;font-size:0.75rem" @click="updateStatus(a.id,'rejected')">Reject</button>
                </div></td>
            </tr>
        </tbody></table></div>
    </div>
    <!-- Interview Modal -->
    <div class="modal fade" id="interviewModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content">
        <div class="modal-header"><h5 class="modal-title">Schedule Interview</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
        <div class="modal-body">
            <div class="mb-3"><label class="form-label">Date</label><input type="date" class="form-control" v-model="intForm.interview_date" style="background:var(--bg-input);color:var(--text-primary);border-color:var(--border-color)"></div>
            <div class="mb-3"><label class="form-label">Time</label><input type="time" class="form-control" v-model="intForm.interview_time" style="background:var(--bg-input);color:var(--text-primary);border-color:var(--border-color)"></div>
            <div class="mb-3"><label class="form-label">Meeting Link (optional)</label><input class="form-control" v-model="intForm.interview_link" style="background:var(--bg-input);color:var(--text-primary);border-color:var(--border-color)"></div>
            <div class="mb-3"><label class="form-label">Location (optional)</label><input class="form-control" v-model="intForm.interview_location" style="background:var(--bg-input);color:var(--text-primary);border-color:var(--border-color)"></div>
        </div>
        <div class="modal-footer"><button class="btn btn-portal btn-outline-portal" data-bs-dismiss="modal">Cancel</button><button class="btn btn-portal btn-primary-portal" @click="scheduleInterview">Schedule</button></div>
    </div></div></div>`,
    data() { return { jobs: [], apps: [], selectedJob: null, loadingJobs: true, loadingApps: false, intForm: { interview_date: '', interview_time: '', interview_link: '', interview_location: '' }, intAppId: null, modal: null } },
    methods: {
        formatDate(d) { if (!d) return '—'; return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) },
        async fetchJobs() { this.loadingJobs = true; try { const d = await this.$root.apiCall('/api/company/jobs'); this.jobs = d.jobs } catch (e) { this.$root.showToast(e.message, 'danger') } this.loadingJobs = false },
        async selectJob(j) { this.selectedJob = j; this.loadingApps = true; try { const d = await this.$root.apiCall(`/api/company/jobs/${j.id}/applications`); this.apps = d.applications } catch (e) { this.$root.showToast(e.message, 'danger') } this.loadingApps = false },
        async updateStatus(id, status) { try { await this.$root.apiCall(`/api/company/applications/${id}/status`, { method: 'PUT', body: JSON.stringify({ status }) }); this.$root.showToast(`Status updated to ${status}`, 'success'); this.selectJob(this.selectedJob) } catch (e) { this.$root.showToast(e.message, 'danger') } },
        showInterviewModal(a) { this.intAppId = a.id; this.intForm = { interview_date: '', interview_time: '', interview_link: '', interview_location: '' }; if (!this.modal) this.modal = new bootstrap.Modal(document.getElementById('interviewModal')); this.modal.show() },
        async scheduleInterview() { if (!this.intForm.interview_date) { this.$root.showToast('Date is required', 'warning'); return } try { await this.$root.apiCall(`/api/company/applications/${this.intAppId}/interview`, { method: 'PUT', body: JSON.stringify(this.intForm) }); this.$root.showToast('Interview scheduled', 'success'); this.modal.hide(); this.selectJob(this.selectedJob) } catch (e) { this.$root.showToast(e.message, 'danger') } }
    },
    mounted() { this.fetchJobs() }
};
