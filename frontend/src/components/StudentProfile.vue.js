// StudentProfile.vue.js
const StudentProfileComponent = {
    template: `
    <div class="page-header"><h1 class="page-title">My Profile</h1><p class="page-subtitle">Manage your student profile and resume</p></div>
    <div v-if="loading" class="portal-spinner"><div class="spinner"></div></div>
    <div v-else class="row g-4">
        <div class="col-lg-8">
            <div class="form-portal fade-in">
                <h5 class="mb-3" style="font-family:var(--font-heading)">Personal Information</h5>
                <div v-if="msg" class="alert-portal success mb-3"><i class="bi bi-check-circle"></i> {{msg}}</div>
                <form @submit.prevent="save">
                    <div class="row">
                        <div class="col-md-6 mb-3"><label class="form-label">Full Name</label><input class="form-control" v-model="form.name" required></div>
                        <div class="col-md-6 mb-3"><label class="form-label">Roll Number</label><input class="form-control" v-model="form.roll_number"></div>
                    </div>
                    <div class="row">
                        <div class="col-md-4 mb-3"><label class="form-label">Branch</label><select class="form-select" v-model="form.branch"><option value="">Select</option><option v-for="b in branches" :value="b" v-text="b"></option></select></div>
                        <div class="col-md-4 mb-3"><label class="form-label">CGPA</label><input type="number" step="0.01" min="0" max="10" class="form-control" v-model="form.cgpa"></div>
                        <div class="col-md-4 mb-3"><label class="form-label">Graduation Year</label><input type="number" class="form-control" v-model="form.year"></div>
                    </div>
                    <div class="mb-3"><label class="form-label">Phone</label><input class="form-control" v-model="form.phone"></div>
                    <div class="mb-3"><label class="form-label">Skills (comma-separated)</label><input class="form-control" v-model="form.skills" placeholder="e.g. Python, JavaScript, React"></div>
                    <div class="mb-3"><label class="form-label">Bio</label><textarea class="form-control" v-model="form.bio" rows="3" placeholder="Tell us about yourself..."></textarea></div>
                    <div class="row">
                        <div class="col-md-6 mb-3"><label class="form-label">LinkedIn URL</label><input type="url" class="form-control" v-model="form.linkedin_url" placeholder="https://linkedin.com/in/..."></div>
                        <div class="col-md-6 mb-3"><label class="form-label">GitHub URL</label><input type="url" class="form-control" v-model="form.github_url" placeholder="https://github.com/..."></div>
                    </div>
                    <button type="submit" class="btn btn-portal btn-primary-portal" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm"></span> Save Profile</button>
                </form>
            </div>
        </div>
        <div class="col-lg-4">
            <div class="portal-card fade-in mb-3">
                <h5 class="mb-3" style="font-family:var(--font-heading)">Resume</h5>
                <div v-if="form.resume_path" class="alert-portal success mb-3"><i class="bi bi-file-earmark-pdf"></i> Resume uploaded</div>
                <div v-else class="alert-portal warning mb-3"><i class="bi bi-exclamation-circle"></i> No resume uploaded</div>
                <form @submit.prevent="uploadResume" enctype="multipart/form-data">
                    <input type="file" class="form-control mb-3" ref="resumeInput" accept=".pdf,.doc,.docx" style="background:var(--bg-input);border-color:var(--border-color);color:var(--text-primary)">
                    <button type="submit" class="btn btn-portal btn-outline-portal w-100" :disabled="uploading"><i class="bi bi-upload"></i> {{uploading?'Uploading...':'Upload Resume'}}</button>
                </form>
            </div>
            <div class="portal-card fade-in">
                <h5 class="mb-3" style="font-family:var(--font-heading)">Profile Summary</h5>
                <div class="d-flex justify-content-between mb-2" style="font-size:0.88rem"><span style="color:var(--text-muted)">Email</span><span v-text="form.email||'—'"></span></div>
                <div class="d-flex justify-content-between mb-2" style="font-size:0.88rem"><span style="color:var(--text-muted)">CGPA</span><span v-text="form.cgpa||'—'"></span></div>
                <div class="d-flex justify-content-between mb-2" style="font-size:0.88rem"><span style="color:var(--text-muted)">Branch</span><span v-text="form.branch||'—'"></span></div>
                <div class="d-flex justify-content-between mb-2" style="font-size:0.88rem"><span style="color:var(--text-muted)">Applications</span><span v-text="form.total_applications||0"></span></div>
                <div class="d-flex justify-content-between" style="font-size:0.88rem"><span style="color:var(--text-muted)">Status</span><span :class="form.is_placed?'badge-status badge-selected':'badge-status badge-active'" v-text="form.is_placed?'Placed':'Active'"></span></div>
            </div>
        </div>
    </div>`,
    data() { return { form: {}, loading: true, saving: false, uploading: false, msg: '', branches: ['CSE', 'ECE', 'EEE', 'ME', 'CE', 'IT', 'Chemical', 'Biotech', 'Other'] } },
    methods: {
        async fetchData() { this.loading = true; try { const d = await this.$root.apiCall('/api/student/profile'); this.form = { ...d.student } } catch (e) { this.$root.showToast(e.message, 'danger') } this.loading = false },
        async save() { this.saving = true; this.msg = ''; try { await this.$root.apiCall('/api/student/profile', { method: 'PUT', body: JSON.stringify(this.form) }); this.msg = 'Profile updated!'; this.$root.showToast('Profile saved', 'success') } catch (e) { this.$root.showToast(e.message, 'danger') } this.saving = false },
        async uploadResume() { const f = this.$refs.resumeInput.files[0]; if (!f) { this.$root.showToast('Select a file', 'warning'); return } this.uploading = true; try { const fd = new FormData(); fd.append('resume', f); const h = { 'Authorization': `Bearer ${this.$root.token}` }; const r = await fetch('/api/student/profile/resume', { method: 'POST', headers: h, body: fd }); const d = await r.json(); if (!r.ok) throw { message: d.error }; this.form.resume_path = d.resume_path; this.$root.showToast('Resume uploaded!', 'success') } catch (e) { this.$root.showToast(e.message, 'danger') } this.uploading = false }
    },
    mounted() { this.fetchData() }
};
