// StudentDashboard.vue.js
const StudentDashboardComponent = {
    template: `
    <div class="page-header"><h1 class="page-title">Student Dashboard</h1><p class="page-subtitle">Your placement activity at a glance</p></div>
    <div v-if="loading" class="portal-spinner"><div class="spinner"></div></div>
    <div v-else>
        <div class="row g-3 mb-4">
            <div class="col-6 col-lg-4 col-xl-2" v-for="s in statCards" :key="s.label">
                <div class="stat-card fade-in"><div class="stat-icon" :class="s.color"><i :class="s.icon"></i></div><div class="stat-value" v-text="s.value"></div><div class="stat-label" v-text="s.label"></div></div>
            </div>
        </div>
        <div class="row g-4">
            <div class="col-lg-7">
                <div class="portal-card fade-in">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 style="font-family:var(--font-heading);margin:0">Upcoming Interviews</h5>
                    </div>
                    <div v-if="interviews.length===0" class="empty-state py-4"><i class="bi bi-calendar-event"></i><p>No upcoming interviews</p></div>
                    <div v-else v-for="a in interviews" :key="a.id" class="d-flex align-items-center gap-3 p-3 mb-2" style="background:var(--bg-surface);border-radius:var(--radius-md)">
                        <div style="width:48px;height:48px;border-radius:var(--radius-md);background:rgba(114,9,183,0.12);display:flex;align-items:center;justify-content:center"><i class="bi bi-camera-video" style="color:var(--secondary);font-size:1.2rem"></i></div>
                        <div style="flex:1;min-width:0"><div style="font-weight:600;font-size:0.92rem" v-text="a.job?.title||'Interview'"></div><div style="font-size:0.8rem;color:var(--text-muted)">{{a.job?.company?.name}} • {{formatDate(a.interview_date)}} {{a.interview_time||''}}</div></div>
                        <a v-if="a.interview_link" :href="a.interview_link" target="_blank" class="btn btn-sm btn-portal btn-primary-portal" style="font-size:0.78rem">Join</a>
                    </div>
                </div>
            </div>
            <div class="col-lg-5">
                <div class="portal-card fade-in">
                    <h5 style="font-family:var(--font-heading)" class="mb-3">Quick Actions</h5>
                    <div class="d-grid gap-2">
                        <button class="btn btn-portal btn-primary-portal" @click="$root.navigate('browse-jobs')"><i class="bi bi-search"></i> Browse Jobs</button>
                        <button class="btn btn-portal btn-outline-portal" @click="$root.navigate('my-applications')"><i class="bi bi-file-text"></i> View Applications</button>
                        <button class="btn btn-portal btn-outline-portal" @click="$root.navigate('profile')"><i class="bi bi-pencil"></i> Edit Profile</button>
                        <button class="btn btn-portal btn-outline-portal" @click="exportCSV" :disabled="exporting"><i class="bi bi-download"></i> {{exporting?'Exporting...':'Export History (CSV)'}}</button>
                    </div>
                </div>
            </div>
        </div>
    </div>`,
    data() { return { loading: true, stats: {}, interviews: [], exporting: false } },
    computed: {
        statCards() {
            const s = this.stats; return [
                { label: 'Available Drives', value: s.available_drives || 0, icon: 'bi bi-briefcase-fill', color: 'primary' },
                { label: 'Applied', value: s.applied || 0, icon: 'bi bi-send-fill', color: 'info' },
                { label: 'Shortlisted', value: s.shortlisted || 0, icon: 'bi bi-star-fill', color: 'warning' },
                { label: 'Interviews', value: s.interview || 0, icon: 'bi bi-camera-video-fill', color: 'accent' },
                { label: 'Selected', value: s.selected || 0, icon: 'bi bi-trophy-fill', color: 'success' },
                { label: 'Total Apps', value: s.total_applications || 0, icon: 'bi bi-file-text-fill', color: 'danger' },
            ]
        }
    },
    methods: {
        formatDate(d) { if (!d) return '—'; return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }) },
        async fetchData() { this.loading = true; try { const d = await this.$root.apiCall('/api/student/dashboard'); this.stats = d.stats; this.interviews = d.upcoming_interviews || [] } catch (e) { this.$root.showToast(e.message, 'danger') } this.loading = false },
        async exportCSV() { this.exporting = true; try { await this.$root.apiCall('/api/student/export/csv', { method: 'POST' }); this.$root.showToast('CSV export started. Check notifications when ready.', 'success') } catch (e) { this.$root.showToast(e.message, 'danger') } this.exporting = false }
    },
    mounted() { this.fetchData() }
};
