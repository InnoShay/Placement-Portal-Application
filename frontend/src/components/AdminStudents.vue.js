// AdminStudents.vue.js
const AdminStudentsComponent = {
    template: `
    <div class="page-header"><h1 class="page-title">Student Management</h1><p class="page-subtitle">View and manage all registered students</p></div>
    <div class="d-flex gap-2 mb-4"><div class="search-box" style="flex:1;max-width:400px"><i class="bi bi-search search-icon"></i><input v-model="search" @input="debounceSearch" placeholder="Search by name, roll number, branch..."></div></div>
    <div v-if="loading" class="portal-spinner"><div class="spinner"></div></div>
    <div v-else-if="students.length===0" class="empty-state"><i class="bi bi-people"></i><h5>No students found</h5></div>
    <div v-else class="portal-table fade-in"><table class="table mb-0"><thead><tr><th>Student</th><th>Roll No</th><th>Branch</th><th>CGPA</th><th>Year</th><th>Applications</th><th>Status</th><th>Actions</th></tr></thead><tbody>
        <tr v-for="s in students" :key="s.id">
            <td><div style="font-weight:600;font-size:0.88rem" v-text="s.name"></div><div style="font-size:0.75rem;color:var(--text-muted)" v-text="s.email||''"></div></td>
            <td v-text="s.roll_number||'—'"></td><td v-text="s.branch||'—'"></td><td v-text="s.cgpa||'—'"></td><td v-text="s.year||'—'"></td>
            <td v-text="s.total_applications||0"></td>
            <td><span v-if="s.is_placed" class="badge-status badge-selected">Placed</span><span v-else-if="s.is_blacklisted" class="badge-status badge-rejected">Blacklisted</span><span v-else class="badge-status badge-active">Active</span></td>
            <td><div class="d-flex gap-1">
                <button class="btn btn-sm btn-outline-portal btn-portal" style="padding:5px 12px;font-size:0.78rem" @click="toggleBlacklist(s.id)" :title="s.is_blacklisted?'Unblacklist':'Blacklist'"><i :class="s.is_blacklisted?'bi bi-unlock':'bi bi-lock'"></i></button>
            </div></td>
        </tr>
    </tbody></table></div>
    <div v-if="totalPages>1" class="portal-pagination"><button :disabled="page<=1" @click="page--;fetchData()">‹</button><button v-for="p in totalPages" :key="p" :class="{active:page===p}" @click="page=p;fetchData()" v-text="p"></button><button :disabled="page>=totalPages" @click="page++;fetchData()">›</button></div>`,
    data() { return { students: [], search: '', loading: true, page: 1, totalPages: 1, timer: null } },
    methods: {
        debounceSearch() { clearTimeout(this.timer); this.timer = setTimeout(() => { this.page = 1; this.fetchData() }, 400) },
        async fetchData() { this.loading = true; try { const q = new URLSearchParams({ search: this.search, page: this.page, per_page: 15 }); const d = await this.$root.apiCall(`/api/admin/students?${q}`); this.students = d.students; this.totalPages = d.pages || 1 } catch (e) { this.$root.showToast(e.message, 'danger') } this.loading = false },
        async toggleBlacklist(id) { try { await this.$root.apiCall(`/api/admin/students/${id}/blacklist`, { method: 'PUT' }); this.$root.showToast('Status updated', 'info'); this.fetchData() } catch (e) { this.$root.showToast(e.message, 'danger') } }
    },
    mounted() { this.fetchData() }
};
