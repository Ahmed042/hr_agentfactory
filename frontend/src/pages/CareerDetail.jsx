import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { publicAPI } from '../api/client';
import { ArrowLeft, MapPin, Briefcase, DollarSign, Clock, Globe, Zap, CheckCircle, Send } from 'lucide-react';

export default function CareerDetail() {
  const { jobId } = useParams();
  const [showForm, setShowForm] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    name: '', email: '', phone: '', resume_text: '', cover_letter: '',
    location: '', experience_years: '', expected_salary: '', skills: '',
  });

  const { data: job, isLoading } = useQuery({
    queryKey: ['public-job', jobId],
    queryFn: () => publicAPI.getJob(jobId).then(res => res.data),
  });

  const applyMutation = useMutation({
    mutationFn: (data) => publicAPI.applyToJob(jobId, data),
    onSuccess: () => setSubmitted(true),
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {
      job_id: parseInt(jobId),
      ...formData,
      experience_years: formData.experience_years ? parseInt(formData.experience_years) : undefined,
      expected_salary: formData.expected_salary ? parseInt(formData.expected_salary) : undefined,
      skills: formData.skills ? formData.skills.split(',').map(s => s.trim()).filter(Boolean) : undefined,
    };
    Object.keys(payload).forEach(k => { if (payload[k] === '' || payload[k] === undefined) delete payload[k]; });
    applyMutation.mutate(payload);
  };

  if (isLoading) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">Loading...</div>;
  if (!job) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-500">Job not found</div>;

  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-4">
          <CheckCircle className="w-16 h-16 text-emerald-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Application Submitted!</h2>
          <p className="text-gray-500 mb-6">Thank you for applying. Check your email for a confirmation. We'll review your application and get back to you within 3-5 business days.</p>
          <Link to="/careers" className="btn-primary inline-block">View More Jobs</Link>
        </div>
      </div>
    );
  }

  const renderSection = (title, content) => {
    if (!content) return null;
    return (
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">{title}</h3>
        <div className="text-gray-600 text-sm leading-relaxed whitespace-pre-line">{content}</div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-navy-500 text-white">
        <div className="max-w-4xl mx-auto px-6 py-8">
          <Link to="/careers" className="flex items-center gap-2 text-white/70 hover:text-white text-sm mb-4">
            <ArrowLeft className="w-4 h-4" />Back to all positions
          </Link>
          <h1 className="text-3xl font-bold mb-3">{job.title}</h1>
          <div className="flex flex-wrap items-center gap-4 text-sm text-white/70">
            {job.department && <span className="flex items-center gap-1"><Briefcase className="w-4 h-4" />{job.department}</span>}
            {job.location && <span className="flex items-center gap-1"><MapPin className="w-4 h-4" />{job.location}</span>}
            <span className="flex items-center gap-1"><Clock className="w-4 h-4" />{(job.employment_type || 'full_time').replace('_', ' ')}</span>
            {job.is_remote && <span className="flex items-center gap-1"><Globe className="w-4 h-4" />Remote</span>}
          </div>
          {(job.salary_min || job.salary_max) && (
            <div className="flex items-center gap-1 mt-2 text-white/80">
              <DollarSign className="w-4 h-4" />${job.salary_min?.toLocaleString()} - ${job.salary_max?.toLocaleString()} /year
            </div>
          )}
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-10">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Job Details */}
          <div className="lg:col-span-2">
            {renderSection('About the Role', job.description)}
            {renderSection('Key Responsibilities', job.responsibilities)}
            {renderSection('Required Qualifications', job.required_qualifications)}
            {renderSection('Preferred Qualifications', job.preferred_qualifications)}
            {renderSection('Benefits', job.benefits)}

            {job.skills_required?.length > 0 && (
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Skills</h3>
                <div className="flex flex-wrap gap-2">
                  {job.skills_required.map((s, i) => (
                    <span key={i} className="px-3 py-1 bg-navy-50 text-navy-500 rounded-full text-sm font-medium">{s}</span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Apply Sidebar */}
          <div>
            <div className="bg-white rounded-xl border border-gray-200 p-6 sticky top-6">
              {!showForm ? (
                <>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Interested?</h3>
                  <p className="text-sm text-gray-500 mb-4">Apply now and our AI will review your application immediately.</p>
                  <button onClick={() => setShowForm(true)} className="w-full btn-primary py-3 flex items-center justify-center gap-2">
                    <Send className="w-4 h-4" />Apply Now
                  </button>
                </>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-3">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Apply</h3>
                  <input type="text" required placeholder="Full Name *" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="input text-sm" />
                  <input type="email" required placeholder="Email *" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="input text-sm" />
                  <input type="tel" placeholder="Phone" value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} className="input text-sm" />
                  <input type="text" placeholder="Location (e.g., New York, NY)" value={formData.location} onChange={e => setFormData({...formData, location: e.target.value})} className="input text-sm" />
                  <input type="number" placeholder="Years of experience" value={formData.experience_years} onChange={e => setFormData({...formData, experience_years: e.target.value})} className="input text-sm" />
                  <input type="number" placeholder="Expected salary ($/year)" value={formData.expected_salary} onChange={e => setFormData({...formData, expected_salary: e.target.value})} className="input text-sm" />
                  <input type="text" placeholder="Skills (comma separated)" value={formData.skills} onChange={e => setFormData({...formData, skills: e.target.value})} className="input text-sm" />
                  <textarea rows={4} placeholder="Paste your resume text here..." value={formData.resume_text} onChange={e => setFormData({...formData, resume_text: e.target.value})} className="input text-sm" />
                  <textarea rows={3} placeholder="Cover letter (optional)" value={formData.cover_letter} onChange={e => setFormData({...formData, cover_letter: e.target.value})} className="input text-sm" />
                  {applyMutation.isError && (
                    <p className="text-xs text-red-600">{applyMutation.error?.response?.data?.detail || 'Application failed. Try again.'}</p>
                  )}
                  <button type="submit" disabled={applyMutation.isPending} className="w-full btn-primary py-2.5 disabled:opacity-50">
                    {applyMutation.isPending ? 'Submitting...' : 'Submit Application'}
                  </button>
                  <button type="button" onClick={() => setShowForm(false)} className="w-full btn-secondary py-2 text-sm">Cancel</button>
                </form>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
