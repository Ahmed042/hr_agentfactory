import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { candidatesAPI, actionsAPI } from '../api/client';
import { Plus, Search, MoreHorizontal, X, User, CheckCircle, XCircle, Calendar, Send, UserCheck } from 'lucide-react';
import { useToast } from '../components/Toast';

const STAGE_STYLES = {
  applied: 'bg-blue-50 text-blue-700 border-blue-200',
  screening: 'bg-amber-50 text-amber-700 border-amber-200',
  technical: 'bg-purple-50 text-purple-700 border-purple-200',
  hr: 'bg-pink-50 text-pink-700 border-pink-200',
  offer: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  hired: 'bg-green-50 text-green-700 border-green-200',
  rejected: 'bg-red-50 text-red-700 border-red-200',
};

const SOURCES = ['linkedin', 'indeed', 'referral', 'website', 'direct', 'other'];

export default function Candidates() {
  const [showForm, setShowForm] = useState(false);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [formData, setFormData] = useState({
    email: '', job_role: '', name: '', phone: '', source: '',
    location: '', experience_years: '', expected_salary: '', skills: '',
  });
  const queryClient = useQueryClient();
  const toast = useToast();

  const { data: candidates = [], isLoading } = useQuery({
    queryKey: ['candidates', statusFilter, search],
    queryFn: () => candidatesAPI.getAll({ status: statusFilter || undefined, search: search || undefined }).then(res => res.data),
  });

  const createMutation = useMutation({
    mutationFn: (data) => candidatesAPI.create(data),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ['candidates'] });
      setShowForm(false);
      setFormData({ email: '', job_role: '', name: '', phone: '', source: '', location: '', experience_years: '', expected_salary: '', skills: '' });
      const emailSent = res.data?.email_sent;
      toast.success(emailSent ? 'Candidate added and welcome email sent!' : 'Candidate added successfully!');
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Failed to add candidate');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => candidatesAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates'] });
      toast.success('Candidate updated');
    },
    onError: () => toast.error('Failed to update candidate'),
  });

  const actionMutation = useMutation({
    mutationFn: ({ action, data }) => {
      if (action === 'approve') return actionsAPI.approve(data.candidate_id);
      if (action === 'reject') return actionsAPI.reject(data.candidate_id);
      if (action === 'interview') return actionsAPI.requestInterview(data);
      if (action === 'offer') return actionsAPI.sendOffer(data);
      if (action === 'hire') return actionsAPI.markHired(data.candidate_id);
    },
    onSuccess: (res, { action }) => {
      queryClient.invalidateQueries({ queryKey: ['candidates'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      const msgs = { approve: 'Candidate approved! Email sent.', reject: 'Candidate rejected. Email sent.', interview: 'Interview request sent!', offer: 'Offer letter sent!', hire: 'Candidate marked as hired! Onboarding email sent.' };
      toast.success(msgs[action] || 'Action completed');
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Action failed'),
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {
      ...formData,
      experience_years: formData.experience_years ? parseInt(formData.experience_years) : undefined,
      expected_salary: formData.expected_salary ? parseInt(formData.expected_salary) : undefined,
      skills: formData.skills ? formData.skills.split(',').map(s => s.trim()).filter(Boolean) : undefined,
    };
    Object.keys(payload).forEach(k => { if (payload[k] === '' || payload[k] === undefined) delete payload[k]; });
    createMutation.mutate(payload);
  };

  const handleStageChange = (candidateId, newStage) => {
    updateMutation.mutate({ id: candidateId, data: { status: newStage, stage: newStage } });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Candidates</h1>
          <p className="text-sm text-gray-500 mt-1">{candidates.length} total candidates in pipeline</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add Candidate
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search candidates..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input pl-9"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="input w-44"
        >
          <option value="">All Stages</option>
          <option value="applied">Applied</option>
          <option value="screening">Screening</option>
          <option value="technical">Technical</option>
          <option value="hr">HR Interview</option>
          <option value="offer">Offer</option>
          <option value="hired">Hired</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      {/* Add Candidate Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Add New Candidate</h3>
              <button onClick={() => setShowForm(false)} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                  <input type="text" value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} className="input" placeholder="John Doe" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
                  <input type="email" required value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} className="input" placeholder="john@example.com" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                  <input type="text" value={formData.phone} onChange={(e) => setFormData({...formData, phone: e.target.value})} className="input" placeholder="+92 300 1234567" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Job Role *</label>
                  <input type="text" required value={formData.job_role} onChange={(e) => setFormData({...formData, job_role: e.target.value})} className="input" placeholder="Full Stack Developer" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Source</label>
                  <select value={formData.source} onChange={(e) => setFormData({...formData, source: e.target.value})} className="input">
                    <option value="">Select source</option>
                    {SOURCES.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                  <input type="text" value={formData.location} onChange={(e) => setFormData({...formData, location: e.target.value})} className="input" placeholder="NYC, United States" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Experience (years)</label>
                  <input type="number" value={formData.experience_years} onChange={(e) => setFormData({...formData, experience_years: e.target.value})} className="input" placeholder="3" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Expected Salary (PKR)</label>
                  <input type="number" value={formData.expected_salary} onChange={(e) => setFormData({...formData, expected_salary: e.target.value})} className="input" placeholder="150000" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Skills (comma separated)</label>
                <input type="text" value={formData.skills} onChange={(e) => setFormData({...formData, skills: e.target.value})} className="input" placeholder="React, Python, AWS, Docker" />
              </div>
              <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
                <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
                <button type="submit" disabled={createMutation.isPending} className="btn-primary disabled:opacity-50">
                  {createMutation.isPending ? 'Adding...' : 'Add Candidate'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Candidates Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-gray-400">Loading candidates...</div>
        ) : candidates.length === 0 ? (
          <div className="p-12 text-center">
            <User className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">No candidates found</p>
            <p className="text-sm text-gray-400 mt-1">Add your first candidate to get started</p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Candidate</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Role</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Stage</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">AI Score</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Source</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {candidates.map((c) => (
                <tr key={c.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 bg-navy-500 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-white text-sm font-semibold">
                          {(c.name || c.email)?.[0]?.toUpperCase() || '?'}
                        </span>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{c.name || c.email.split('@')[0]}</p>
                        <p className="text-xs text-gray-400">{c.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-gray-700">{c.job_role || '-'}</span>
                  </td>
                  <td className="px-6 py-4">
                    <select
                      value={c.status || 'applied'}
                      onChange={(e) => handleStageChange(c.id, e.target.value)}
                      className={`text-xs font-semibold px-2 py-1 rounded-full border cursor-pointer ${STAGE_STYLES[c.status] || STAGE_STYLES.applied}`}
                    >
                      <option value="applied">Applied</option>
                      <option value="screening">Screening</option>
                      <option value="technical">Technical</option>
                      <option value="hr">HR Interview</option>
                      <option value="offer">Offer</option>
                      <option value="hired">Hired</option>
                      <option value="rejected">Rejected</option>
                    </select>
                  </td>
                  <td className="px-6 py-4">
                    {c.ai_score ? (
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-gray-200 rounded-full h-1.5">
                          <div
                            className="h-1.5 rounded-full"
                            style={{
                              width: `${c.ai_score}%`,
                              backgroundColor: c.ai_score >= 70 ? '#10B981' : c.ai_score >= 50 ? '#F59E0B' : '#EF4444',
                            }}
                          />
                        </div>
                        <span className="text-xs font-semibold text-gray-600">{c.ai_score}</span>
                      </div>
                    ) : (
                      <span className="text-xs text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-gray-500 capitalize">{c.source || '-'}</span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-1">
                      {(c.status === 'applied') && (
                        <>
                          <button onClick={() => actionMutation.mutate({ action: 'approve', data: { candidate_id: c.id } })} className="p-1.5 hover:bg-emerald-50 rounded-lg text-emerald-600" title="Approve">
                            <CheckCircle className="w-4 h-4" />
                          </button>
                          <button onClick={() => actionMutation.mutate({ action: 'reject', data: { candidate_id: c.id } })} className="p-1.5 hover:bg-red-50 rounded-lg text-red-500" title="Reject">
                            <XCircle className="w-4 h-4" />
                          </button>
                        </>
                      )}
                      {(c.status === 'screening') && (
                        <button onClick={() => actionMutation.mutate({ action: 'interview', data: { candidate_id: c.id, interview_type: 'technical' } })} className="p-1.5 hover:bg-blue-50 rounded-lg text-blue-600" title="Request Interview">
                          <Calendar className="w-4 h-4" />
                        </button>
                      )}
                      {(c.status === 'interview' || c.status === 'technical' || c.status === 'hr') && (
                        <button onClick={() => { const salary = prompt('Annual salary ($):'); const startDate = prompt('Start date (MM/DD/YYYY):'); if (salary && startDate) actionMutation.mutate({ action: 'offer', data: { candidate_id: c.id, salary: parseFloat(salary), start_date: startDate } }); }} className="p-1.5 hover:bg-purple-50 rounded-lg text-purple-600" title="Send Offer">
                          <Send className="w-4 h-4" />
                        </button>
                      )}
                      {c.status === 'offer' && (
                        <button onClick={() => actionMutation.mutate({ action: 'hire', data: { candidate_id: c.id } })} className="p-1.5 hover:bg-emerald-50 rounded-lg text-emerald-600" title="Mark Hired">
                          <UserCheck className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
