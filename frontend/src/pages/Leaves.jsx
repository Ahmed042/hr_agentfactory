import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { leavesAPI, employeesAPI } from '../api/client';
import { useToast } from '../components/Toast';
import { CalendarDays, Plus, Check, X, Trash2 } from 'lucide-react';

export default function Leaves() {
  const queryClient = useQueryClient();
  const { addToast } = useToast();
  const [showForm, setShowForm] = useState(false);
  const [filter, setFilter] = useState('all');
  const [form, setForm] = useState({
    employee_id: '',
    leave_type: 'casual',
    start_date: '',
    end_date: '',
    reason: '',
  });

  const { data: leaves = [], isLoading } = useQuery({
    queryKey: ['leaves', filter],
    queryFn: () => leavesAPI.getAll(filter !== 'all' ? { status: filter } : {}).then(r => r.data),
  });

  const { data: employees = [] } = useQuery({
    queryKey: ['employees'],
    queryFn: () => employeesAPI.getAll().then(r => r.data),
  });

  const createMutation = useMutation({
    mutationFn: (data) => leavesAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leaves'] });
      setShowForm(false);
      setForm({ employee_id: '', leave_type: 'casual', start_date: '', end_date: '', reason: '' });
      addToast('Leave request submitted', 'success');
    },
    onError: (err) => addToast(err.response?.data?.detail || 'Failed to submit', 'error'),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, status }) => leavesAPI.update(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leaves'] });
      addToast('Leave request updated', 'success');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => leavesAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leaves'] });
      addToast('Leave request deleted', 'success');
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    createMutation.mutate({ ...form, employee_id: parseInt(form.employee_id) });
  };

  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
  };

  const typeColors = {
    sick: 'bg-orange-100 text-orange-800',
    casual: 'bg-blue-100 text-blue-800',
    annual: 'bg-purple-100 text-purple-800',
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Leave Management</h1>
          <p className="text-sm text-gray-500 mt-1">Manage employee leave requests</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-2 bg-navy-500 text-white px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-navy-600">
          <Plus className="w-4 h-4" /> New Leave Request
        </button>
      </div>

      {/* Create Form */}
      {showForm && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Submit Leave Request</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Employee</label>
              <select value={form.employee_id} onChange={e => setForm({ ...form, employee_id: e.target.value })} required className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                <option value="">Select Employee</option>
                {employees.map(emp => (
                  <option key={emp.id} value={emp.id}>{emp.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Leave Type</label>
              <select value={form.leave_type} onChange={e => setForm({ ...form, leave_type: e.target.value })} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                <option value="casual">Casual</option>
                <option value="sick">Sick</option>
                <option value="annual">Annual</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
              <input type="date" value={form.start_date} onChange={e => setForm({ ...form, start_date: e.target.value })} required className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
              <input type="date" value={form.end_date} onChange={e => setForm({ ...form, end_date: e.target.value })} required className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Reason</label>
              <textarea value={form.reason} onChange={e => setForm({ ...form, reason: e.target.value })} rows={2} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="Reason for leave..." />
            </div>
            <div className="md:col-span-2 flex gap-3">
              <button type="submit" disabled={createMutation.isPending} className="bg-navy-500 text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-navy-600">
                {createMutation.isPending ? 'Submitting...' : 'Submit Request'}
              </button>
              <button type="button" onClick={() => setShowForm(false)} className="border border-gray-300 text-gray-700 px-6 py-2 rounded-lg text-sm">Cancel</button>
            </div>
          </form>
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-2 mb-4">
        {['all', 'pending', 'approved', 'rejected'].map(f => (
          <button key={f} onClick={() => setFilter(f)} className={`px-4 py-1.5 rounded-lg text-sm font-medium capitalize ${filter === f ? 'bg-navy-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
            {f}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-400">Loading...</div>
        ) : leaves.length === 0 ? (
          <div className="p-8 text-center text-gray-400">
            <CalendarDays className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>No leave requests found</p>
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Employee</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Dates</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Days</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Reason</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {leaves.map(leave => (
                <tr key={leave.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{leave.employee_name}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${typeColors[leave.leave_type] || ''}`}>{leave.leave_type}</span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{leave.start_date} to {leave.end_date}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{leave.days}</td>
                  <td className="px-6 py-4 text-sm text-gray-600 max-w-xs truncate">{leave.reason || '-'}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${statusColors[leave.status] || ''}`}>{leave.status}</span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-1">
                      {leave.status === 'pending' && (
                        <>
                          <button onClick={() => updateMutation.mutate({ id: leave.id, status: 'approved' })} className="p-1.5 text-green-600 hover:bg-green-50 rounded" title="Approve">
                            <Check className="w-4 h-4" />
                          </button>
                          <button onClick={() => updateMutation.mutate({ id: leave.id, status: 'rejected' })} className="p-1.5 text-red-600 hover:bg-red-50 rounded" title="Reject">
                            <X className="w-4 h-4" />
                          </button>
                        </>
                      )}
                      <button onClick={() => deleteMutation.mutate(leave.id)} className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded" title="Delete">
                        <Trash2 className="w-4 h-4" />
                      </button>
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
