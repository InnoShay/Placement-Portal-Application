// AdminDashboard.vue.js
const AdminDashboardComponent = {
    template: `
    <div class="page-header"><h1 class="page-title">Admin Dashboard</h1><p class="page-subtitle">Overview of placement portal activity</p></div>
    <div v-if="loading" class="portal-spinner"><div class="spinner"></div></div>
    <div v-else>
        <div class="row g-3 mb-4">
            <div class="col-6 col-lg-4 col-xl-2" v-for="s in statCards" :key="s.label">
                <div class="stat-card fade-in">
                    <div class="stat-icon" :class="s.color"><i :class="s.icon"></i></div>
                    <div class="stat-value" v-text="s.value"></div>
                    <div class="stat-label" v-text="s.label"></div>
                </div>
            </div>
        </div>
        <div class="row g-4">
            <div class="col-lg-7">
                <div class="portal-card fade-in">
                    <h5 class="mb-3" style="font-family:var(--font-heading)">Recent Applications</h5>
                    <div v-if="recentApps.length===0" class="empty-state"><i class="bi bi-inbox"></i><h5>No applications yet</h5></div>
                    <div class="portal-table" v-else><table class="table mb-0"><thead><tr><th>Student</th><th>Position</th><th>Company</th><th>Status</th><th>Date</th></tr></thead><tbody>
                        <tr v-for="a in recentApps" :key="a.id">
                            <td v-text="a.student?.name||'—'"></td>
                            <td v-text="a.job?.title||'—'"></td>
                            <td v-text="a.job?.company?.name||'—'"></td>
                            <td><span class="badge-status" :class="'badge-'+a.status" v-text="a.status"></span></td>
                            <td style="color:var(--text-muted);font-size:0.82rem" v-text="formatDate(a.application_date)"></td>
                        </tr>
                    </tbody></table></div>
                </div>
            </div>
            <div class="col-lg-5">
                <div class="portal-card fade-in">
                    <h5 class="mb-3" style="font-family:var(--font-heading)">Recent Companies</h5>
                    <div v-for="c in recentCompanies" :key="c.id" class="d-flex align-items-center gap-3 mb-3 p-2" style="border-radius:var(--radius-md)">
                        <div class="sidebar-avatar" v-text="c.name?c.name[0].toUpperCase():'C'" style="width:40px;height:40px;font-size:0.9rem"></div>
                        <div style="flex:1;min-width:0"><div style="font-weight:600;font-size:0.9rem" v-text="c.name" class="truncate"></div><div style="font-size:0.78rem;color:var(--text-muted)" v-text="c.industry||'—'"></div></div>
                        <span class="badge-status" :class="'badge-'+c.approval_status" v-text="c.approval_status"></span>
                    </div>
                    <div v-if="recentCompanies.length===0" class="empty-state py-4"><i class="bi bi-buildings"></i><p>No companies yet</p></div>
                </div>
            </div>
        </div>
    </div>`,
    data() { return { loading: true, stats: {}, recentApps: [], recentCompanies: [] } },
    computed: {
        statCards() {
            const s = this.stats; return [
                { label: 'Students', value: s.total_students || 0, icon: 'bi bi-people-fill', color: 'primary' },
                { label: 'Companies', value: s.total_companies || 0, icon: 'bi bi-buildings', color: 'info' },
                { label: 'Drives', value: s.total_jobs || 0, icon: 'bi bi-briefcase-fill', color: 'accent' },
                { label: 'Applications', value: s.total_applications || 0, icon: 'bi bi-file-text-fill', color: 'warning' },
                { label: 'Pending', value: (s.pending_companies || 0) + (s.pending_drives || 0), icon: 'bi bi-clock-fill', color: 'danger' },
                { label: 'Placed', value: s.total_placements || 0, icon: 'bi bi-trophy-fill', color: 'success' },
            ]
        }
    },
    methods: {
        formatDate(d) { if (!d) return '—'; return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) },
        async fetchData() {
            this.loading = true;
            try {
                const data = await this.$root.apiCall('/api/admin/dashboard');
                this.stats = data.stats; this.recentApps = data.recent_applications || []; this.recentCompanies = data.recent_companies || [];
            } catch (e) { this.$root.showToast(e.message, 'danger') }
            this.loading = false;
        }
    },
    mounted() { this.fetchData() }
};
