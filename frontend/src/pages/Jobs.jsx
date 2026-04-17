import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { jobPostingsAPI } from '../api/client';
import { Plus, MapPin, Briefcase, DollarSign, Clock, Users, X, Globe, Building2, Sparkles } from 'lucide-react';
import { useToast } from '../components/Toast';

const STATUS_STYLES = {
  draft: 'bg-gray-100 text-gray-600 border-gray-200',
  active: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  paused: 'bg-amber-50 text-amber-700 border-amber-200',
  closed: 'bg-red-50 text-red-700 border-red-200',
};

export default function Jobs() {
  const [showForm, setShowForm] = useState(false);
  const [statusFilter, setStatusFilter] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '', department: '', location: '', employment_type: 'full_time',
    experience_level: 'mid', salary_min: '', salary_max: '', description: '',
    responsibilities: '', required_qualifications: '', preferred_qualifications: '',
    benefits: '', skills_required: '', is_remote: false,
  });
  const queryClient = useQueryClient();

  const { data: jobs = [], isLoading } = useQuery({
    queryKey: ['jobs', statusFilter],
    queryFn: () => jobPostingsAPI.getAll({ status: statusFilter || undefined }).then(res => res.data),
  });

  const toast = useToast();

  const createMutation = useMutation({
    mutationFn: (data) => jobPostingsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      setShowForm(false);
      setFormData({ title: '', department: '', location: '', employment_type: 'full_time', experience_level: 'mid', salary_min: '', salary_max: '', description: '', responsibilities: '', required_qualifications: '', preferred_qualifications: '', benefits: '', skills_required: '', is_remote: false });
      toast.success('Job posting created!');
    },
    onError: (err) => {
      const detail = err.response?.data?.detail;
      const msg = Array.isArray(detail) ? detail.map(d => `${d.loc?.join('.')}: ${d.msg}`).join(', ') : (detail || 'Failed to create job');
      toast.error(msg);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => jobPostingsAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      toast.success('Job updated');
    },
    onError: () => toast.error('Failed to update job'),
  });

  const generateWithAI = async () => {
    if (!formData.title) return;
    setAiLoading(true);
    try {
      const res = await jobPostingsAPI.generateDescription(formData.title, formData.department);
      const data = res.data;
      setFormData(prev => ({
        ...prev,
        description: data.description || prev.description,
        responsibilities: data.responsibilities || prev.responsibilities,
        required_qualifications: data.required_qualifications || prev.required_qualifications,
        preferred_qualifications: data.preferred_qualifications || prev.preferred_qualifications,
        benefits: data.benefits || prev.benefits,
        skills_required: (Array.isArray(data.skills_required) ? data.skills_required.join(', ') : data.skills_required) || prev.skills_required,
        experience_level: data.experience_level || prev.experience_level,
      }));
    } catch (err) {
      console.error('AI generation failed:', err);
    } finally {
      setAiLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {};
    // Only include non-empty fields with correct types
    if (formData.title) payload.title = formData.title;
    if (formData.department) payload.department = formData.department;
    if (formData.location) payload.location = formData.location;
    if (formData.employment_type) payload.employment_type = formData.employment_type;
    if (formData.experience_level) payload.experience_level = formData.experience_level;
    if (formData.salary_min) payload.salary_min = parseInt(formData.salary_min);
    if (formData.salary_max) payload.salary_max = parseInt(formData.salary_max);
    if (formData.description) payload.description = formData.description;
    if (formData.responsibilities) payload.responsibilities = formData.responsibilities;
    if (formData.required_qualifications) payload.required_qualifications = formData.required_qualifications;
    if (formData.preferred_qualifications) payload.preferred_qualifications = formData.preferred_qualifications;
    if (formData.benefits) payload.benefits = formData.benefits;
    payload.is_remote = !!formData.is_remote;
    // Handle skills - could be string or array
    if (formData.skills_required) {
      payload.skills_required = typeof formData.skills_required === 'string'
        ? formData.skills_required.split(',').map(s => s.trim()).filter(Boolean)
        : formData.skills_required;
    }
    createMutation.mutate(payload);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Job Postings</h1>
          <p className="text-sm text-gray-500 mt-1">{jobs.length} job postings</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Create Job
        </button>
      </div>

      {/* Status Filter */}
      <div className="flex gap-2">
        {['', 'active', 'draft', 'paused', 'closed'].map(s => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              statusFilter === s ? 'bg-navy-500 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
            }`}
          >
            {s ? s.charAt(0).toUpperCase() + s.slice(1) : 'All'}
          </button>
        ))}
      </div>

      {/* Create Job Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Create Job Posting</h3>
              <button onClick={() => setShowForm(false)} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Job Title *</label>
                <input type="text" required value={formData.title} onChange={(e) => setFormData({...formData, title: e.target.value})} className="input" placeholder="Senior Full Stack Developer" />
              </div>
              <button type="button" onClick={generateWithAI} disabled={!formData.title || aiLoading} className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 disabled:opacity-50">
                <Sparkles className="w-4 h-4" />
                {aiLoading ? 'Generating...' : 'Generate with AI'}
              </button>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
                  <input type="text" value={formData.department} onChange={(e) => setFormData({...formData, department: e.target.value})} className="input" placeholder="Engineering" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                  <input type="text" value={formData.location} onChange={(e) => setFormData({...formData, location: e.target.value})} className="input" placeholder="NYC, United States" />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Employment Type</label>
                  <select value={formData.employment_type} onChange={(e) => setFormData({...formData, employment_type: e.target.value})} className="input">
                    <option value="full_time">Full Time</option>
                    <option value="part_time">Part Time</option>
                    <option value="contract">Contract</option>
                    <option value="internship">Internship</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Experience Level</label>
                  <select value={formData.experience_level} onChange={(e) => setFormData({...formData, experience_level: e.target.value})} className="input">
                    <option value="entry">Entry Level</option>
                    <option value="mid">Mid Level</option>
                    <option value="senior">Senior</option>
                    <option value="lead">Lead</option>
                  </select>
                </div>
                <div className="flex items-end pb-1">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" checked={formData.is_remote} onChange={(e) => setFormData({...formData, is_remote: e.target.checked})} className="w-4 h-4 text-navy-500 rounded border-gray-300" />
                    <span className="text-sm font-medium text-gray-700">Remote</span>
                  </label>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Min Salary ($)</label>
                  <input type="number" value={formData.salary_min} onChange={(e) => setFormData({...formData, salary_min: e.target.value})} className="input" placeholder="100000" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Max Salary ($)</label>
                  <input type="number" value={formData.salary_max} onChange={(e) => setFormData({...formData, salary_max: e.target.value})} className="input" placeholder="250000" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea rows={3} value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} className="input" placeholder="Job description..." />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Responsibilities</label>
                <textarea rows={3} value={formData.responsibilities} onChange={(e) => setFormData({...formData, responsibilities: e.target.value})} className="input" placeholder="Key responsibilities..." />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Required Qualifications</label>
                <textarea rows={3} value={formData.required_qualifications} onChange={(e) => setFormData({...formData, required_qualifications: e.target.value})} className="input" placeholder="Required qualifications..." />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Preferred Qualifications</label>
                <textarea rows={2} value={formData.preferred_qualifications} onChange={(e) => setFormData({...formData, preferred_qualifications: e.target.value})} className="input" placeholder="Preferred qualifications..." />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Skills (comma separated)</label>
                <input type="text" value={formData.skills_required} onChange={(e) => setFormData({...formData, skills_required: e.target.value})} className="input" placeholder="React, Python, AWS, Docker" />
              </div>
              <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
                <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
                <button type="submit" disabled={createMutation.isPending} className="btn-primary disabled:opacity-50">
                  {createMutation.isPending ? 'Creating...' : 'Create Job Posting'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Jobs Grid */}
      {isLoading ? (
        <div className="text-center py-12 text-gray-400">Loading jobs...</div>
      ) : jobs.length === 0 ? (
        <div className="card p-12 text-center">
          <Briefcase className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">No job postings yet</p>
          <p className="text-sm text-gray-400 mt-1">Create your first job posting to attract candidates</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {jobs.map((job) => (
            <div key={job.id} className="card p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{job.title}</h3>
                  <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
                    {job.department && (
                      <span className="flex items-center gap-1"><Building2 className="w-3.5 h-3.5" />{job.department}</span>
                    )}
                    {job.location && (
                      <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" />{job.location}</span>
                    )}
                  </div>
                </div>
                <select
                  value={job.status || 'draft'}
                  onChange={(e) => updateMutation.mutate({ id: job.id, data: { status: e.target.value } })}
                  className={`badge border cursor-pointer ${STATUS_STYLES[job.status] || STATUS_STYLES.draft}`}
                >
                  <option value="draft">Draft</option>
                  <option value="active">Active</option>
                  <option value="paused">Paused</option>
                  <option value="closed">Closed</option>
                </select>
              </div>

              <div className="flex flex-wrap gap-2 mb-4">
                <span className="badge bg-blue-50 text-blue-700 border border-blue-200">
                  <Clock className="w-3 h-3 mr-1" />
                  {job.employment_type?.replace('_', ' ') || 'Full time'}
                </span>
                <span className="badge bg-purple-50 text-purple-700 border border-purple-200">
                  {job.experience_level || 'Mid'} level
                </span>
                {job.is_remote && (
                  <span className="badge bg-sky-50 text-sky-700 border border-sky-200">
                    <Globe className="w-3 h-3 mr-1" />Remote
                  </span>
                )}
              </div>

              {(job.salary_min || job.salary_max) && (
                <div className="flex items-center gap-1.5 text-sm text-gray-600 mb-3">
                  <DollarSign className="w-4 h-4 text-gray-400" />
                  ${job.salary_min?.toLocaleString() || '0'} - ${job.salary_max?.toLocaleString() || '0'}
                </div>
              )}

              {job.skills_required?.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mb-4">
                  {job.skills_required.map((skill, i) => (
                    <span key={i} className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">{skill}</span>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                <span className="flex items-center gap-1.5 text-sm text-gray-500">
                  <Users className="w-4 h-4" />
                  {job.applications_count || 0} applications
                </span>
                {job.status === 'active' && (
                  <a
                    href={`/careers/${job.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-sm text-navy-500 hover:underline"
                  >
                    <Globe className="w-3.5 h-3.5" />
                    View Public Page
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
