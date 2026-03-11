// AdminDrives.vue.js
const AdminDrivesComponent = {
    template: `
    <div class="page-header"><h1 class="page-title">Placement Drives</h1><p class="page-subtitle">Approve and manage placement drives</p></div>
    <div class="d-flex flex-wrap gap-2 mb-4">
        <div class="search-box" style="flex:1;max-width:400px"><i class="bi bi-search search-icon"></i><input v-model="search" @input="debounceSearch" placeholder="Search drives..."></div>
        <div class="portal-tabs mb-0" style="border:none">
            <button :class="{active:sf===''}" @click="sf='';fetchData()">All</button>
            <button :class="{active:sf==='pending'}" @click="sf='pending';fetchData()">Pending</button>
            <button :class="{active:sf==='approved'}" @click="sf='approved';fetchData()">Approved</button>
            <button :class="{active:sf==='closed'}" @click="sf='closed';fetchData()">Closed</button>
        </div>
    </div>
    <div v-if="loading" class="portal-spinner"><div class="spinner"></div></div>
    <div v-else-if="drives.length===0" class="empty-state"><i class="bi bi-briefcase"></i><h5>No drives found</h5></div>
    <div v-else class="portal-table fade-in"><table class="table mb-0"><thead><tr><th>Position</th><th>Company</th><th>Type</th><th>Deadline</th><th>Apps</th><th>Status</th><th>Actions</th></tr></thead><tbody>
        <tr v-for="d in drives" :key="d.id">
            <td><div style="font-weight:600" v-text="d.title"></div><div style="font-size:0.75rem;color:var(--text-muted)" v-text="d.location||''"></div></td>
            <td v-text="d.company?.name||'—'"></td>
            <td v-text="d.job_type||'—'"></td>
            <td style="font-size:0.85rem" v-text="formatDate(d.application_deadline)"></td>
            <td v-text="d.total_applications||0"></td>
            <td><span class="badge-status" :class="'badge-'+d.status" v-text="d.status"></span></td>
            <td><div class="d-flex gap-1">
                <button v-if="d.status==='pending'" class="btn btn-sm btn-success-portal btn-portal" style="padding:5px 12px;font-size:0.78rem" @click="approve(d.id)"><i class="bi bi-check-lg"></i></button>
                <button v-if="d.status==='pending'" class="btn btn-sm btn-danger-portal btn-portal" style="padding:5px 12px;font-size:0.78rem" @click="reject(d.id)"><i class="bi bi-x-lg"></i></button>
                <button v-if="d.status==='approved'" class="btn btn-sm btn-outline-portal btn-portal" style="padding:5px 12px;font-size:0.78rem" @click="close(d.id)"><i class="bi bi-lock"></i></button>
                <button class="btn btn-sm btn-portal" style="padding:5px 12px;font-size:0.78rem;background:rgba(239,71,111,0.1);color:var(--danger)" @click="remove(d.id)"><i class="bi bi-trash3"></i></button>
            </div></td>
        </tr>
    </tbody></table></div>`,
    data() { return { drives: [], search: '', sf: '', loading: true, page: 1, timer: null } },
    methods: {
        debounceSearch() { clearTimeout(this.timer); this.timer = setTimeout(() => this.fetchData(), 400) },
        formatDate(d) { if (!d) return '—'; return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) },
        async fetchData() { this.loading = true; try { const q = new URLSearchParams({ search: this.search, status: this.sf, page: this.page }); const d = await this.$root.apiCall(`/api/admin/drives?${q}`); this.drives = d.drives } catch (e) { this.$root.showToast(e.message, 'danger') } this.loading = false },
        async approve(id) { try { await this.$root.apiCall(`/api/admin/drives/${id}/approve`, { method: 'PUT' }); this.$root.showToast('Drive approved', 'success'); this.fetchData(); this.$root.fetchAdminCounts() } catch (e) { this.$root.showToast(e.message, 'danger') } },
        async reject(id) { try { await this.$root.apiCall(`/api/admin/drives/${id}/reject`, { method: 'PUT' }); this.$root.showToast('Drive rejected', 'warning'); this.fetchData(); this.$root.fetchAdminCounts() } catch (e) { this.$root.showToast(e.message, 'danger') } },
        async close(id) { try { await this.$root.apiCall(`/api/admin/drives/${id}/close`, { method: 'PUT' }); this.$root.showToast('Drive closed', 'info'); this.fetchData() } catch (e) { this.$root.showToast(e.message, 'danger') } },
        async remove(id) { if (!confirm('Delete this drive?')) return; try { await this.$root.apiCall(`/api/admin/drives/${id}`, { method: 'DELETE' }); this.$root.showToast('Drive deleted', 'success'); this.fetchData() } catch (e) { this.$root.showToast(e.message, 'danger') } }
    },
    mounted() { this.fetchData() }
};
