// CompanyJobs.vue.js
const CompanyJobsComponent = {
    template: `
    <div class="page-header"><h1 class="page-title">Job Postings</h1><p class="page-subtitle">Create and manage your placement drives</p></div>
    <div class="d-flex gap-2 mb-4"><button class="btn btn-portal btn-primary-portal" @click="showForm=!showForm"><i :class="showForm?'bi bi-x-lg':'bi bi-plus-lg'"></i> {{showForm?'Cancel':'New Job Posting'}}</button></div>
    <!-- Create Job Form -->
    <div v-if="showForm" class="form-portal fade-in mb-4" style="max-width:750px">
        <h5 class="mb-3" style="font-family:var(--font-heading)">Create Placement Drive</h5>
        <form @submit.prevent="createJob">
            <div class="row">
                <div class="col-md-6 mb-3"><label class="form-label">Job Title *</label><input class="form-control" v-model="jobForm.title" required></div>
                <div class="col-md-3 mb-3"><label class="form-label">Type</label><select class="form-select" v-model="jobForm.job_type"><option value="full-time">Full-time</option><option value="internship">Internship</option><option value="contract">Contract</option></select></div>
                <div class="col-md-3 mb-3"><label class="form-label">Work Mode</label><select class="form-select" v-model="jobForm.work_mode"><option value="on-site">On-site</option><option value="remote">Remote</option><option value="hybrid">Hybrid</option></select></div>
            </div>
            <div class="mb-3"><label class="form-label">Description *</label><textarea class="form-control" v-model="jobForm.description" rows="3" required></textarea></div>
            <div class="row">
                <div class="col-md-4 mb-3"><label class="form-label">Min Salary (₹)</label><input type="number" class="form-control" v-model="jobForm.salary_min"></div>
                <div class="col-md-4 mb-3"><label class="form-label">Max Salary (₹)</label><input type="number" class="form-control" v-model="jobForm.salary_max"></div>
                <div class="col-md-4 mb-3"><label class="form-label">Openings</label><input type="number" min="1" class="form-control" v-model="jobForm.openings"></div>
            </div>
            <div class="row">
                <div class="col-md-4 mb-3"><label class="form-label">Skills Required</label><input class="form-control" v-model="jobForm.skills_required" placeholder="e.g. Python, React"></div>
                <div class="col-md-4 mb-3"><label class="form-label">Experience</label><input class="form-control" v-model="jobForm.experience_required" placeholder="e.g. 0-1 years"></div>
                <div class="col-md-4 mb-3"><label class="form-label">Location</label><input class="form-control" v-model="jobForm.location"></div>
            </div>
            <div class="row">
                <div class="col-md-3 mb-3"><label class="form-label">Min CGPA</label><input type="number" step="0.1" min="0" max="10" class="form-control" v-model="jobForm.min_cgpa"></div>
                <div class="col-md-3 mb-3"><label class="form-label">Branch</label><input class="form-control" v-model="jobForm.eligibility_branch" placeholder="e.g. CSE,ECE"></div>
                <div class="col-md-3 mb-3"><label class="form-label">Grad Year</label><input type="number" class="form-control" v-model="jobForm.eligibility_year"></div>
                <div class="col-md-3 mb-3"><label class="form-label">Deadline *</label><input type="date" class="form-control" v-model="jobForm.application_deadline" required></div>
            </div>
            <div class="mb-3"><label class="form-label">Benefits</label><textarea class="form-control" v-model="jobForm.benefits" rows="2" placeholder="e.g. Health insurance, stock options..."></textarea></div>
            <button type="submit" class="btn btn-portal btn-success-portal" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm"></span> Create Job Posting</button>
        </form>
    </div>
    <!-- Jobs List -->
    <div v-if="loading" class="portal-spinner"><div class="spinner"></div></div>
    <div v-else-if="jobs.length===0&&!showForm" class="empty-state"><i class="bi bi-briefcase"></i><h5>No job postings yet</h5><p style="color:var(--text-muted)">Create your first placement drive</p></div>
    <div v-else class="row g-3">
        <div class="col-md-6 col-xl-4" v-for="j in jobs" :key="j.id">
            <div class="job-card fade-in">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div><div class="job-title" v-text="j.title"></div><div class="job-company" v-text="j.job_type+' • '+(j.work_mode||'on-site')"></div></div>
                    <span class="badge-status" :class="'badge-'+j.status" v-text="j.status"></span>
                </div>
                <div class="job-meta"><span><i class="bi bi-geo-alt"></i> {{j.location||'—'}}</span><span><i class="bi bi-people"></i> {{j.total_applications||0}} apps</span><span><i class="bi bi-calendar"></i> {{formatDate(j.application_deadline)}}</span></div>
                <div class="job-tags" v-if="j.skills_required"><span class="job-tag" v-for="s in j.skills_required.split(',').slice(0,4)" :key="s" v-text="s.trim()"></span></div>
                <div class="d-flex gap-2 mt-3">
                    <button v-if="j.status==='approved'" class="btn btn-sm btn-outline-portal btn-portal" style="font-size:0.78rem" @click="$root.navigate('manage-apps')"><i class="bi bi-eye"></i> View Apps</button>
                    <button v-if="j.status!=='closed'" class="btn btn-sm btn-portal" style="font-size:0.78rem;background:rgba(239,71,111,0.08);color:var(--danger)" @click="closeJob(j.id)"><i class="bi bi-lock"></i> Close</button>
                </div>
            </div>
        </div>
    </div>`,
    data() { return { jobs: [], showForm: false, loading: true, saving: false, jobForm: { title: '', description: '', job_type: 'full-time', work_mode: 'on-site', salary_min: '', salary_max: '', openings: 1, skills_required: '', experience_required: '', location: '', min_cgpa: '', eligibility_branch: '', eligibility_year: '', application_deadline: '', benefits: '' } } },
    methods: {
        formatDate(d) { if (!d) return '—'; return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) },
        async fetchData() { this.loading = true; try { const d = await this.$root.apiCall('/api/company/jobs'); this.jobs = d.jobs } catch (e) { this.$root.showToast(e.message, 'danger') } this.loading = false },
        async createJob() { this.saving = true; try { await this.$root.apiCall('/api/company/jobs', { method: 'POST', body: JSON.stringify(this.jobForm) }); this.$root.showToast('Job posted! Awaiting admin approval.', 'success'); this.showForm = false; this.resetForm(); this.fetchData() } catch (e) { this.$root.showToast(e.message, 'danger') } this.saving = false },
        async closeJob(id) { if (!confirm('Close this job posting?')) return; try { await this.$root.apiCall(`/api/company/jobs/${id}/close`, { method: 'PUT' }); this.$root.showToast('Job closed', 'info'); this.fetchData() } catch (e) { this.$root.showToast(e.message, 'danger') } },
        resetForm() { this.jobForm = { title: '', description: '', job_type: 'full-time', work_mode: 'on-site', salary_min: '', salary_max: '', openings: 1, skills_required: '', experience_required: '', location: '', min_cgpa: '', eligibility_branch: '', eligibility_year: '', application_deadline: '', benefits: '' } }
    },
    mounted() { this.fetchData() }
};
