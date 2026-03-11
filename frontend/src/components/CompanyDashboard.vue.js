// CompanyDashboard.vue.js
const CompanyDashboardComponent = {
    template: `
    <div class="page-header"><h1 class="page-title">Company Dashboard</h1><p class="page-subtitle">Your recruitment activity overview</p></div>
    <div v-if="loading" class="portal-spinner"><div class="spinner"></div></div>
    <div v-else-if="company&&company.approval_status==='pending'" class="fade-in" style="padding-top:40px">
        <div class="text-center"><div style="width:80px;height:80px;border-radius:50%;background:rgba(255,209,102,0.12);display:flex;align-items:center;justify-content:center;margin:0 auto 20px"><i class="bi bi-hourglass-split" style="font-size:2rem;color:var(--warning)"></i></div>
        <h3 style="font-family:var(--font-heading)">Approval Pending</h3><p style="color:var(--text-muted);max-width:480px;margin:12px auto">Your company registration is under review. You will be able to access all features once approved by the admin.</p></div>
    </div>
    <div v-else-if="company&&company.approval_status==='rejected'" class="fade-in" style="padding-top:40px">
        <div class="text-center"><div style="width:80px;height:80px;border-radius:50%;background:rgba(239,71,111,0.12);display:flex;align-items:center;justify-content:center;margin:0 auto 20px"><i class="bi bi-x-circle" style="font-size:2rem;color:var(--danger)"></i></div>
        <h3 style="font-family:var(--font-heading)">Registration Rejected</h3><p style="color:var(--text-muted);max-width:480px;margin:12px auto">Your company registration has been rejected. Please contact the admin for more information.</p></div>
    </div>
    <div v-else>
        <div class="row g-3 mb-4">
            <div class="col-6 col-lg-3" v-for="s in statCards" :key="s.label">
                <div class="stat-card fade-in"><div class="stat-icon" :class="s.color"><i :class="s.icon"></i></div><div class="stat-value" v-text="s.value"></div><div class="stat-label" v-text="s.label"></div></div>
            </div>
        </div>
        <div class="portal-card fade-in">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 style="font-family:var(--font-heading);margin:0">Quick Actions</h5>
            </div>
            <div class="d-flex flex-wrap gap-2">
                <button class="btn btn-portal btn-primary-portal" @click="$root.navigate('my-jobs')"><i class="bi bi-plus-lg"></i> Post New Job</button>
                <button class="btn btn-portal btn-outline-portal" @click="$root.navigate('manage-apps')"><i class="bi bi-people"></i> View Applications</button>
                <button class="btn btn-portal btn-outline-portal" @click="$root.navigate('profile')"><i class="bi bi-pencil"></i> Edit Profile</button>
            </div>
        </div>
    </div>`,
    data() { return { loading: true, company: null, stats: {} } },
    computed: {
        statCards() {
            const s = this.stats; return [
                { label: 'Total Jobs', value: s.total_jobs || 0, icon: 'bi bi-briefcase-fill', color: 'primary' },
                { label: 'Active Jobs', value: s.active_jobs || 0, icon: 'bi bi-lightning-fill', color: 'success' },
                { label: 'Applications', value: s.total_applications || 0, icon: 'bi bi-file-text-fill', color: 'warning' },
                { label: 'Selected', value: s.selected || 0, icon: 'bi bi-trophy-fill', color: 'info' },
            ]
        }
    },
    methods: {
        async fetchData() { this.loading = true; try { const d = await this.$root.apiCall('/api/company/dashboard'); this.company = d.company; this.stats = d.stats } catch (e) { this.$root.showToast(e.message, 'danger') } this.loading = false }
    },
    mounted() { this.fetchData() }
};
