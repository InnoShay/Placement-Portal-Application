// AdminPlacements.vue.js
const AdminPlacementsComponent = {
    template: `
    <div class="page-header"><h1 class="page-title">Placements</h1><p class="page-subtitle">All confirmed placements</p></div>
    <div v-if="loading" class="portal-spinner"><div class="spinner"></div></div>
    <div v-else-if="placements.length===0" class="empty-state"><i class="bi bi-trophy"></i><h5>No placements yet</h5></div>
    <div v-else class="portal-table fade-in"><table class="table mb-0"><thead><tr><th>Student</th><th>Company</th><th>Position</th><th>Salary</th><th>Joining Date</th><th>Status</th></tr></thead><tbody>
        <tr v-for="p in placements" :key="p.id">
            <td style="font-weight:600" v-text="p.student_name||'—'"></td>
            <td v-text="p.company_name||'—'"></td>
            <td v-text="p.position||'—'"></td>
            <td v-text="p.salary?'₹'+Number(p.salary).toLocaleString():'—'"></td>
            <td style="font-size:0.85rem" v-text="p.joining_date||'—'"></td>
            <td><span class="badge-status badge-selected" v-text="p.status||'confirmed'"></span></td>
        </tr>
    </tbody></table></div>`,
    data() { return { placements: [], loading: true } },
    methods: {
        async fetchData() { this.loading = true; try { const d = await this.$root.apiCall('/api/admin/placements'); this.placements = d.placements } catch (e) { this.$root.showToast(e.message, 'danger') } this.loading = false }
    },
    mounted() { this.fetchData() }
};
