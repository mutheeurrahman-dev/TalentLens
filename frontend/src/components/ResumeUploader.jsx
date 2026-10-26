import React, { useState, useRef } from 'react';
import { getPresignedUrl, uploadToS3, reportUploadFailure } from '../api/api.js';
import ResumeHistory from './ResumeHistory.jsx';

const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024; // 10MB

/**
 * ResumeUploader Component
 * Dedicated section for PDF resume uploads, drag-and-drop, upload progress,
 * live processing status, and resume ingestion history.
 */
export default function ResumeUploader({
  onUploadComplete,
  candidates = [],
  onSelectCandidate,
}) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [progressPercent, setProgressPercent] = useState(0);
  const [errorMessage, setErrorMessage] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const validateFile = (file) => {
    if (!file) return false;

    if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') {
      setErrorMessage('Invalid file format. Only PDF files are supported.');
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      return false;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      setErrorMessage('File size exceeds the 10MB limit.');
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      return false;
    }

    return true;
  };

  const handleFileChange = (e) => {
    setErrorMessage(null);
    setSuccessMessage(null);
    const file = e.target.files?.[0];
    if (file && validateFile(file)) {
      setSelectedFile(file);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!uploading) setIsDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (uploading) return;

    setErrorMessage(null);
    setSuccessMessage(null);
    const file = e.dataTransfer.files?.[0];
    if (file && validateFile(file)) {
      setSelectedFile(file);
    }
  };

  const handleUpload = async (e) => {
    if (e) e.preventDefault();
    if (!selectedFile || uploading) return;

    setUploading(true);
    setErrorMessage(null);
    setSuccessMessage(null);
    setProgressPercent(15);
    setUploadProgress('Requesting secure upload authorization...');
    let candidateId = null;

    try {
      // 1. Request presigned URL from backend
      const presignedData = await getPresignedUrl(selectedFile.name);
      candidateId = presignedData?.candidateId;
      const uploadUrl = presignedData?.uploadUrl;

      if (!uploadUrl) {
        throw new Error('Server did not return a valid upload URL.');
      }

      // 2. Direct PUT upload to S3
      setProgressPercent(50);
      setUploadProgress('Uploading resume directly to AWS S3...');
      await uploadToS3(uploadUrl, selectedFile);

      // 3. Complete
      setProgressPercent(100);
      setUploadProgress('Upload complete! Enqueueing processing...');
      setSuccessMessage(`Successfully uploaded ${selectedFile.name}`);

      if (onUploadComplete) {
        onUploadComplete(candidateId, selectedFile.name);
      }

      // Reset file input
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      setTimeout(() => {
        setUploadProgress(null);
        setProgressPercent(0);
      }, 3500);
    } catch (err) {
      console.error('Upload failed:', err);
      if (candidateId) {
        try {
          await reportUploadFailure(candidateId, err.message || 'Upload failed.');
        } catch (_) {
          // ignore report failure
        }
      }
      setErrorMessage(err.message || 'Failed to upload resume. Please try again.');
      setUploadProgress(null);
      setProgressPercent(0);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card upload-section">
      <div className="section-header-wrap">
        <span className="section-badge">AWS S3</span>
        <h2 className="section-title">Upload Resume</h2>
        <p className="section-subtitle">Drop candidate PDF to trigger automated parsing.</p>
      </div>

      {/* Drag & Drop Target Area */}
      <div
        className={`dropzone-container ${isDragActive ? 'drag-active' : ''} ${selectedFile ? 'has-file' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !uploading && fileInputRef.current?.click()}
      >
        <input
          id="resume-file"
          type="file"
          ref={fileInputRef}
          accept=".pdf,application/pdf"
          onChange={handleFileChange}
          disabled={uploading}
          className="file-input-hidden"
        />

        <div className="dropzone-content">
          <div className="dropzone-icon-circle">
            <span className="dropzone-icon">📄</span>
          </div>
          {selectedFile ? (
            <div className="file-selected-box">
              <span className="file-selected-name">{selectedFile.name}</span>
              <span className="file-selected-size">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • PDF Document
              </span>
              <span className="file-change-hint">Click or drop to replace</span>
            </div>
          ) : (
            <div className="dropzone-prompt">
              <span className="dropzone-primary-text">
                <strong>Click to browse</strong> or drag & drop PDF here
              </span>
              <span className="dropzone-sub-text">Standard PDF resumes up to 10MB</span>
            </div>
          )}
        </div>
      </div>

      {/* Upload Progress Bar */}
      {uploading && (
        <div className="upload-progress-wrapper">
          <div className="upload-progress-info">
            <span className="upload-progress-label">{uploadProgress}</span>
            <span className="upload-progress-percent">{progressPercent}%</span>
          </div>
          <div className="progress-track">
            <div
              className="progress-fill"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
      )}

      {/* Success Notification */}
      {successMessage && !uploading && (
        <div className="alert-banner alert-success">
          <span>✓ {successMessage}</span>
          <button
            type="button"
            className="alert-dismiss"
            onClick={() => setSuccessMessage(null)}
          >
            ✕
          </button>
        </div>
      )}

      {/* Error Notification */}
      {errorMessage && (
        <div className="alert-banner alert-error">
          <span>⚠️ {errorMessage}</span>
          <button
            type="button"
            className="alert-dismiss"
            onClick={() => setErrorMessage(null)}
          >
            ✕
          </button>
        </div>
      )}

      {/* Upload Action Button */}
      <button
        type="button"
        className="btn btn-primary btn-block upload-action-btn"
        onClick={handleUpload}
        disabled={!selectedFile || uploading}
      >
        {uploading ? (
          <span className="btn-loading-content">
            <span className="loading-spinner small"></span>
            <span>Uploading...</span>
          </span>
        ) : (
          'Upload & Screen Resume'
        )}
      </button>

      {/* Resume History List */}
      {candidates && candidates.length > 0 && (
        <div className="uploader-history-section">
          <div className="history-header-row">
            <h3 className="history-section-title">Upload History ({candidates.length})</h3>
            <span className="history-sub-label">Recent documents</span>
          </div>
          <ResumeHistory
            candidates={candidates}
            onSelectCandidate={onSelectCandidate}
          />
        </div>
      )}
    </div>
  );
}
