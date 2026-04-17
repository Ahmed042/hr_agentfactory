import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { payrollAPI } from '../api/client';
import { useToast } from '../components/Toast';
import { DollarSign, Calendar, FileText, Zap } from 'lucide-react';

export default function Payroll() {
  const [month, setMonth] = useState('');
  const [genMonth, setGenMonth] = useState(new Date().toISOString().slice(0, 7));
  const queryClient = useQueryClient();
  const toast = useToast();

  const { data: salaries = [], isLoading } = useQuery({
    queryKey: ['payroll', month],
    queryFn: () => payrollAPI.getAll(month || undefined).then(res => res.data),
  });

  const generateMutation = useMutation({
    mutationFn: (data) => payrollAPI.generate(data),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ['payroll'] });
      const count = res.data?.generated || 0;
      toast.success(count > 0 ? `Generated ${count} payslip(s)` : 'Payslips already exist for this month');
    },
    onError: () => toast.error('Failed to generate payroll'),
  });

  const sendMutation = useMutation({
    mutationFn: (m) => payrollAPI.sendPayslips(m),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ['payroll'] });
      toast.success(`Payslips emailed to ${res.data?.sent || 0} employee(s)!`);
    },
    onError: () => toast.error('Failed to send payslips'),
  });

  const totalGross = salaries.reduce((s, r) => s + (r.gross_salary || 0), 0);
  const totalNet = salaries.reduce((s, r) => s + (r.net_salary || 0), 0);
  const totalDeductions = salaries.reduce((s, r) => s + (r.total_deductions || 0), 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Payroll</h1>
          <p className="text-sm text-gray-500 mt-1">US payroll with tax calculations</p>
        </div>
        <div className="flex items-center gap-3">
          <input type="month" value={genMonth} onChange={e => setGenMonth(e.target.value)} className="input w-40" />
          <button
            onClick={() => generateMutation.mutate({ month: genMonth })}
            disabled={generateMutation.isPending}
            className="btn-primary flex items-center gap-2 disabled:opacity-50"
          >
            <Zap className="w-4 h-4" />
            {generateMutation.isPending ? 'Generating...' : 'Generate Payroll'}
          </button>
          {salaries.length > 0 && (
            <button
              onClick={() => sendMutation.mutate(genMonth)}
              disabled={sendMutation.isPending}
              className="btn-success flex items-center gap-2 disabled:opacity-50"
            >
              <FileText className="w-4 h-4" />
              {sendMutation.isPending ? 'Emailing...' : 'Email Payslips'}
            </button>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-blue-50 text-blue-600 rounded-lg flex items-center justify-center"><DollarSign className="w-5 h-5" /></div>
            <span className="text-sm text-gray-500">Total Gross</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">${totalGross.toLocaleString(undefined, {minimumFractionDigits: 2})}</p>
        </div>
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-red-50 text-red-600 rounded-lg flex items-center justify-center"><FileText className="w-5 h-5" /></div>
            <span className="text-sm text-gray-500">Total Deductions</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">${totalDeductions.toLocaleString(undefined, {minimumFractionDigits: 2})}</p>
        </div>
        <div className="card p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-emerald-50 text-emerald-600 rounded-lg flex items-center justify-center"><DollarSign className="w-5 h-5" /></div>
            <span className="text-sm text-gray-500">Total Net Pay</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">${totalNet.toLocaleString(undefined, {minimumFractionDigits: 2})}</p>
        </div>
      </div>

      {/* Filter */}
      <div className="flex items-center gap-3">
        <Calendar className="w-4 h-4 text-gray-400" />
        <input type="month" value={month} onChange={e => setMonth(e.target.value)} className="input w-44" placeholder="Filter by month" />
        {month && <button onClick={() => setMonth('')} className="text-sm text-gray-500 hover:text-gray-700">Clear</button>}
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-gray-400">Loading payroll...</div>
        ) : salaries.length === 0 ? (
          <div className="p-12 text-center">
            <DollarSign className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">No payroll records</p>
            <p className="text-sm text-gray-400 mt-1">Add employees and click "Generate Payroll"</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Employee</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Month</th>
                  <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Gross</th>
                  <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Federal</th>
                  <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">State</th>
                  <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">SS</th>
                  <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Medicare</th>
                  <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">401(k)</th>
                  <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Health</th>
                  <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Net</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {salaries.map((s) => (
                  <tr key={s.id} className="hover:bg-gray-50 text-sm">
                    <td className="px-4 py-3">
                      <p className="font-medium text-gray-900">{s.employee_name}</p>
                      <p className="text-xs text-gray-400">{s.employee_role}</p>
                    </td>
                    <td className="px-4 py-3 text-gray-600">{s.month}</td>
                    <td className="px-4 py-3 text-right font-medium text-gray-900">${s.gross_salary?.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td className="px-4 py-3 text-right text-red-600">${s.federal_tax?.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td className="px-4 py-3 text-right text-red-600">${s.state_tax?.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td className="px-4 py-3 text-right text-red-600">${s.social_security?.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td className="px-4 py-3 text-right text-red-600">${s.medicare?.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td className="px-4 py-3 text-right text-orange-600">${s.retirement_401k?.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td className="px-4 py-3 text-right text-orange-600">${s.health_insurance?.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td className="px-4 py-3 text-right font-bold text-emerald-700">${s.net_salary?.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td className="px-4 py-3">
                      <span className={`badge border ${s.payment_status === 'paid' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-amber-50 text-amber-700 border-amber-200'}`}>
                        {s.payment_status?.toUpperCase()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
