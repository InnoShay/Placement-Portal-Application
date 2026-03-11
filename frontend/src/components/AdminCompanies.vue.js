// AdminCompanies.vue.js
const AdminCompaniesComponent = {
    template: `
    <div class="page-header"><h1 class="page-title">Company Management</h1><p class="page-subtitle">Approve, reject, and manage company registrations</p></div>
    <div class="d-flex flex-wrap gap-2 mb-4 align-items-center">
        <div class="search-box" style="flex:1;min-width:200px;max-width:400px"><i class="bi bi-search search-icon"></i><input type="text" v-model="search" @input="debounceSearch" placeholder="Search companies..."></div>
        <div class="portal-tabs mb-0" style="border:none">
            <button :class="{active:statusFilter===''}" @click="statusFilter='';fetchData()">All</button>
            <button :class="{active:statusFilter==='pending'}" @click="statusFilter='pending';fetchData()">Pending</button>
            <button :class="{active:statusFilter==='approved'}" @click="statusFilter='approved';fetchData()">Approved</button>
            <button :class="{active:statusFilter==='rejected'}" @click="statusFilter='rejected';fetchData()">Rejected</button>
        </div>
    </div>
    <div v-if="loading" class="portal-spinner"><div class="spinner"></div></div>
    <div v-else-if="companies.length===0" class="empty-state"><i class="bi bi-buildings"></i><h5>No companies found</h5></div>
    <div v-else class="portal-table fade-in"><table class="table mb-0"><thead><tr><th>Company</th><th>Industry</th><th>Location</th><th>HR Contact</th><th>Status</th><th>Actions</th></tr></thead><tbody>
        <tr v-for="c in companies" :key="c.id">
            <td><div class="d-flex align-items-center gap-2"><div class="sidebar-avatar" style="width:34px;height:34px;font-size:0.75rem" v-text="c.name?c.name[0].toUpperCase():'?'"></div><div><div style="font-weight:600;font-size:0.88rem" v-text="c.name"></div><div style="font-size:0.75rem;color:var(--text-muted)" v-text="c.website||''"></div></div></div></td>
            <td v-text="c.industry||'—'"></td>
            <td v-text="c.location||'—'"></td>
            <td><span v-text="c.hr_name||'—'" style="font-size:0.85rem"></span><br><span style="font-size:0.75rem;color:var(--text-muted)" v-text="c.hr_email||''"></span></td>
            <td><span class="badge-status" :class="'badge-'+c.approval_status" v-text="c.approval_status"></span><span v-if="c.is_blacklisted" class="badge-status badge-rejected ms-1">Blacklisted</span></td>
            <td>
                <div class="d-flex gap-1">
                    <button v-if="c.approval_status==='pending'" class="btn btn-sm btn-success-portal btn-portal" style="padding:5px 12px;font-size:0.78rem" @click="approve(c.id)"><i class="bi bi-check-lg"></i></button>
                    <button v-if="c.approval_status==='pending'" class="btn btn-sm btn-danger-portal btn-portal" style="padding:5px 12px;font-size:0.78rem" @click="reject(c.id)"><i class="bi bi-x-lg"></i></button>
                    <button class="btn btn-sm btn-outline-portal btn-portal" style="padding:5px 12px;font-size:0.78rem" @click="toggleBlacklist(c.id)" :title="c.is_blacklisted?'Unblacklist':'Blacklist'"><i :class="c.is_blacklisted?'bi bi-unlock':'bi bi-lock'"></i></button>
                    <button class="btn btn-sm btn-portal" style="padding:5px 12px;font-size:0.78rem;background:rgba(239,71,111,0.1);color:var(--danger)" @click="remove(c.id)"><i class="bi bi-trash3"></i></button>
                </div>
            </td>
        </tr>
    </tbody></table></div>
    <div v-if="totalPages>1" class="portal-pagination"><button :disabled="page<=1" @click="page--;fetchData()">‹</button><button v-for="p in totalPages" :key="p" :class="{active:page===p}" @click="page=p;fetchData()" v-text="p"></button><button :disabled="page>=totalPages" @click="page++;fetchData()">›</button></div>`,
    data() { return { companies: [], search: '', statusFilter: '', loading: true, page: 1, totalPages: 1, timer: null } },
    methods: {
        debounceSearch() { clearTimeout(this.timer); this.timer = setTimeout(() => { this.page = 1; this.fetchData() }, 400) },
        async fetchData() {
            this.loading = true;
            try {
                const q = new URLSearchParams({ search: this.search, status: this.statusFilter, page: this.page, per_page: 15 });
                const data = await this.$root.apiCall(`/api/admin/companies?${q}`);
                this.companies = data.companies; this.totalPages = data.pages || 1;
            } catch (e) { this.$root.showToast(e.message, 'danger') }
            this.loading = false;
        },
        async approve(id) { try { await this.$root.apiCall(`/api/admin/companies/${id}/approve`, { method: 'PUT' }); this.$root.showToast('Company approved', 'success'); this.fetchData(); this.$root.fetchAdminCounts() } catch (e) { this.$root.showToast(e.message, 'danger') } },
        async reject(id) { try { await this.$root.apiCall(`/api/admin/companies/${id}/reject`, { method: 'PUT' }); this.$root.showToast('Company rejected', 'warning'); this.fetchData(); this.$root.fetchAdminCounts() } catch (e) { this.$root.showToast(e.message, 'danger') } },
        async toggleBlacklist(id) { try { await this.$root.apiCall(`/api/admin/companies/${id}/blacklist`, { method: 'PUT' }); this.$root.showToast('Blacklist updated', 'info'); this.fetchData() } catch (e) { this.$root.showToast(e.message, 'danger') } },
        async remove(id) { if (!confirm('Remove this company permanently?')) return; try { await this.$root.apiCall(`/api/admin/companies/${id}`, { method: 'DELETE' }); this.$root.showToast('Company removed', 'success'); this.fetchData(); this.$root.fetchAdminCounts() } catch (e) { this.$root.showToast(e.message, 'danger') } }
    },
    mounted() { this.fetchData() }
};
