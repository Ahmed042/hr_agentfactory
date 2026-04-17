import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { departmentsAPI } from '../api/client';
import { useToast } from '../components/Toast';
import { Plus, Building2, Users, DollarSign, Edit3, Trash2, X } from 'lucide-react';

export default function Departments() {
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({ name: '', description: '', budget: '', head_name: '' });
  const queryClient = useQueryClient();
  const toast = useToast();

  const { data: departments = [], isLoading } = useQuery({
    queryKey: ['departments'],
    queryFn: () => departmentsAPI.getAll().then(res => res.data),
  });

  const saveMutation = useMutation({
    mutationFn: (data) => editingId ? departmentsAPI.update(editingId, data) : departmentsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] });
      setShowForm(false);
      setEditingId(null);
      setFormData({ name: '', description: '', budget: '', head_name: '' });
      toast.success(editingId ? 'Department updated' : 'Department created');
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Failed to save department'),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => departmentsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] });
      toast.success('Department deleted');
    },
  });

  const handleEdit = (dept) => {
    setEditingId(dept.id);
    setFormData({ name: dept.name, description: dept.description || '', budget: dept.budget || '', head_name: dept.head_name || '' });
    setShowForm(true);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = { ...formData, budget: formData.budget ? parseFloat(formData.budget) : undefined };
    Object.keys(payload).forEach(k => { if (payload[k] === '' || payload[k] === undefined) delete payload[k]; });
    saveMutation.mutate(payload);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Departments</h1>
          <p className="text-sm text-gray-500 mt-1">{departments.length} departments</p>
        </div>
        <button onClick={() => { setEditingId(null); setFormData({ name: '', description: '', budget: '', head_name: '' }); setShowForm(true); }} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />Add Department
        </button>
      </div>

      {/* Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">{editingId ? 'Edit Department' : 'Add Department'}</h3>
              <button onClick={() => { setShowForm(false); setEditingId(null); }} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Department Name *</label>
                <input type="text" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="input" placeholder="Engineering" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea rows={2} value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} className="input" placeholder="Department overview..." />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Annual Budget ($)</label>
                  <input type="number" value={formData.budget} onChange={e => setFormData({...formData, budget: e.target.value})} className="input" placeholder="500000" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Department Head</label>
                  <input type="text" value={formData.head_name} onChange={e => setFormData({...formData, head_name: e.target.value})} className="input" placeholder="Jane Smith" />
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
                <button type="button" onClick={() => { setShowForm(false); setEditingId(null); }} className="btn-secondary">Cancel</button>
                <button type="submit" disabled={saveMutation.isPending} className="btn-primary disabled:opacity-50">
                  {saveMutation.isPending ? 'Saving...' : (editingId ? 'Update' : 'Create')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Cards Grid */}
      {isLoading ? (
        <div className="text-center py-12 text-gray-400">Loading...</div>
      ) : departments.length === 0 ? (
        <div className="card p-12 text-center">
          <Building2 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">No departments yet</p>
          <p className="text-sm text-gray-400 mt-1">Create your first department</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {departments.map((dept) => (
            <div key={dept.id} className="card p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-navy-50 text-navy-500 rounded-lg flex items-center justify-center">
                    <Building2 className="w-5 h-5" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">{dept.name}</h3>
                </div>
              </div>
              {dept.description && <p className="text-sm text-gray-500 mb-3">{dept.description}</p>}
              <div className="space-y-2 mb-4">
                {dept.budget && (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <DollarSign className="w-4 h-4 text-gray-400" />Budget: ${Number(dept.budget).toLocaleString()}
                  </div>
                )}
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Users className="w-4 h-4 text-gray-400" />{dept.employee_count || 0} employees
                </div>
                {dept.head_name && (
                  <div className="text-sm text-gray-600">Head: {dept.head_name}</div>
                )}
              </div>
              <div className="flex gap-2 pt-3 border-t border-gray-100">
                <button onClick={() => handleEdit(dept)} className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg">
                  <Edit3 className="w-3.5 h-3.5" />Edit
                </button>
                <button onClick={() => { if(confirm('Delete department?')) deleteMutation.mutate(dept.id); }} className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg">
                  <Trash2 className="w-3.5 h-3.5" />Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
