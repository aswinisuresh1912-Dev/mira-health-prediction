const API_URL = '/api/patients';

let patientsData = [];
let patientToDeleteId = null;

// grab DOM elements
const patientTableBody = document.getElementById('patient-table-body');
const searchInput = document.getElementById('search-input');

const statTotalPatients = document.getElementById('stat-total-patients');
const statHighRisk = document.getElementById('stat-high-risk');
const statAvgGlucose = document.getElementById('stat-avg-glucose');
const statAvgCholesterol = document.getElementById('stat-avg-cholesterol');
const tableCountBadge = document.getElementById('table-count-badge');

const modalPatient = document.getElementById('modal-patient');
const modalDelete = document.getElementById('modal-delete');
const patientForm = document.getElementById('patient-form');
const modalTitle = document.getElementById('modal-title');
const btnSubmitForm = document.getElementById('btn-submit-form');
const submitBtnText = btnSubmitForm.querySelector('.btn-text');

const formId = document.getElementById('patient-id');
const formName = document.getElementById('form-name');
const formDob = document.getElementById('form-dob');
const formEmail = document.getElementById('form-email');
const formGlucose = document.getElementById('form-glucose');
const formHaemoglobin = document.getElementById('form-haemoglobin');
const formCholesterol = document.getElementById('form-cholesterol');
const formGender = document.getElementById('form-gender');

const errName = document.getElementById('err-name');
const errDob = document.getElementById('err-dob');
const errEmail = document.getElementById('err-email');
const errGlucose = document.getElementById('err-glucose');
const errHaemoglobin = document.getElementById('err-haemoglobin');
const errCholesterol = document.getElementById('err-cholesterol');
const errGender = document.getElementById('err-gender');

const btnNewPatient = document.getElementById('btn-new-patient');
const btnCloseModal = document.getElementById('btn-close-modal');
const btnCancelModal = document.getElementById('btn-cancel-modal');
const btnCloseDelete = document.getElementById('btn-close-delete');
const btnCancelDelete = document.getElementById('btn-cancel-delete');
const btnConfirmDelete = document.getElementById('btn-confirm-delete');
const deletePatientName = document.getElementById('delete-patient-name');

const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebar-toggle');


document.addEventListener('DOMContentLoaded', () => {
    fetchPatients();

    searchInput.addEventListener('input', filterPatients);

    btnNewPatient.addEventListener('click', () => openPatientModal());
    btnCloseModal.addEventListener('click', closePatientModal);
    btnCancelModal.addEventListener('click', closePatientModal);

    btnCloseDelete.addEventListener('click', closeDeleteModal);
    btnCancelDelete.addEventListener('click', closeDeleteModal);
    btnConfirmDelete.addEventListener('click', confirmDeleteRecord);

    patientForm.addEventListener('submit', handleFormSubmit);

    // sidebar view switching
    const navDashboard = document.getElementById('nav-dashboard');
    const navPatients = document.getElementById('nav-patients');
    const statsRow = document.querySelector('.stats-row');
    const pageTitle = document.querySelector('.page-title');
    const pageSubtitle = document.querySelector('.page-subtitle');

    if (navDashboard && navPatients) {
        navDashboard.addEventListener('click', (e) => {
            e.preventDefault();
            navDashboard.classList.add('active');
            navPatients.classList.remove('active');
            if (statsRow) statsRow.style.display = 'grid';
            if (pageTitle) pageTitle.textContent = "Health Prediction Dashboard";
            if (pageSubtitle) pageSubtitle.textContent = "Real-time patient diagnostics powered by ML-based risk analysis";
            window.scrollTo({ top: 0, behavior: 'smooth' });
            if (window.innerWidth <= 768 && sidebar) sidebar.classList.remove('open');
        });

        navPatients.addEventListener('click', (e) => {
            e.preventDefault();
            navPatients.classList.add('active');
            navDashboard.classList.remove('active');
            if (statsRow) statsRow.style.display = 'none';
            if (pageTitle) pageTitle.textContent = "Patient Records";
            if (pageSubtitle) pageSubtitle.textContent = "Manage and view all registered patient medical histories";
            window.scrollTo({ top: 0, behavior: 'smooth' });
            if (window.innerWidth <= 768 && sidebar) sidebar.classList.remove('open');
        });
    }

    // sidebar toggle for mobile
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    // clear errors as user types / changes
    const inputs = [formName, formDob, formEmail, formGlucose, formHaemoglobin, formCholesterol, formGender];
    inputs.forEach(input => {
        const eventType = input.tagName === 'SELECT' ? 'change' : 'input';
        input.addEventListener(eventType, () => {
            const errId = 'err-' + input.id.replace('form-', '');
            const errEl = document.getElementById(errId);
            if (errEl) errEl.textContent = '';
        });
    });
});


function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let iconClass = 'fa-info-circle';
    if (type === 'success') iconClass = 'fa-check-circle';
    if (type === 'danger') iconClass = 'fa-exclamation-triangle';
    if (type === 'warning') iconClass = 'fa-circle-exclamation';

    toast.innerHTML = `
        <i class="fa-solid ${iconClass}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 50);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}


async function fetchPatients() {
    showTableLoading(true);
    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error('Failed to load patient records.');
        patientsData = await response.json();
        renderPatients(patientsData);
        updateDashboardStats(patientsData);
    } catch (err) {
        showToast(err.message, 'danger');
        patientTableBody.innerHTML = `
            <tr class="table-placeholder">
                <td colspan="7">
                    <div class="empty-state text-danger">
                        <i class="fa-solid fa-circle-xmark"></i>
                        <p>Connection failed. Make sure the backend server is running.</p>
                    </div>
                </td>
            </tr>
        `;
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();
    if (!validateForm()) return;

    const payload = {
        full_name: formName.value.trim(),
        dob: formDob.value,
        gender: formGender.value,
        email: formEmail.value.trim(),
        glucose: parseFloat(formGlucose.value),
        haemoglobin: parseFloat(formHaemoglobin.value),
        cholesterol: parseFloat(formCholesterol.value)
    };

    const isEdit = !!formId.value;
    const url = isEdit ? `${API_URL}/${formId.value}` : API_URL;
    const method = isEdit ? 'PUT' : 'POST';

    setFormLoading(true);

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            if (data.detail && typeof data.detail === 'string') {
                throw new Error(data.detail);
            } else if (Array.isArray(data.detail)) {
                throw new Error(data.detail.map(d => `${d.loc[1] || 'Field'}: ${d.msg}`).join(', '));
            } else {
                throw new Error('An error occurred during submission.');
            }
        }

        showToast(isEdit ? 'Patient record updated successfully.' : 'Diagnostics generated! Patient record created.', 'success');
        closePatientModal();
        fetchPatients();
    } catch (err) {
        showToast(err.message, 'danger');
    } finally {
        setFormLoading(false);
    }
}

async function confirmDeleteRecord() {
    if (!patientToDeleteId) return;

    try {
        const response = await fetch(`${API_URL}/${patientToDeleteId}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Failed to delete patient record.');

        showToast('Patient record deleted successfully.', 'success');
        closeDeleteModal();
        fetchPatients();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}


function renderPatients(patients) {
    // update the record count badge
    if (tableCountBadge) {
        tableCountBadge.textContent = `${patients.length} record${patients.length !== 1 ? 's' : ''}`;
    }

    if (patients.length === 0) {
        patientTableBody.innerHTML = `
            <tr class="table-placeholder">
                <td colspan="7">
                    <div class="empty-state">
                        <i class="fa-solid fa-folder-open"></i>
                        <p>No patient records found. Click "New Patient Record" to get started.</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    patientTableBody.innerHTML = '';

    patients.forEach(patient => {
        const row = document.createElement('tr');

        const formattedRemarks = formatRemarks(patient.remarks);
        const glucoseInd = getMetricIndicatorClass(patient.glucose, 'glucose');
        const haemoglobinInd = getMetricIndicatorClass(patient.haemoglobin, 'haemoglobin');
        const cholesterolInd = getMetricIndicatorClass(patient.cholesterol, 'cholesterol');

        row.innerHTML = `
            <td>
                <div class="patient-name-cell">
                    <span class="patient-name">${escapeHTML(patient.full_name)}</span>
                    <span class="patient-email">${escapeHTML(patient.email)}</span>
                </div>
            </td>
            <td>
                <div class="patient-dob-cell">
                    <div>${patient.dob}</div>
                    <div class="text-sm text-muted">Age: ${calculateAge(patient.dob)} • ${escapeHTML(patient.gender)}</div>
                </div>
            </td>
            <td>
                <div class="metric-value">
                    <span class="metric-indicator ${glucoseInd}"></span>
                    <span>${patient.glucose.toFixed(1)}</span>
                </div>
            </td>
            <td>
                <div class="metric-value">
                    <span class="metric-indicator ${haemoglobinInd}"></span>
                    <span>${patient.haemoglobin.toFixed(1)}</span>
                </div>
            </td>
            <td>
                <div class="metric-value">
                    <span class="metric-indicator ${cholesterolInd}"></span>
                    <span>${patient.cholesterol.toFixed(1)}</span>
                </div>
            </td>
            <td>${formattedRemarks}</td>
            <td class="text-right">
                <div class="actions-cell">
                    <button class="btn-icon btn-edit" title="Edit Patient" onclick="openPatientModal(${patient.id})">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </button>
                    <button class="btn-icon btn-delete" title="Delete Patient" onclick="openDeleteModal(${patient.id}, '${escapeQuote(patient.full_name)}')">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </td>
        `;

        patientTableBody.appendChild(row);
    });
}

function updateDashboardStats(patients) {
    statTotalPatients.textContent = patients.length;

    let highRiskCount = 0;
    let sumGlucose = 0.0;
    let sumCholesterol = 0.0;

    patients.forEach(p => {
        if (p.remarks.includes('[High Risk]')) highRiskCount++;
        sumGlucose += p.glucose;
        sumCholesterol += p.cholesterol;
    });

    statHighRisk.textContent = highRiskCount;

    const avgGlucoseVal = patients.length > 0 ? (sumGlucose / patients.length).toFixed(1) : '0';
    const avgCholesterolVal = patients.length > 0 ? (sumCholesterol / patients.length).toFixed(1) : '0';

    statAvgGlucose.innerHTML = `${avgGlucoseVal} <small>mg/dL</small>`;
    statAvgCholesterol.innerHTML = `${avgCholesterolVal} <small>mg/dL</small>`;

    // update the table record badge too
    if (tableCountBadge) {
        tableCountBadge.textContent = `${patients.length} record${patients.length !== 1 ? 's' : ''}`;
    }
}

function filterPatients() {
    const query = searchInput.value.toLowerCase().trim();

    if (!query) {
        renderPatients(patientsData);
        return;
    }

    const filtered = patientsData.filter(p => {
        return p.full_name.toLowerCase().includes(query) ||
               p.email.toLowerCase().includes(query) ||
               p.remarks.toLowerCase().includes(query);
    });

    renderPatients(filtered);
}


function openPatientModal(id = null) {
    clearFormErrors();
    patientForm.reset();

    if (id) {
        const patient = patientsData.find(p => p.id === id);
        if (!patient) return;

        modalTitle.innerHTML = `<i class="fa-solid fa-user-pen"></i> Edit Patient Record`;
        submitBtnText.textContent = "Recompute Diagnostics";

        formId.value = patient.id;
        formName.value = patient.full_name;
        formDob.value = patient.dob;
        formEmail.value = patient.email;
        formGlucose.value = patient.glucose;
        formHaemoglobin.value = patient.haemoglobin;
        formCholesterol.value = patient.cholesterol;
        formGender.value = patient.gender || '';
    } else {
        modalTitle.innerHTML = `<i class="fa-solid fa-user-plus"></i> New Patient Record`;
        submitBtnText.textContent = "Generate Diagnostics";
        formId.value = '';
        formGender.value = '';
    }

    modalPatient.classList.add('active');
}

function closePatientModal() {
    modalPatient.classList.remove('active');
}

function openDeleteModal(id, name) {
    patientToDeleteId = id;
    deletePatientName.textContent = name;
    modalDelete.classList.add('active');
}

function closeDeleteModal() {
    modalDelete.classList.remove('active');
    patientToDeleteId = null;
}


function validateForm() {
    let isValid = true;
    clearFormErrors();

    if (!formName.value.trim()) {
        errName.textContent = "Full name is required.";
        isValid = false;
    }

    const dobValue = formDob.value;
    if (!dobValue) {
        errDob.textContent = "Date of birth is required.";
        isValid = false;
    } else {
        const dobDate = new Date(dobValue);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (dobDate > today) {
            errDob.textContent = "Date of birth cannot be in the future.";
            isValid = false;
        }
    }

    const emailValue = formEmail.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailValue) {
        errEmail.textContent = "Email is required.";
        isValid = false;
    } else if (!emailRegex.test(emailValue)) {
        errEmail.textContent = "Enter a valid email (e.g. name@domain.com).";
        isValid = false;
    }

    if (!formGender.value) {
        errGender.textContent = "Gender selection is required.";
        isValid = false;
    }

    const glucoseVal = parseFloat(formGlucose.value);
    if (isNaN(glucoseVal) || glucoseVal <= 0) {
        errGlucose.textContent = "Must be a positive number.";
        isValid = false;
    }

    const hbVal = parseFloat(formHaemoglobin.value);
    if (isNaN(hbVal) || hbVal <= 0) {
        errHaemoglobin.textContent = "Must be a positive number.";
        isValid = false;
    }

    const cholVal = parseFloat(formCholesterol.value);
    if (isNaN(cholVal) || cholVal <= 0) {
        errCholesterol.textContent = "Must be a positive number.";
        isValid = false;
    }

    return isValid;
}

function clearFormErrors() {
    const errors = [errName, errDob, errGender, errEmail, errGlucose, errHaemoglobin, errCholesterol];
    errors.forEach(err => {
        if (err) err.textContent = '';
    });
}


function getMetricIndicatorClass(val, metric) {
    if (metric === 'glucose') {
        if (val > 125.0) return 'bg-danger';
        if (val > 99.0) return 'bg-warning';
        return 'bg-normal';
    }
    if (metric === 'cholesterol') {
        if (val > 239.0) return 'bg-danger';
        if (val > 199.0) return 'bg-warning';
        return 'bg-normal';
    }
    if (metric === 'haemoglobin') {
        if (val < 10.0) return 'bg-danger';
        if (val < 12.1) return 'bg-warning';
        return 'bg-normal';
    }
    return 'bg-normal';
}

function formatRemarks(remarksText) {
    let badgeClass = 'badge-low';
    let riskLabel = 'Low Risk';

    if (remarksText.includes('[High Risk]')) {
        badgeClass = 'badge-high';
        riskLabel = 'High Risk';
    } else if (remarksText.includes('[Moderate Risk]')) {
        badgeClass = 'badge-moderate';
        riskLabel = 'Moderate Risk';
    }

    const cleanedText = remarksText.replace(/\[(High|Moderate|Low) Risk\]\s*(Classified as:\s*)?/i, '');

    return `
        <div class="remark-badge-container">
            <span class="remark-badge ${badgeClass}">${riskLabel}</span>
            <span class="remark-text">${escapeHTML(cleanedText)}</span>
        </div>
    `;
}

function calculateAge(dobStr) {
    const dob = new Date(dobStr);
    const today = new Date();
    let age = today.getFullYear() - dob.getFullYear();
    const monthDiff = today.getMonth() - dob.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
        age--;
    }
    return age >= 0 ? age : 0;
}

function escapeHTML(str) {
    return str.replace(/[&<>'"]/g,
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}

function escapeQuote(str) {
    return str.replace(/'/g, "\\'");
}

function showTableLoading(isLoading) {
    if (isLoading) {
        patientTableBody.innerHTML = `
            <tr class="table-placeholder">
                <td colspan="7">
                    <div class="loading-state">
                        <div class="pulse-loader"></div>
                        <p>Loading patient records...</p>
                    </div>
                </td>
            </tr>
        `;
    }
}

function setFormLoading(isLoading) {
    if (isLoading) {
        btnSubmitForm.disabled = true;
        submitBtnText.textContent = "Processing Diagnostics...";
    } else {
        btnSubmitForm.disabled = false;
        submitBtnText.textContent = "Generate Diagnostics";
    }
}
