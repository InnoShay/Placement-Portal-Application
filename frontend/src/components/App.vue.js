// App.vue.js - Main Vue Application
const app = Vue.createApp({
    data() {
        return {
            isAuthenticated: false,
            user: {},
            profile: {},
            token: localStorage.getItem('ppa_token') || '',
            currentAuthView: 'login',
            currentView: 'dashboard',
            sidebarOpen: false,
            showNotifications: false,
            loading: false,
            globalSearch: '',
            toasts: [],
            authError: '',
            pendingCompanies: 0,
            pendingDrives: 0,
            unreadNotifCount: 0,
            branches: ['CSE','ECE','EEE','ME','CE','IT','Chemical','Biotech','Other'],
            loginForm: { email: '', password: '' },
            registerForm: { email: '', password: '', role: '', name: '', roll_number: '', branch: '', cgpa: '', year: '', company_name: '', industry: '', location: '', hr_name: '', website: '' },
        }
    },
    computed: {
        userName() {
            if (this.user.role === 'company' && this.profile.name) return this.profile.name;
            if (this.user.role === 'student' && this.profile.name) return this.profile.name;
            if (this.user.role === 'admin') return 'Administrator';
            return this.user.email || 'User';
        },
        userInitials() {
            const n = this.userName;
            if (!n) return '?';
            return n.split(' ').map(w => w[0]).join('').substring(0,2).toUpperCase();
        },
        viewTitle() {
            const titles = {
                'dashboard': 'Dashboard', 'companies': 'Companies', 'students': 'Students',
                'drives': 'Placement Drives', 'applications': 'Applications', 'placements': 'Placements',
                'profile': this.user.role === 'company' ? 'Company Profile' : 'My Profile',
                'my-jobs': 'Job Postings', 'manage-apps': 'Manage Applications',
                'browse-jobs': 'Browse Jobs', 'my-applications': 'My Applications',
                'my-placements': 'My Placements'
            };
            return titles[this.currentView] || 'Dashboard';
        },
        currentComponent() {
            if (this.user.role === 'admin') {
                const map = { 'dashboard':'admin-dashboard','companies':'admin-companies','students':'admin-students','drives':'admin-drives','applications':'admin-applications','placements':'admin-placements' };
                return map[this.currentView] || 'admin-dashboard';
            }
            if (this.user.role === 'company') {
                const map = { 'dashboard':'company-dashboard','profile':'company-profile','my-jobs':'company-jobs','manage-apps':'company-applications' };
                return map[this.currentView] || 'company-dashboard';
            }
            if (this.user.role === 'student') {
                const map = { 'dashboard':'student-dashboard','browse-jobs':'student-jobs','my-applications':'student-applications','my-placements':'student-placements','profile':'student-profile' };
                return map[this.currentView] || 'student-dashboard';
            }
            return 'student-dashboard';
        }
    },
    methods: {
        async apiCall(url, options = {}) {
            const headers = { 'Content-Type': 'application/json' };
            if (this.token) headers['Authorization'] = `Bearer ${this.token}`;
            if (options.headers) Object.assign(headers, options.headers);
            const res = await fetch(url, { ...options, headers });
            const data = await res.json();
            if (!res.ok) throw { status: res.status, message: data.error || 'Request failed' };
            return data;
        },
        showToast(message, type = 'info') {
            const icons = { success:'bi bi-check-circle-fill', danger:'bi bi-exclamation-triangle-fill', warning:'bi bi-exclamation-circle-fill', info:'bi bi-info-circle-fill' };
            const id = Date.now();
            this.toasts.push({ id, message, type, icon: icons[type] || icons.info });
            setTimeout(() => { this.toasts = this.toasts.filter(t => t.id !== id); }, 4000);
        },
        navigate(view) {
            this.currentView = view;
            this.sidebarOpen = false;
        },
        async login() {
            this.loading = true; this.authError = '';
            try {
                const data = await this.apiCall('/api/auth/login', { method: 'POST', body: JSON.stringify(this.loginForm) });
                this.token = data.token;
                localStorage.setItem('ppa_token', data.token);
                this.user = data.user;
                this.profile = data.company || data.student || {};
                this.isAuthenticated = true;
                this.currentView = 'dashboard';
                this.showToast('Welcome back!', 'success');
                if (this.user.role === 'admin') this.fetchAdminCounts();
            } catch (e) { this.authError = e.message; }
            this.loading = false;
        },
        async register() {
            this.loading = true; this.authError = '';
            try {
                const data = await this.apiCall('/api/auth/register', { method: 'POST', body: JSON.stringify(this.registerForm) });
                this.token = data.token;
                localStorage.setItem('ppa_token', data.token);
                this.user = data.user;
                this.isAuthenticated = true;
                this.currentView = 'dashboard';
                this.showToast(data.message, 'success');
            } catch (e) { this.authError = e.message; }
            this.loading = false;
        },
        logout() {
            this.token = ''; this.user = {}; this.profile = {};
            this.isAuthenticated = false; localStorage.removeItem('ppa_token');
            this.currentView = 'dashboard'; this.currentAuthView = 'login';
        },
        async checkAuth() {
            if (!this.token) return;
            try {
                const data = await this.apiCall('/api/auth/me');
                this.user = data.user;
                this.profile = data.company || data.student || {};
                this.isAuthenticated = true;
                if (this.user.role === 'admin') this.fetchAdminCounts();
                this.fetchNotifCount();
            } catch { this.logout(); }
        },
        async fetchAdminCounts() {
            try {
                const data = await this.apiCall('/api/admin/dashboard');
                this.pendingCompanies = data.stats.pending_companies;
                this.pendingDrives = data.stats.pending_drives;
            } catch {}
        },
        async fetchNotifCount() {
            try {
                const data = await this.apiCall('/api/notifications');
                this.unreadNotifCount = data.unread_count;
            } catch {}
        },
        handleGlobalSearch() {
            if (!this.globalSearch.trim()) return;
            if (this.user.role === 'admin') { this.currentView = 'students'; }
            else if (this.user.role === 'student') { this.currentView = 'browse-jobs'; }
        }
    },
    mounted() { this.checkAuth(); }
});

// Register all components then mount
app.component('admin-dashboard', AdminDashboardComponent);
app.component('admin-companies', AdminCompaniesComponent);
app.component('admin-students', AdminStudentsComponent);
app.component('admin-drives', AdminDrivesComponent);
app.component('admin-applications', AdminApplicationsComponent);
app.component('admin-placements', AdminPlacementsComponent);
app.component('company-dashboard', CompanyDashboardComponent);
app.component('company-profile', CompanyProfileComponent);
app.component('company-jobs', CompanyJobsComponent);
app.component('company-applications', CompanyApplicationsComponent);
app.component('student-dashboard', StudentDashboardComponent);
app.component('student-profile', StudentProfileComponent);
app.component('student-jobs', StudentJobsComponent);
app.component('student-applications', StudentApplicationsComponent);
app.component('student-placements', StudentPlacementsComponent);

app.mount('#app');
