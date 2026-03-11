// AdminApplications.vue.js
const AdminApplicationsComponent = {
    template: `
    <div class="page-header"><h1 class="page-title">All Applications</h1><p class="page-subtitle">View all student applications across placement drives</p></div>
    <div class="d-flex flex-wrap gap-2 mb-4">
        <div class="portal-tabs mb-0" style="border:none">
            <button v-for="s in ['','applied','shortlisted','interview','selected','rejected']" :key="s" :class="{active:sf===s}" @click="sf=s;fetchData()" v-text="s||'All'" style="text-transform:capitalize"></button>
        </div>
    </div>
    <div v-if="loading" class="portal-spinner"><div class="spinner"></div></div>
    <div v-else-if="apps.length===0" class="empty-state"><i class="bi bi-file-text"></i><h5>No applications found</h5></div>
    <div v-else class="portal-table fade-in"><table class="table mb-0"><thead><tr><th>Student</th><th>Position</th><th>Company</th><th>Applied</th><th>Interview</th><th>Status</th></tr></thead><tbody>
        <tr v-for="a in apps" :key="a.id">
            <td><div style="font-weight:600;font-size:0.88rem" v-text="a.student?.name||'—'"></div><div style="font-size:0.75rem;color:var(--text-muted)" v-text="a.student?.branch||''"></div></td>
            <td v-text="a.job?.title||'—'"></td>
            <td v-text="a.job?.company?.name||'—'"></td>
            <td style="font-size:0.82rem" v-text="formatDate(a.application_date)"></td>
            <td style="font-size:0.82rem" v-text="a.interview_date?formatDate(a.interview_date):'—'"></td>
            <td><span class="badge-status" :class="'badge-'+a.status" v-text="a.status"></span></td>
        </tr>
    </tbody></table></div>`,
    data() { return { apps: [], sf: '', loading: true } },
    methods: {
        formatDate(d) { if (!d) return '—'; return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) },
        async fetchData() { this.loading = true; try { const q = new URLSearchParams({ status: this.sf, per_page: 50 }); const d = await this.$root.apiCall(`/api/admin/applications?${q}`); this.apps = d.applications } catch (e) { this.$root.showToast(e.message, 'danger') } this.loading = false }
    },
    mounted() { this.fetchData() }
};
