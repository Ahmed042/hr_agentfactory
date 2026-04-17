import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { emailsAPI } from '../api/client';
import { Mail, Send, ArrowLeft, User, ChevronRight, Inbox as InboxIcon } from 'lucide-react';

export default function Inbox() {
  const [selectedThread, setSelectedThread] = useState(null);
  const [replyBody, setReplyBody] = useState('');
  const [replySubject, setReplySubject] = useState('');
  const queryClient = useQueryClient();

  const { data: threads = [], isLoading } = useQuery({
    queryKey: ['email-inbox'],
    queryFn: () => emailsAPI.getInbox().then(res => res.data),
  });

  const { data: threadData } = useQuery({
    queryKey: ['email-thread', selectedThread],
    queryFn: () => emailsAPI.getThread(selectedThread).then(res => res.data),
    enabled: !!selectedThread,
  });

  const replyMutation = useMutation({
    mutationFn: (data) => emailsAPI.reply(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['email-thread', selectedThread] });
      queryClient.invalidateQueries({ queryKey: ['email-inbox'] });
      setReplyBody('');
      setReplySubject('');
    },
  });

  const handleReply = (e) => {
    e.preventDefault();
    if (!replyBody.trim()) return;
    replyMutation.mutate({
      candidate_id: selectedThread,
      subject: replySubject || `RE: ${threadData?.emails?.[0]?.subject || 'Follow up'}`,
      body: replyBody,
    });
  };

  const formatDate = (d) => {
    if (!d) return '';
    return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  // Thread detail view
  if (selectedThread && threadData) {
    return (
      <div className="space-y-6">
        <button onClick={() => setSelectedThread(null)} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
          <ArrowLeft className="w-4 h-4" />Back to Inbox
        </button>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-navy-500 rounded-full flex items-center justify-center">
            <span className="text-white font-semibold">{(threadData.candidate?.name || '?')[0].toUpperCase()}</span>
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">{threadData.candidate?.name}</h2>
            <p className="text-sm text-gray-500">{threadData.candidate?.email} · {threadData.candidate?.job_role}</p>
          </div>
        </div>

        {/* Emails */}
        <div className="space-y-4">
          {threadData.emails?.map((email) => (
            <div key={email.id} className={`card p-5 ${email.direction === 'outbound' ? 'ml-8 border-l-4 border-l-navy-500' : 'mr-8 border-l-4 border-l-gray-300'}`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-gray-500">
                  {email.direction === 'outbound' ? 'You' : threadData.candidate?.name}
                </span>
                <span className="text-xs text-gray-400">{formatDate(email.sent_at)}</span>
              </div>
              {email.subject && <p className="text-sm font-medium text-gray-800 mb-1">{email.subject}</p>}
              <p className="text-sm text-gray-600 whitespace-pre-line">{email.body}</p>
              {email.ai_action && (
                <span className="inline-block mt-2 px-2 py-0.5 bg-purple-50 text-purple-700 rounded text-[10px] font-semibold">
                  AI: {email.ai_action}
                </span>
              )}
            </div>
          ))}
        </div>

        {/* Reply Form */}
        <div className="card p-5">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Reply</h4>
          <form onSubmit={handleReply} className="space-y-3">
            <input
              type="text"
              placeholder="Subject"
              value={replySubject}
              onChange={(e) => setReplySubject(e.target.value)}
              className="input text-sm"
            />
            <textarea
              rows={4}
              placeholder="Type your reply..."
              value={replyBody}
              onChange={(e) => setReplyBody(e.target.value)}
              className="input text-sm"
            />
            <button type="submit" disabled={replyMutation.isPending || !replyBody.trim()} className="btn-primary flex items-center gap-2 disabled:opacity-50">
              <Send className="w-4 h-4" />
              {replyMutation.isPending ? 'Sending...' : 'Send Reply'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Inbox list view
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Email Inbox</h1>
        <p className="text-sm text-gray-500 mt-1">{threads.length} conversations</p>
      </div>

      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-gray-400">Loading inbox...</div>
        ) : threads.length === 0 ? (
          <div className="p-12 text-center">
            <InboxIcon className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">Inbox empty</p>
            <p className="text-sm text-gray-400 mt-1">Emails will appear here when candidates are added</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {threads.map((thread) => (
              <button
                key={thread.candidate_id}
                onClick={() => setSelectedThread(thread.candidate_id)}
                className="w-full text-left px-6 py-4 hover:bg-gray-50 transition-colors flex items-center gap-4"
              >
                <div className="w-10 h-10 bg-navy-500 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-white text-sm font-semibold">
                    {(thread.candidate_name || '?')[0].toUpperCase()}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-0.5">
                    <span className="text-sm font-semibold text-gray-900">{thread.candidate_name}</span>
                    <span className="text-xs text-gray-400">{formatDate(thread.last_email)}</span>
                  </div>
                  <p className="text-xs text-gray-500 mb-0.5">{thread.job_role}</p>
                  <p className="text-sm text-gray-500 truncate">{thread.latest_subject}</p>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <span className="badge bg-gray-100 text-gray-600">{thread.email_count}</span>
                  <ChevronRight className="w-4 h-4 text-gray-300" />
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
