import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { templatesAPI } from '../api/client';
import { Plus, FileText, Edit3, Trash2, X, ToggleLeft, ToggleRight } from 'lucide-react';

const TYPE_STYLES = {
  offer_letter: 'bg-emerald-50 text-emerald-700',
  nda: 'bg-red-50 text-red-700',
  onboarding: 'bg-blue-50 text-blue-700',
  contract: 'bg-purple-50 text-purple-700',
  policy: 'bg-amber-50 text-amber-700',
};

const TYPE_LABELS = {
  offer_letter: 'Offer Letter',
  nda: 'NDA',
  onboarding: 'Onboarding',
  contract: 'Contract',
  policy: 'Policy',
};

export default function Templates() {
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [typeFilter, setTypeFilter] = useState('');
  const [formData, setFormData] = useState({
    name: '', template_type: 'offer_letter', description: '', content: '', is_active: true,
  });
  const queryClient = useQueryClient();

  const { data: templates = [], isLoading } = useQuery({
    queryKey: ['templates', typeFilter],
    queryFn: () => templatesAPI.getAll({ template_type: typeFilter || undefined }).then(res => res.data),
  });

  const createMutation = useMutation({
    mutationFn: (data) => editingId ? templatesAPI.update(editingId, data) : templatesAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
      setShowForm(false);
      setEditingId(null);
      setFormData({ name: '', template_type: 'offer_letter', description: '', content: '', is_active: true });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => templatesAPI.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['templates'] }),
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, is_active }) => templatesAPI.update(id, { is_active }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['templates'] }),
  });

  const handleEdit = (template) => {
    setEditingId(template.id);
    setFormData({
      name: template.name, template_type: template.template_type,
      description: template.description || '', content: template.content || '', is_active: template.is_active,
    });
    setShowForm(true);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  const PLACEHOLDER_HELP = '{{candidate_name}}, {{job_role}}, {{salary}}, {{start_date}}, {{company_name}}, {{department}}';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Document Templates</h1>
          <p className="text-sm text-gray-500 mt-1">Manage reusable document templates</p>
        </div>
        <button onClick={() => { setEditingId(null); setFormData({ name: '', template_type: 'offer_letter', description: '', content: '', is_active: true }); setShowForm(true); }} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Create Template
        </button>
      </div>

      {/* Type Filter */}
      <div className="flex gap-2 flex-wrap">
        {['', 'offer_letter', 'nda', 'onboarding', 'contract', 'policy'].map(t => (
          <button
            key={t}
            onClick={() => setTypeFilter(t)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              typeFilter === t ? 'bg-navy-500 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
            }`}
          >
            {t ? (TYPE_LABELS[t] || t) : 'All'}
          </button>
        ))}
      </div>

      {/* Create/Edit Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">{editingId ? 'Edit Template' : 'Create Template'}</h3>
              <button onClick={() => { setShowForm(false); setEditingId(null); }} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Template Name *</label>
                  <input type="text" required value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} className="input" placeholder="Standard Offer Letter" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                  <select value={formData.template_type} onChange={(e) => setFormData({...formData, template_type: e.target.value})} className="input">
                    <option value="offer_letter">Offer Letter</option>
                    <option value="nda">NDA</option>
                    <option value="onboarding">Onboarding</option>
                    <option value="contract">Contract</option>
                    <option value="policy">Policy</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <input type="text" value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} className="input" placeholder="Brief description of template" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
                <p className="text-xs text-gray-400 mb-2">Available placeholders: {PLACEHOLDER_HELP}</p>
                <textarea
                  rows={12}
                  value={formData.content}
                  onChange={(e) => setFormData({...formData, content: e.target.value})}
                  className="input font-mono text-sm"
                  placeholder={`Dear {{candidate_name}},\n\nWe are pleased to offer you the position of {{job_role}}...\n\nSalary: PKR {{salary}}\nStart Date: {{start_date}}`}
                />
              </div>
              <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
                <button type="button" onClick={() => { setShowForm(false); setEditingId(null); }} className="btn-secondary">Cancel</button>
                <button type="submit" disabled={createMutation.isPending} className="btn-primary disabled:opacity-50">
                  {createMutation.isPending ? 'Saving...' : (editingId ? 'Update Template' : 'Create Template')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Templates Grid */}
      {isLoading ? (
        <div className="text-center py-12 text-gray-400">Loading templates...</div>
      ) : templates.length === 0 ? (
        <div className="card p-12 text-center">
          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">No templates yet</p>
          <p className="text-sm text-gray-400 mt-1">Create templates for offer letters, NDAs, and more</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {templates.map((template) => (
            <div key={template.id} className={`card p-6 ${!template.is_active ? 'opacity-60' : ''}`}>
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-base font-semibold text-gray-900">{template.name}</h3>
                  <span className={`badge mt-1 ${TYPE_STYLES[template.template_type] || 'bg-gray-100 text-gray-600'}`}>
                    {TYPE_LABELS[template.template_type] || template.template_type}
                  </span>
                </div>
                <button
                  onClick={() => toggleMutation.mutate({ id: template.id, is_active: !template.is_active })}
                  className="text-gray-400 hover:text-gray-600"
                  title={template.is_active ? 'Deactivate' : 'Activate'}
                >
                  {template.is_active ? <ToggleRight className="w-6 h-6 text-emerald-500" /> : <ToggleLeft className="w-6 h-6" />}
                </button>
              </div>

              {template.description && (
                <p className="text-sm text-gray-500 mb-3">{template.description}</p>
              )}

              {template.content && (
                <div className="bg-gray-50 rounded-lg p-3 mb-4 max-h-24 overflow-hidden">
                  <p className="text-xs text-gray-500 font-mono whitespace-pre-wrap">{template.content.substring(0, 150)}...</p>
                </div>
              )}

              <div className="flex items-center gap-2 pt-3 border-t border-gray-100">
                <button onClick={() => handleEdit(template)} className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg">
                  <Edit3 className="w-3.5 h-3.5" />Edit
                </button>
                <button onClick={() => { if (confirm('Delete this template?')) deleteMutation.mutate(template.id); }} className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg">
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
