// StudentJobs.vue.js
const StudentJobsComponent = {
    template: `
    <div class="page-header"><h1 class="page-title">Browse Jobs</h1><p class="page-subtitle">Find and apply for placement drives</p></div>
    <div class="d-flex flex-wrap gap-2 mb-4 align-items-center">
        <div class="search-box" style="flex:1;min-width:200px;max-width:400px"><i class="bi bi-search search-icon"></i><input v-model="search" @input="debounceSearch" placeholder="Search by title, company, skills..."></div>
        <div class="form-check form-switch d-flex align-items-center gap-2" style="padding-left:0">
            <input class="form-check-input" type="checkbox" v-model="eligibleOnly" @change="fetchData()" id="eligCheck" style="width:40px;height:20px;background-color:var(--bg-input);border-color:var(--border-light)">
            <label class="form-check-label" for="eligCheck" style="font-size:0.85rem;color:var(--text-secondary)">Eligible only</label>
        </div>
    </div>
    <!-- Job Detail Modal -->
    <div v-if="selectedJob" class="portal-card fade-in mb-4" style="border-color:var(--primary)">
        <div class="d-flex justify-content-between align-items-start mb-3">
            <div><h4 style="font-family:var(--font-heading);margin-bottom:4px" v-text="selectedJob.title"></h4><p style="color:var(--text-muted);margin:0" v-text="selectedJob.company?.name+' • '+selectedJob.location"></p></div>
            <button class="btn-ghost" @click="selectedJob=null"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="row mb-3">
            <div class="col-6 col-md-3 mb-2"><small style="color:var(--text-muted)">Type</small><div style="font-weight:600" v-text="selectedJob.job_type"></div></div>
            <div class="col-6 col-md-3 mb-2"><small style="color:var(--text-muted)">Salary</small><div style="font-weight:600" v-text="selectedJob.salary_min||selectedJob.salary_max?'₹'+(selectedJob.salary_min||0)+' - ₹'+(selectedJob.salary_max||0):'Not disclosed'"></div></div>
            <div class="col-6 col-md-3 mb-2"><small style="color:var(--text-muted)">Deadline</small><div style="font-weight:600" v-text="formatDate(selectedJob.application_deadline)"></div></div>
            <div class="col-6 col-md-3 mb-2"><small style="color:var(--text-muted)">Openings</small><div style="font-weight:600" v-text="selectedJob.openings||'—'"></div></div>
        </div>
        <div class="mb-3"><h6 style="color:var(--text-secondary)">Description</h6><p style="color:var(--text-secondary);white-space:pre-wrap;font-size:0.9rem" v-text="selectedJob.description"></p></div>
        <div v-if="selectedJob.skills_required" class="mb-3"><h6 style="color:var(--text-secondary)">Skills</h6><div class="d-flex flex-wrap gap-1"><span class="job-tag" v-for="s in selectedJob.skills_required.split(',')" :key="s" v-text="s.trim()"></span></div></div>
        <div v-if="selectedJob.benefits" class="mb-3"><h6 style="color:var(--text-secondary)">Benefits</h6><p style="color:var(--text-secondary);font-size:0.9rem" v-text="selectedJob.benefits"></p></div>
        <div v-if="selectedJob.min_cgpa" class="mb-3"><small style="color:var(--text-muted)">Min CGPA: {{selectedJob.min_cgpa}} | Branch: {{selectedJob.eligibility_branch||'All'}}</small></div>
        <div v-if="selectedJob.has_applied" class="alert-portal info"><i class="bi bi-check-circle"></i> You have already applied for this position</div>
        <div v-else-if="!selectedJob.is_eligible" class="alert-portal warning"><i class="bi bi-exclamation-circle"></i> You do not meet the eligibility criteria</div>
        <div v-else>
            <div class="mb-3"><label class="form-label" style="color:var(--text-secondary)">Cover Letter (optional)</label><textarea class="form-control" v-model="coverLetter" rows="3" placeholder="Why are you interested in this role?" style="background:var(--bg-input);border-color:var(--border-color);color:var(--text-primary)"></textarea></div>
            <button class="btn btn-portal btn-success-portal" @click="apply(selectedJob.id)" :disabled="applying"><i class="bi bi-send"></i> {{applying?'Applying...':'Apply Now'}}</button>
        </div>
    </div>
    <!-- Jobs Grid -->
    <div v-if="loading" class="portal-spinner"><div class="spinner"></div></div>
    <div v-else-if="jobs.length===0" class="empty-state"><i class="bi bi-briefcase"></i><h5>No jobs found</h5><p style="color:var(--text-muted)">Try adjusting your search filters</p></div>
    <div v-else class="row g-3">
        <div class="col-md-6 col-xl-4" v-for="j in jobs" :key="j.id">
            <div class="job-card" :style="j.has_applied?'border-color:var(--success);opacity:0.85':''" @click="selectJob(j)">
                <div class="d-flex gap-3 align-items-start">
                    <div class="job-company-logo" v-text="j.company?.name?j.company.name[0].toUpperCase():'?'"></div>
                    <div style="flex:1;min-width:0">
                        <div class="job-title" v-text="j.title"></div>
                        <div class="job-company" v-text="j.company?.name||'—'"></div>
                    </div>
                    <span v-if="j.has_applied" class="badge-status badge-applied">Applied</span>
                    <span v-else-if="!j.is_eligible" class="badge-status badge-closed">Ineligible</span>
                </div>
                <div class="job-meta"><span><i class="bi bi-geo-alt"></i> {{j.location||'Remote'}}</span><span><i class="bi bi-currency-rupee"></i> {{j.salary_max?'₹'+Number(j.salary_max).toLocaleString():'—'}}</span><span><i class="bi bi-calendar"></i> {{formatDate(j.application_deadline)}}</span><span><i class="bi bi-briefcase"></i> {{j.job_type}}</span></div>
                <div class="job-tags" v-if="j.skills_required"><span class="job-tag" v-for="s in j.skills_required.split(',').slice(0,3)" :key="s" v-text="s.trim()"></span></div>
            </div>
        </div>
    </div>
    <div v-if="totalPages>1" class="portal-pagination"><button :disabled="page<=1" @click="page--;fetchData()">‹ Prev</button><span style="color:var(--text-muted);padding:8px">Page {{page}} of {{totalPages}}</span><button :disabled="page>=totalPages" @click="page++;fetchData()">Next ›</button></div>`,
    data() { return { jobs: [], search: '', eligibleOnly: false, loading: true, page: 1, totalPages: 1, timer: null, selectedJob: null, coverLetter: '', applying: false } },
    methods: {
        debounceSearch() { clearTimeout(this.timer); this.timer = setTimeout(() => { this.page = 1; this.fetchData() }, 400) },
        formatDate(d) { if (!d) return '—'; return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) },
        async fetchData() { this.loading = true; try { const q = new URLSearchParams({ search: this.search, eligible_only: this.eligibleOnly, page: this.page, per_page: 12 }); const d = await this.$root.apiCall(`/api/student/jobs?${q}`); this.jobs = d.jobs; this.totalPages = d.pages || 1 } catch (e) { this.$root.showToast(e.message, 'danger') } this.loading = false },
        async selectJob(j) { try { const d = await this.$root.apiCall(`/api/student/jobs/${j.id}`); this.selectedJob = d.job; this.coverLetter = '' } catch (e) { this.$root.showToast(e.message, 'danger') } },
        async apply(jobId) { this.applying = true; try { await this.$root.apiCall(`/api/student/jobs/${jobId}/apply`, { method: 'POST', body: JSON.stringify({ cover_letter: this.coverLetter }) }); this.$root.showToast('Application submitted!', 'success'); this.selectedJob = null; this.fetchData() } catch (e) { this.$root.showToast(e.message, 'danger') } this.applying = false }
    },
    mounted() { this.fetchData() }
};
