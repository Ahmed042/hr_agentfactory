import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { publicAPI } from '../api/client';
import { Link } from 'react-router-dom';
import { MapPin, Briefcase, DollarSign, Clock, Globe, Search, Zap, ChevronRight } from 'lucide-react';

export default function Careers() {
  const [search, setSearch] = useState('');
  const [department, setDepartment] = useState('');

  const { data: jobs = [], isLoading } = useQuery({
    queryKey: ['public-careers', search, department],
    queryFn: () => publicAPI.getCareers({ search: search || undefined, department: department || undefined }).then(res => res.data),
  });

  const departments = [...new Set(jobs.map(j => j.department).filter(Boolean))];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero */}
      <div className="bg-navy-500 text-white">
        <div className="max-w-5xl mx-auto px-6 py-16">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
              <Zap className="w-6 h-6" />
            </div>
            <span className="text-lg font-bold">HR AgentFactory</span>
          </div>
          <h1 className="text-4xl font-bold mb-4">Join Our Team</h1>
          <p className="text-white/70 text-lg max-w-2xl">
            We're building the future of HR technology. Find your next opportunity and grow with us.
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="max-w-5xl mx-auto px-6 -mt-6">
        <div className="bg-white rounded-xl shadow-lg p-4 flex items-center gap-4">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search positions..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-navy-500"
            />
          </div>
          {departments.length > 0 && (
            <select
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              className="px-4 py-2.5 border border-gray-200 rounded-lg text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-navy-500"
            >
              <option value="">All Departments</option>
              {departments.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          )}
        </div>
      </div>

      {/* Job Listings */}
      <div className="max-w-5xl mx-auto px-6 py-10">
        <p className="text-sm text-gray-500 mb-6">{jobs.length} open position{jobs.length !== 1 ? 's' : ''}</p>

        {isLoading ? (
          <div className="text-center py-16 text-gray-400">Loading positions...</div>
        ) : jobs.length === 0 ? (
          <div className="text-center py-16">
            <Briefcase className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">No open positions right now</p>
            <p className="text-sm text-gray-400 mt-1">Check back soon for new opportunities</p>
          </div>
        ) : (
          <div className="space-y-4">
            {jobs.map((job) => (
              <Link
                key={job.id}
                to={`/careers/${job.id}`}
                className="block bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md hover:border-navy-500/30 transition-all group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 group-hover:text-navy-500 transition-colors">
                      {job.title}
                    </h3>
                    <div className="flex flex-wrap items-center gap-4 mt-2 text-sm text-gray-500">
                      {job.department && (
                        <span className="flex items-center gap-1"><Briefcase className="w-3.5 h-3.5" />{job.department}</span>
                      )}
                      {job.location && (
                        <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" />{job.location}</span>
                      )}
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5" />
                        {(job.employment_type || 'full_time').replace('_', ' ')}
                      </span>
                      {job.is_remote && (
                        <span className="flex items-center gap-1 text-blue-600"><Globe className="w-3.5 h-3.5" />Remote</span>
                      )}
                    </div>
                    {(job.salary_min || job.salary_max) && (
                      <div className="flex items-center gap-1 mt-2 text-sm text-gray-600">
                        <DollarSign className="w-3.5 h-3.5" />
                        ${job.salary_min?.toLocaleString()} - ${job.salary_max?.toLocaleString()} /year
                      </div>
                    )}
                    {job.skills_required?.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-3">
                        {job.skills_required.slice(0, 5).map((s, i) => (
                          <span key={i} className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">{s}</span>
                        ))}
                      </div>
                    )}
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-300 group-hover:text-navy-500 mt-1 flex-shrink-0 transition-colors" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 bg-white">
        <div className="max-w-5xl mx-auto px-6 py-8 text-center text-sm text-gray-400">
          Powered by HR AgentFactory
        </div>
      </div>
    </div>
  );
}
