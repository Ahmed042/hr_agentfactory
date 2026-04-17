import { useQuery } from '@tanstack/react-query';
import { analyticsAPI } from '../api/client';
import { Users, UserCheck, Calendar, Briefcase, TrendingUp, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const STAGE_COLORS = {
  applied: '#3B82F6',
  screening: '#F59E0B',
  technical: '#8B5CF6',
  hr: '#EC4899',
  offer: '#10B981',
  hired: '#059669',
  rejected: '#EF4444',
};

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => analyticsAPI.getDashboard().then(res => res.data),
  });

  const { data: funnel } = useQuery({
    queryKey: ['hiring-funnel'],
    queryFn: () => analyticsAPI.getHiringFunnel().then(res => res.data),
  });

  const { data: activity = [] } = useQuery({
    queryKey: ['recent-activity'],
    queryFn: () => analyticsAPI.getActivity(10).then(res => res.data),
  });

  const pipelineData = stats?.pipeline
    ? Object.entries(stats.pipeline).map(([stage, count]) => ({
        stage: stage.charAt(0).toUpperCase() + stage.slice(1),
        count,
        fill: STAGE_COLORS[stage] || '#64748B',
      }))
    : [];

  const statCards = [
    { name: 'Active Candidates', value: stats?.active_candidates || 0, icon: Users, color: 'bg-blue-50 text-blue-600', border: 'border-blue-200' },
    { name: 'Total Employees', value: stats?.total_employees || 0, icon: UserCheck, color: 'bg-emerald-50 text-emerald-600', border: 'border-emerald-200' },
    { name: 'Interviews Scheduled', value: stats?.interviews_scheduled || 0, icon: Calendar, color: 'bg-amber-50 text-amber-600', border: 'border-amber-200' },
    { name: 'Active Job Postings', value: stats?.active_jobs || 0, icon: Briefcase, color: 'bg-purple-50 text-purple-600', border: 'border-purple-200' },
  ];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-24 mb-4" />
              <div className="h-8 bg-gray-200 rounded w-16" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Overview of your recruitment pipeline</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className={`card p-6 border ${stat.border}`}>
              <div className="flex items-center justify-between mb-4">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${stat.color}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <TrendingUp className="w-4 h-4 text-emerald-500" />
              </div>
              <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
              <div className="text-sm text-gray-500 mt-1">{stat.name}</div>
            </div>
          );
        })}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pipeline Chart */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Hiring Pipeline</h3>
          {pipelineData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={pipelineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="stage" tick={{ fontSize: 12, fill: '#64748B' }} />
                <YAxis tick={{ fontSize: 12, fill: '#64748B' }} />
                <Tooltip
                  contentStyle={{ background: '#fff', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '13px' }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {pipelineData.map((entry, index) => (
                    <Cell key={index} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-400">
              No pipeline data yet
            </div>
          )}
        </div>

        {/* Hiring Funnel */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Hiring Funnel</h3>
          {funnel?.funnel?.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={funnel.funnel} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis type="number" tick={{ fontSize: 12, fill: '#64748B' }} />
                <YAxis dataKey="stage" type="category" tick={{ fontSize: 12, fill: '#64748B' }} width={90} />
                <Tooltip
                  contentStyle={{ background: '#fff', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '13px' }}
                />
                <Bar dataKey="count" fill="#1E3A8A" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-400">
              No funnel data yet
            </div>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card p-6">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="w-5 h-5 text-navy-500" />
          <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
        </div>
        {activity.length > 0 ? (
          <div className="space-y-3">
            {activity.map((item, i) => (
              <div key={item.id || i} className="flex items-start gap-3 py-3 border-b border-gray-100 last:border-0">
                <div className="w-2 h-2 bg-navy-500 rounded-full mt-2 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">{item.description || item.action}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-gray-400">{item.entity_type}</span>
                    <span className="text-xs text-gray-300">·</span>
                    <span className="text-xs text-gray-400">{item.actor || 'System'}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-400 py-8 text-center">No recent activity. Add candidates to get started.</p>
        )}
      </div>
    </div>
  );
}
