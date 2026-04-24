function UploadForm({ rawText, setRawText, selectedFile, setSelectedFile, handleUpload, submitting }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-lg shadow-slate-300/20 dark:border-slate-800 dark:bg-slate-900/80 dark:shadow-slate-950/30">
      <div className="mb-5">
        <h2 className="text-2xl font-bold text-slate-950 dark:text-white">Submit Community Report</h2>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
          Submit text, PDFs, or field images. The backend will turn the report into a clear issue
          summary, urgency level, people count, and volunteer-ready task.
        </p>
      </div>
      <form className="grid gap-4" onSubmit={handleUpload}>
        <label className="grid gap-2">
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Community report text</span>
          <textarea
            className="min-h-48 rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-cyan-400 dark:border-slate-700 dark:bg-slate-950/70 dark:text-white"
            value={rawText}
            onChange={(event) => setRawText(event.target.value)}
            placeholder="Critical food shortage in Village A affecting 150 people..."
          />
        </label>
        <label className="grid gap-2">
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Upload PDF or image</span>
          <input
            className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-700 dark:border-slate-600 dark:bg-slate-950/70 dark:text-slate-300"
            type="file"
            accept=".pdf,.png,.jpg,.jpeg,.bmp,.tiff,.txt"
            onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
          />
        </label>
        {selectedFile ? <p className="text-sm text-cyan-600 dark:text-cyan-300">Selected: {selectedFile.name}</p> : null}
        <button
          className="rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-wait disabled:opacity-60"
          type="submit"
          disabled={submitting}
        >
          {submitting ? "Processing report..." : "Create case from report"}
        </button>
      </form>
    </div>
  );
}

export default UploadForm;
