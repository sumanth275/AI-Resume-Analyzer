"""Backward-compatible re-exports for job portal and application models."""

from models.job_model import JobListingModel
from models.application_model import JobApplicationModel

__all__ = ['JobListingModel', 'JobApplicationModel']
