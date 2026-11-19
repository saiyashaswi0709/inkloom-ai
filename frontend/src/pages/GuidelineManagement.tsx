import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { Scroll, Upload, Plus, FileText, ChevronRight, Trash2, CheckCircle2 } from 'lucide-react';

export const GuidelineManagement: React.FC = () => {
  const [guidelines, setGuidelines] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedGuideline, setSelectedGuideline] = useState<any | null>(null);

  // Upload modal state
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadCategory, setUploadCategory] = useState('Voice & Tone');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchGuidelines = async () => {
    try {
      const res = await api.get('/guidelines');
      setGuidelines(res.data);
      if (res.data.length > 0 && !selectedGuideline) {
        setSelectedGuideline(res.data[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGuidelines();
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', uploadTitle);
    formData.append('category', uploadCategory);

    try {
      const res = await api.post('/guidelines/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setShowUploadModal(false);
      setFile(null);
      setUploadTitle('');
      fetchGuidelines();
      setSelectedGuideline(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to remove this guideline?')) return;
    try {
      await api.delete(`/guidelines/${id}`);
      fetchGuidelines();
      if (selectedGuideline?.id === id) {
        setSelectedGuideline(null);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Brand Guidelines</h1>
          <p className="text-sm text-slate-500 mt-1">
            Official style guides, messaging rules, and tone standards.
          </p>
        </div>
        <button
          onClick={() => setShowUploadModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium shadow-sm transition-colors"
        >
          <Upload className="w-4 h-4" />
          <span>Upload Guideline Document</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Guideline List */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-xs divide-y divide-slate-100">
          <div className="p-4 bg-slate-50/50 rounded-t-xl font-semibold text-xs text-slate-500 uppercase tracking-wider">
            Guidelines ({guidelines.length})
          </div>

          {loading ? (
            <div className="p-6 text-center text-slate-400 text-sm">Loading guidelines...</div>
          ) : guidelines.length === 0 ? (
            <div className="p-6 text-center text-slate-500 text-sm">No guidelines found.</div>
          ) : (
            guidelines.map((g) => (
              <div
                key={g.id}
                onClick={() => setSelectedGuideline(g)}
                className={`p-4 cursor-pointer transition-colors flex items-center justify-between ${
                  selectedGuideline?.id === g.id ? 'bg-indigo-50/60 border-l-4 border-indigo-600' : 'hover:bg-slate-50'
                }`}
              >
                <div className="space-y-1">
                  <h4 className="font-semibold text-sm text-slate-900">{g.title}</h4>
                  <div className="flex items-center space-x-2 text-xs text-slate-500">
                    <span className="px-2 py-0.5 rounded bg-slate-100 font-medium">{g.category}</span>
                    <span>• {g.chunks?.length || 0} sections</span>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400" />
              </div>
            ))
          )}
        </div>

        {/* Selected Guideline Detail & Chunks */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-6">
          {selectedGuideline ? (
            <>
              <div className="flex items-start justify-between border-b border-slate-100 pb-4">
                <div>
                  <div className="flex items-center space-x-2">
                    <h2 className="text-xl font-bold text-slate-900">{selectedGuideline.title}</h2>
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700">
                      {selectedGuideline.category}
                    </span>
                  </div>
                  {selectedGuideline.source_document_name && (
                    <p className="text-xs text-slate-400 mt-1 flex items-center space-x-1">
                      <FileText className="w-3.5 h-3.5" />
                      <span>Source: {selectedGuideline.source_document_name}</span>
                    </p>
                  )}
                </div>
                <button
                  onClick={() => handleDelete(selectedGuideline.id)}
                  className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                  title="Delete guideline"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              {selectedGuideline.description && (
                <p className="text-sm text-slate-600">{selectedGuideline.description}</p>
              )}

              {/* Chunks */}
              <div className="space-y-4">
                <h3 className="font-semibold text-slate-900 text-sm">Extracted Guideline Sections</h3>
                <div className="space-y-3">
                  {selectedGuideline.chunks && selectedGuideline.chunks.length > 0 ? (
                    selectedGuideline.chunks.map((chunk: any) => (
                      <div
                        key={chunk.id}
                        className="p-4 rounded-lg bg-slate-50 border border-slate-200/80 space-y-2"
                      >
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-bold text-indigo-900">{chunk.section_name}</span>
                          {chunk.page_number && (
                            <span className="text-slate-400">Page {chunk.page_number}</span>
                          )}
                        </div>
                        <p className="text-xs text-slate-700 leading-relaxed whitespace-pre-line">
                          {chunk.content}
                        </p>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-slate-400">No sections found in this guideline.</p>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-400 text-sm">
              Select a guideline to view its content and sections.
            </div>
          )}
        </div>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 max-w-md w-full p-6 shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Upload Guideline Document</h3>
            <p className="text-xs text-slate-500">
              Upload PDF or DOCX brand books. Our engine will automatically parse, chunk, and index sections.
            </p>

            {error && (
              <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700">
                {error}
              </div>
            )}

            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-700">Document Title</label>
                <input
                  type="text"
                  required
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  placeholder="e.g. Tone and Voice Standard 2026"
                  className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700">Category</label>
                <select
                  value={uploadCategory}
                  onChange={(e) => setUploadCategory(e.target.value)}
                  className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
                >
                  <option value="Voice & Tone">Voice & Tone</option>
                  <option value="Security & Compliance">Security & Compliance</option>
                  <option value="Product Messaging">Product Messaging</option>
                  <option value="Legal & Disclosures">Legal & Disclosures</option>
                  <option value="Visual & Formatting">Visual & Formatting</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700">File (.pdf, .docx, .txt)</label>
                <input
                  type="file"
                  required
                  accept=".pdf,.docx,.doc,.txt,.md"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="mt-1 w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold"
                >
                  {uploading ? 'Processing & Indexing...' : 'Upload & Extract'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
