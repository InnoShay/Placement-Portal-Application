// CompanyProfile.vue.js
const CompanyProfileComponent = {
    template: `
    <div class="page-header"><h1 class="page-title">Company Profile</h1><p class="page-subtitle">Manage your company information</p></div>
    <div v-if="loading" class="portal-spinner"><div class="spinner"></div></div>
    <div v-else class="form-portal fade-in" style="max-width:700px">
        <div v-if="msg" class="alert-portal success mb-3"><i class="bi bi-check-circle"></i> {{msg}}</div>
        <form @submit.prevent="save">
            <div class="row">
                <div class="col-md-6 mb-3"><label class="form-label">Company Name</label><input class="form-control" v-model="form.name" required></div>
                <div class="col-md-6 mb-3"><label class="form-label">Industry</label><input class="form-control" v-model="form.industry"></div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3"><label class="form-label">Location</label><input class="form-control" v-model="form.location"></div>
                <div class="col-md-6 mb-3"><label class="form-label">Website</label><input type="url" class="form-control" v-model="form.website"></div>
            </div>
            <div class="row">
                <div class="col-md-4 mb-3"><label class="form-label">HR Name</label><input class="form-control" v-model="form.hr_name"></div>
                <div class="col-md-4 mb-3"><label class="form-label">HR Email</label><input type="email" class="form-control" v-model="form.hr_email"></div>
                <div class="col-md-4 mb-3"><label class="form-label">HR Phone</label><input class="form-control" v-model="form.hr_phone"></div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3"><label class="form-label">Company Size</label><select class="form-select" v-model="form.company_size"><option value="">Select</option><option v-for="s in ['1-50','51-200','201-500','500+']" :value="s" v-text="s"></option></select></div>
                <div class="col-md-6 mb-3"><label class="form-label">Founded Year</label><input type="number" class="form-control" v-model="form.founded_year"></div>
            </div>
            <div class="mb-3"><label class="form-label">Description</label><textarea class="form-control" v-model="form.description" rows="4"></textarea></div>
            <button type="submit" class="btn btn-portal btn-primary-portal" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm"></span> Save Changes</button>
        </form>
    </div>`,
    data() { return { form: {}, loading: true, saving: false, msg: '' } },
    methods: {
        async fetchData() { this.loading = true; try { const d = await this.$root.apiCall('/api/company/profile'); this.form = { ...d.company } } catch (e) { this.$root.showToast(e.message, 'danger') } this.loading = false },
        async save() { this.saving = true; this.msg = ''; try { await this.$root.apiCall('/api/company/profile', { method: 'PUT', body: JSON.stringify(this.form) }); this.msg = 'Profile updated successfully'; this.$root.showToast('Profile saved', 'success') } catch (e) { this.$root.showToast(e.message, 'danger') } this.saving = false }
    },
    mounted() { this.fetchData() }
};
