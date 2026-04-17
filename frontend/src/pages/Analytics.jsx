import { useQuery } from '@tanstack/react-query';
import { analyticsAPI } from '../api/client';
import { BarChart3, TrendingUp, Users, Clock } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';

const COLORS = ['#3B82F6', '#F59E0B', '#8B5CF6', '#EC4899', '#10B981', '#059669', '#EF4444'];

export default function Analytics() {
  const { data: stats } = useQuery({
    queryKey: ['analytics-dashboard'],
    queryFn: () => analyticsAPI.getDashboard().then(res => res.data),
  });

  const { data: funnel } = useQuery({
    queryKey: ['analytics-funnel'],
    queryFn: () => analyticsAPI.getHiringFunnel().then(res => res.data),
  });

  const pipelineData = stats?.pipeline
    ? Object.entries(stats.pipeline)
        .filter(([_, count]) => count > 0)
        .map(([stage, count]) => ({
          name: stage.charAt(0).toUpperCase() + stage.slice(1),
          value: count,
        }))
    : [];

  const summaryCards = [
    { label: 'Total Candidates', value: stats?.total_candidates || 0, icon: Users, color: 'text-blue-600 bg-blue-50' },
    { label: 'Active Pipeline', value: stats?.active_candidates || 0, icon: TrendingUp, color: 'text-emerald-600 bg-emerald-50' },
    { label: 'AI Actions', value: stats?.ai_actions || 0, icon: BarChart3, color: 'text-purple-600 bg-purple-50' },
    { label: 'Open Positions', value: stats?.active_jobs || 0, icon: Clock, color: 'text-amber-600 bg-amber-50' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-sm text-gray-500 mt-1">Recruitment metrics and insights</p>
        </div>
        <select className="input w-40">
          <option>Last 30 days</option>
          <option>Last 90 days</option>
          <option>This year</option>
          <option>All time</option>
        </select>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {summaryCards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.label} className="card p-6">
              <div className="flex items-center gap-3 mb-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${card.color}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <span className="text-sm font-medium text-gray-500">{card.label}</span>
              </div>
              <p className="text-3xl font-bold text-gray-900">{card.value}</p>
            </div>
          );
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hiring Funnel */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Hiring Funnel</h3>
          {funnel?.funnel?.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={funnel.funnel} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis type="number" tick={{ fontSize: 12, fill: '#64748B' }} />
                <YAxis dataKey="stage" type="category" tick={{ fontSize: 12, fill: '#64748B' }} width={90} />
                <Tooltip contentStyle={{ background: '#fff', border: '1px solid #E5E7EB', borderRadius: '8px' }} />
                <Bar dataKey="count" fill="#1E3A8A" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-400 text-sm">
              No data available yet
            </div>
          )}
        </div>

        {/* Pipeline Breakdown */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Pipeline Breakdown</h3>
          {pipelineData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pipelineData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={3}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {pipelineData.map((_, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#fff', border: '1px solid #E5E7EB', borderRadius: '8px' }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-400 text-sm">
              No pipeline data yet
            </div>
          )}
        </div>
      </div>

      {/* Pipeline Table */}
      {stats?.pipeline && (
        <div className="card overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <h3 className="text-sm font-semibold text-gray-700">Pipeline Stage Details</h3>
          </div>
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Stage</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Count</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Percentage</th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Bar</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {Object.entries(stats.pipeline).map(([stage, count], i) => {
                const total = stats.total_candidates || 1;
                const pct = Math.round((count / total) * 100);
                return (
                  <tr key={stage} className="hover:bg-gray-50">
                    <td className="px-6 py-3 text-sm font-medium text-gray-900 capitalize">{stage}</td>
                    <td className="px-6 py-3 text-sm text-gray-600">{count}</td>
                    <td className="px-6 py-3 text-sm text-gray-600">{pct}%</td>
                    <td className="px-6 py-3">
                      <div className="w-full max-w-[200px] bg-gray-200 rounded-full h-2">
                        <div className="h-2 rounded-full" style={{ width: `${pct}%`, backgroundColor: COLORS[i % COLORS.length] }} />
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
