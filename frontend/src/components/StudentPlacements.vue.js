// StudentPlacements.vue.js
const StudentPlacementsComponent = {
    template: `
    <div class="page-header"><h1 class="page-title">My Placements</h1><p class="page-subtitle">Your confirmed placement records</p></div>
    <div v-if="loading" class="portal-spinner"><div class="spinner"></div></div>
    <div v-else-if="placements.length===0" class="empty-state"><i class="bi bi-trophy"></i><h5>No placements yet</h5><p style="color:var(--text-muted)">Your confirmed placements will appear here</p></div>
    <div v-else class="row g-3">
        <div class="col-md-6" v-for="p in placements" :key="p.id">
            <div class="portal-card fade-in" style="border-color:var(--success)">
                <div class="d-flex align-items-center gap-3 mb-3">
                    <div style="width:52px;height:52px;border-radius:var(--radius-md);background:rgba(6,214,160,0.12);display:flex;align-items:center;justify-content:center"><i class="bi bi-trophy-fill" style="color:var(--success);font-size:1.4rem"></i></div>
                    <div><div style="font-weight:700;font-size:1.05rem;font-family:var(--font-heading)" v-text="p.position"></div><div style="color:var(--text-muted);font-size:0.85rem" v-text="p.company_name||'—'"></div></div>
                </div>
                <div class="d-flex flex-wrap gap-3">
                    <div><small style="color:var(--text-muted)">Salary</small><div style="font-weight:600;color:var(--success)" v-text="p.salary?'₹'+Number(p.salary).toLocaleString()+'/yr':'Not disclosed'"></div></div>
                    <div><small style="color:var(--text-muted)">Joining Date</small><div style="font-weight:600" v-text="p.joining_date||'TBD'"></div></div>
                    <div><small style="color:var(--text-muted)">Status</small><div><span class="badge-status badge-selected" v-text="p.status||'confirmed'"></span></div></div>
                </div>
            </div>
        </div>
    </div>`,
    data() { return { placements: [], loading: true } },
    methods: { async fetchData() { this.loading = true; try { const d = await this.$root.apiCall('/api/student/placements'); this.placements = d.placements } catch (e) { this.$root.showToast(e.message, 'danger') } this.loading = false } },
    mounted() { this.fetchData() }
};
