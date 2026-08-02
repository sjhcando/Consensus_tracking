"""Canonical Google Drive storage locations for Consensus Tracking outputs."""

from pathlib import Path


DRIVE_ROOT = Path(r"G:\내 드라이브")
SECTOR_ANALYSIS_DIR = DRIVE_ROOT / "2. Sector_Analysis"
MARKET_MONITORING_DIR = DRIVE_ROOT / "4. Market_Monitoring"
CONSENSUS_DATA_DIR = MARKET_MONITORING_DIR / "Consensus"
CONSENSUS_DIFF_DIR = CONSENSUS_DATA_DIR
MARKET_DATA_DIR = MARKET_MONITORING_DIR / "Market Price"
REFERENCE_DATA_DIR = MARKET_MONITORING_DIR / "Reference"
RESEARCH_DIR = SECTOR_ANALYSIS_DIR


def sector_dir(sector):
    return RESEARCH_DIR / sector


def sector_reports_dir(sector):
    return sector_dir(sector) / "리포트"


def sector_consensus_dir(sector):
    return sector_dir(sector)


def sector_updates_dir(sector):
    return sector_dir(sector)
