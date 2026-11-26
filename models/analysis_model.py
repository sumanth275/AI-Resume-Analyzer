"""Backward-compatible re-exports for resume, job, and analysis models."""

from models.resume_model import ResumeModel, AnalysisModel
from models.job_model import JobModel

__all__ = ['ResumeModel', 'JobModel', 'AnalysisModel']
