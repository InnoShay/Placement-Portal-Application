// StudentApplications.vue.js
const StudentApplicationsComponent = {
    template: `
    <div class="page-header"><h1 class="page-title">My Applications</h1><p class="page-subtitle">Track your placement application status</p></div>
    <div class="portal-tabs mb-4">
        <button v-for="s in ['','applied','shortlisted','interview','selected','rejected']" :key="s" :class="{active:sf===s}" @click="sf=s;fetchData()" v-text="s||'All'" style="text-transform:capitalize"></button>
    </div>
    <div v-if="loading" class="portal-spinner"><div class="spinner"></div></div>
    <div v-else-if="apps.length===0" class="empty-state"><i class="bi bi-file-text"></i><h5>No applications found</h5><p style="color:var(--text-muted)">Apply for placement drives to see them here</p></div>
    <div v-else class="row g-3">
        <div class="col-12" v-for="a in apps" :key="a.id">
            <div class="portal-card fade-in">
                <div class="d-flex flex-wrap gap-3 align-items-center">
                    <div class="sidebar-avatar" v-text="a.job?.company?.name?a.job.company.name[0].toUpperCase():'?'" style="width:44px;height:44px"></div>
                    <div style="flex:1;min-width:200px">
                        <div style="font-weight:700;font-size:1rem;font-family:var(--font-heading)" v-text="a.job?.title||'—'"></div>
                        <div style="color:var(--text-muted);font-size:0.85rem">{{a.job?.company?.name||'—'}} • {{a.job?.location||'—'}}</div>
                    </div>
                    <span class="badge-status" :class="'badge-'+a.status" v-text="a.status"></span>
                    <div style="text-align:right;min-width:120px">
                        <div style="font-size:0.78rem;color:var(--text-muted)">Applied</div>
                        <div style="font-size:0.85rem" v-text="formatDate(a.application_date)"></div>
                    </div>
                </div>
                <div v-if="a.status==='interview'&&a.interview_date" class="mt-3 p-3" style="background:var(--bg-surface);border-radius:var(--radius-md)">
                    <div class="d-flex align-items-center gap-2"><i class="bi bi-camera-video" style="color:var(--secondary)"></i><strong style="font-size:0.9rem">Interview</strong></div>
                    <div style="font-size:0.85rem;color:var(--text-secondary);margin-top:4px">Date: {{formatDate(a.interview_date)}} {{a.interview_time||''}}</div>
                    <div v-if="a.interview_link" style="font-size:0.85rem;margin-top:2px"><a :href="a.interview_link" target="_blank" style="color:var(--primary-light)">Join Meeting →</a></div>
                    <div v-if="a.interview_location" style="font-size:0.85rem;color:var(--text-muted);margin-top:2px"><i class="bi bi-geo-alt"></i> {{a.interview_location}}</div>
                </div>
                <div v-if="a.feedback" class="mt-3 p-3" style="background:var(--bg-surface);border-radius:var(--radius-md)">
                    <div style="font-size:0.78rem;color:var(--text-muted);margin-bottom:2px">Feedback</div>
                    <div style="font-size:0.88rem;color:var(--text-secondary)" v-text="a.feedback"></div>
                </div>
            </div>
        </div>
    </div>`,
    data() { return { apps: [], sf: '', loading: true } },
    methods: {
        formatDate(d) { if (!d) return '—'; return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) },
        async fetchData() { this.loading = true; try { const q = this.sf ? `?status=${this.sf}` : ''; const d = await this.$root.apiCall(`/api/student/applications${q}`); this.apps = d.applications } catch (e) { this.$root.showToast(e.message, 'danger') } this.loading = false }
    },
    mounted() { this.fetchData() }
};
