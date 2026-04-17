import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { interviewsAPI, candidatesAPI } from '../api/client';
import { Plus, Calendar, Clock, Video, User, X } from 'lucide-react';

const RESULT_STYLES = {
  pending: 'bg-blue-50 text-blue-700 border-blue-200',
  passed: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  failed: 'bg-red-50 text-red-700 border-red-200',
  cancelled: 'bg-gray-100 text-gray-600 border-gray-200',
  no_show: 'bg-amber-50 text-amber-700 border-amber-200',
};

const TYPE_LABELS = {
  screening: 'Screening',
  technical: 'Technical',
  hr: 'HR',
  cultural: 'Cultural Fit',
  final: 'Final',
};

export default function Interviews() {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    candidate_id: '', interview_round: 1, interview_type: 'technical',
    interviewer_name: '', interviewer_email: '', scheduled_at: '',
    duration_minutes: 45, meeting_link: '', location: '',
  });
  const queryClient = useQueryClient();

  const { data: interviews = [], isLoading } = useQuery({
    queryKey: ['interviews'],
    queryFn: () => interviewsAPI.getAll().then(res => res.data),
  });

  const { data: candidates = [] } = useQuery({
    queryKey: ['candidates'],
    queryFn: () => candidatesAPI.getAll().then(res => res.data),
  });

  const createMutation = useMutation({
    mutationFn: (data) => interviewsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['interviews'] });
      queryClient.invalidateQueries({ queryKey: ['candidates'] });
      setShowForm(false);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => interviewsAPI.update(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['interviews'] }),
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {
      ...formData,
      candidate_id: parseInt(formData.candidate_id),
      interview_round: parseInt(formData.interview_round),
      duration_minutes: parseInt(formData.duration_minutes),
      scheduled_at: new Date(formData.scheduled_at).toISOString(),
    };
    Object.keys(payload).forEach(k => { if (payload[k] === '') delete payload[k]; });
    createMutation.mutate(payload);
  };

  const getCandidateName = (id) => {
    const c = candidates.find(c => c.id === id);
    return c ? (c.name || c.email.split('@')[0]) : `#${id}`;
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Interviews</h1>
          <p className="text-sm text-gray-500 mt-1">{interviews.length} scheduled interviews</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Schedule Interview
        </button>
      </div>

      {/* Schedule Interview Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Schedule Interview</h3>
              <button onClick={() => setShowForm(false)} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Candidate *</label>
                <select required value={formData.candidate_id} onChange={(e) => setFormData({...formData, candidate_id: e.target.value})} className="input">
                  <option value="">Select candidate</option>
                  {candidates.map(c => (
                    <option key={c.id} value={c.id}>{c.name || c.email} - {c.job_role}</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Interview Type</label>
                  <select value={formData.interview_type} onChange={(e) => setFormData({...formData, interview_type: e.target.value})} className="input">
                    <option value="screening">Screening</option>
                    <option value="technical">Technical</option>
                    <option value="hr">HR</option>
                    <option value="cultural">Cultural Fit</option>
                    <option value="final">Final</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Round</label>
                  <input type="number" min="1" value={formData.interview_round} onChange={(e) => setFormData({...formData, interview_round: e.target.value})} className="input" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Date & Time *</label>
                  <input type="datetime-local" required value={formData.scheduled_at} onChange={(e) => setFormData({...formData, scheduled_at: e.target.value})} className="input" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Duration (min)</label>
                  <input type="number" value={formData.duration_minutes} onChange={(e) => setFormData({...formData, duration_minutes: e.target.value})} className="input" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Interviewer Name</label>
                  <input type="text" value={formData.interviewer_name} onChange={(e) => setFormData({...formData, interviewer_name: e.target.value})} className="input" placeholder="John Doe" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Interviewer Email</label>
                  <input type="email" value={formData.interviewer_email} onChange={(e) => setFormData({...formData, interviewer_email: e.target.value})} className="input" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Meeting Link</label>
                <input type="url" value={formData.meeting_link} onChange={(e) => setFormData({...formData, meeting_link: e.target.value})} className="input" placeholder="https://meet.google.com/..." />
              </div>
              <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
                <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
                <button type="submit" disabled={createMutation.isPending} className="btn-primary disabled:opacity-50">
                  {createMutation.isPending ? 'Scheduling...' : 'Schedule Interview'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Interviews Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-gray-400">Loading interviews...</div>
        ) : interviews.length === 0 ? (
          <div className="p-12 text-center">
            <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">No interviews scheduled</p>
            <p className="text-sm text-gray-400 mt-1">Schedule an interview to get started</p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Candidate</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Type</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Round</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Date & Time</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Interviewer</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Meeting</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {interviews.map((interview) => (
                <tr key={interview.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-gray-400" />
                      <span className="text-sm font-medium text-gray-900">{getCandidateName(interview.candidate_id)}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-gray-700 capitalize">{TYPE_LABELS[interview.interview_type] || interview.interview_type}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-gray-600">Round {interview.interview_round || 1}</span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-gray-400" />
                      <span className="text-sm text-gray-700">{formatDate(interview.scheduled_at)}</span>
                    </div>
                    <span className="text-xs text-gray-400 ml-5">{interview.duration_minutes || 45} min</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-gray-700">{interview.interviewer_name || '-'}</span>
                  </td>
                  <td className="px-6 py-4">
                    {interview.meeting_link ? (
                      <a href={interview.meeting_link} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-sm text-navy-500 hover:underline">
                        <Video className="w-3.5 h-3.5" />Join
                      </a>
                    ) : (
                      <span className="text-xs text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <select
                      value={interview.result || 'pending'}
                      onChange={(e) => updateMutation.mutate({ id: interview.id, data: { result: e.target.value } })}
                      className={`badge border cursor-pointer ${RESULT_STYLES[interview.result] || RESULT_STYLES.pending}`}
                    >
                      <option value="pending">Pending</option>
                      <option value="passed">Passed</option>
                      <option value="failed">Failed</option>
                      <option value="cancelled">Cancelled</option>
                      <option value="no_show">No Show</option>
                    </select>
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
